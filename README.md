# MIRA: Multi-Format Intake Routing Agent

<div align="center">
  
  ![MIRA Logo](https://img.shields.io/badge/MIRA-Multi--Format%20Intake%20Routing%20Agent-8A2BE2?style=for-the-badge&logo=robot&logoColor=white)
  
  [![GitHub](https://img.shields.io/badge/GitHub-codexcherry-00BFFF?style=flat-square&logo=github)](https://github.com/codexcherry)
  ![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python&logoColor=white)
  ![FastAPI](https://img.shields.io/badge/FastAPI-modern-009688?style=flat-square&logo=fastapi&logoColor=white)
  ![Gemini AI](https://img.shields.io/badge/Gemini_AI-Powered-8E44AD?style=flat-square&logo=google&logoColor=white)
  
</div>

## 🌟 Overview

MIRA is an advanced document processing system that intelligently analyzes and extracts information from multiple data formats. Using the power of Gemini AI, it understands the content and context of your documents, providing valuable insights and structured data.

<div align="center">
  <img src="https://via.placeholder.com/800x400.png?text=MIRA+System+Architecture" alt="MIRA Architecture" width="700px"/>
</div>

## ✨ Key Features

- **Multi-Format Processing** - Seamlessly handle PDF documents, JSON data, and Email content through a unified interface
- **AI-Powered Analysis** - Leverage Gemini AI to extract meaning, identify key information, and generate human-readable insights
- **Intelligent Classification** - Automatically detect document types and route to specialized processing agents
- **Human-Readable Results** - Transform complex data into clear, structured information that's easy to understand
- **Context Memory** - Maintain processing history and relationships between documents for audit and reference
- **Beautiful UI** - Dark-themed, modern interface with animations and responsive design

## 🧩 System Architecture

MIRA consists of four specialized agents working together:

### 1. Classifier Agent
- Receives raw input (file/email/JSON body)
- Classifies format (PDF/JSON/Email) and intent (Invoice, RFQ, Complaint, etc.)
- Routes to the appropriate extraction agent
- Adds format + intent to shared memory

### 2. JSON Agent
- Accepts arbitrary JSON (e.g., webhook payloads, APIs)
- Extracts and re-formats data to a defined FlowBit schema
- Identifies anomalies or missing fields
- Provides comprehensive analysis with insights and key data points

### 3. Email Parser Agent
- Accepts email body text (plain or HTML)
- Extracts sender name, request intent, urgency
- Returns formatted CRM-style record
- Stores conversation ID + parsed metadata in memory

### 4. PDF Agent
- Extracts text content from PDF documents
- Analyzes document structure and purpose
- Identifies key topics and provides recommendations
- Maintains document metadata and relationships

### Shared Memory Module
- Stores input metadata (source, type, timestamp)
- Tracks extracted fields per agent
- Maintains thread/conversation IDs
- Provides cross-agent access to processed data

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Multi-Format-Intake-Routing-Agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```bash
   python -m main
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## 💻 Usage Examples

### Web Interface

The easiest way to use MIRA is through its web interface. Simply:

1. Navigate to the application URL
2. Select the input type (File Upload, JSON Data, or Email Text)
3. Provide your data
4. Click "Process Input"
5. View the structured, human-readable results

### API Integration

MIRA provides a simple REST API for programmatic access:

```python
import requests

# Process a PDF file
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:8000/intake', files=files)
result = response.json()

# Process JSON data
json_data = {'key': 'value', 'nested': {'data': 'structure'}}
response = requests.post(
    'http://localhost:8000/intake', 
    data={'json_data': json.dumps(json_data)}
)
result = response.json()

# Process email text
email_text = """
From: sender@example.com
Subject: Request for Quote
Body: This is an urgent request for quote on your services.
"""
response = requests.post(
    'http://localhost:8000/intake', 
    data={'email_text': email_text}
)
result = response.json()
```

## 🔧 Technology Stack

- **Backend**: Python with FastAPI
- **AI Engine**: Google Gemini AI
- **Data Processing**: PyPDF2, JSON, Email Parser
- **Frontend**: HTML, CSS, JavaScript
- **Memory**: Shared Memory Module
- **Styling**: Custom Dark Theme UI

## 📊 Sample Output

<details>
<summary>JSON Analysis Example</summary>

```json
{
  "data": { "order_id": "12345", "customer": "Acme Corp", "items": [...] },
  "ai_analysis": {
    "summary": "This is a purchase order from Acme Corp with 3 line items",
    "structure_description": "Hierarchical JSON with order metadata and line items",
    "key_data_points": ["Total order value: $1,245.00", "3 unique products"],
    "likely_purpose": "Order processing system integration",
    "insights": ["High-value customer based on order history", "Contains expedited shipping request"]
  }
}
```
</details>

<details>
<summary>PDF Analysis Example </summary>

```json
{
  "document_type": "invoice",
  "title": "Invoice #INV-2023-04-15",
  "ai_analysis": {
    "likely_document_type": "Invoice",
    "content_summary": "This invoice from ABC Suppliers details a purchase of office equipment",
    "topics": ["Office Supplies", "Procurement", "Accounts Payable"],
    "recommended_next_steps": ["Forward to accounting department", "Match with purchase order #PO-2023-04-01"]
  }
}
```
</details>

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
  <p>Developed with ❤️ by <a href="https://github.com/codexcherry">@codexcherry</a></p>
</div>
