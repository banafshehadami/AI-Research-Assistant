# AI Research Assistant

An AI-powered web application that helps researchers search, download, process, and summarize research papers from arXiv using advanced AI models like Google GenAI.

---

## Features
- **Search Research Papers**: Use keywords to find relevant papers on arXiv.
- **PDF Download and Text Extraction**: Automatically download and extract content from research papers.
- **AI Summarization**: Generate concise summaries using Google GenAI.
- **Real-Time Updates**: Track the processing progress dynamically on the web interface.
- **User-Friendly Interface**: A responsive web application for seamless interaction.

---

## Requirements

### **Python Version**
- Python 3.8 or higher

### **Dependencies**
The application uses the following Python libraries:
- Flask
- pdfplumber
- transformers
- google-generativeai
- arxiv
- scholarly
- requests
- tqdm

Install all dependencies using:
```bash
pip install -r requirements.txt

## Usage
## 1. Run the Application
- python app.py

##2. Access the Web Application
Open your web browser and go to:
- http://127.0.0.1:5000/

## 3. Search and Summarize
Enter a keyword and the number of papers to process.
View real-time updates and summaries directly on the web interface.
