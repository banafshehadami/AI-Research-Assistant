from flask import Flask, render_template, request, jsonify
import requests
import pdfplumber
from transformers import pipeline
import arxiv
import google.generativeai as genai
import threading
from time import sleep

app = Flask(__name__)

# Configure Google Generative AI
GOOGLE_API_KEY = "AIzaSyBHT8QBWTZck5iJLYUEdHP-XwX2GNVnH1o" #TODO use you own GOOGLE API KEY
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Load summarization model
summarizer = pipeline("summarization")

# Shared list for storing updates (thread-safe)
updates = []

# Function to log updates
def log_update(message):
    updates.append(message)

# Function to search papers on arXiv
def search_papers_arxiv(keyword, num_results=5):
    search = arxiv.Search(
        query=keyword,
        max_results=num_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers = []
    for result in search.results():
        papers.append({
            "title": result.title,
            "authors": [author.name for author in result.authors] if result.authors else [],
            "year": result.published.year,
            "abstract": result.summary,
            "url": result.entry_id,
            "pdf_url": result.pdf_url,
            "summary": None  # Placeholder for the summary
        })
    return papers

# Function to download PDF
def download_pdf(pdf_url, save_path):
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path
    except Exception as e:
        return None

# Function to extract text from the downloaded PDF
def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return "".join(page.extract_text() for page in pdf.pages)
    except Exception:
        return None

# Background thread to process papers
def process_papers(keyword, num_results):
    global updates
    updates.clear()
    log_update({"message": f"Searching for {num_results} papers with keyword: {keyword}", "type": "info"})
    papers = search_papers_arxiv(keyword, num_results)
    for idx, paper in enumerate(papers, 1):
        log_update({"message": f"Processing Paper {idx}: {paper['title']}", "type": "info"})
        authors = ', '.join(paper['authors']) if paper['authors'] else "No authors listed"
        log_update({"message": f"Authors: {authors}", "type": "info"})
        log_update({"message": f"Abstract: {paper['abstract']}", "type": "info"})

        pdf_path = download_pdf(paper["pdf_url"], f"{paper['title'].replace(' ', '_')}.pdf")
        if pdf_path:
            text = extract_text_from_pdf(pdf_path)
            if text:
                summary = model.generate_content(f"Summarize the following text: {text}")
                paper["summary"] = summary.text
                log_update({"message": f"Summary for Paper {idx}: {summary.text}", "type": "success"})
            else:
                log_update({"message": f"Failed to extract text for Paper {idx}", "type": "error"})
        else:
            log_update({"message": f"Failed to download PDF for Paper {idx}", "type": "error"})

    log_update({"message": "Processing completed.", "type": "info"})

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        num_papers = int(request.form.get("num_papers"))
        thread = threading.Thread(target=process_papers, args=(keyword, num_papers))
        thread.start()
        return render_template("updates.html", keyword=keyword)
    return render_template("index.html")

@app.route("/get_updates", methods=["GET"])
def get_updates():
    return jsonify(updates)

if __name__ == "__main__":
    app.run(debug=True)
