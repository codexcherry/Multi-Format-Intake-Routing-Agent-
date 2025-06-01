from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from agents.classifier import ClassifierAgent
from agents.json_agent import JSONAgent
from agents.email_agent import EmailAgent
from agents.pdf_agent import PDFAgent
from memory.shared_memory import SharedMemory
from utils.llm_client import GeminiClient
import json
from fastapi.staticfiles import StaticFiles
import traceback

app = FastAPI(
    title="Multi-Format Intake Agent with Gemini AI",
    description="Accept data in PDF, JSON, or Email format, intelligently classify it using Gemini AI, and route to the appropriate agent.",
    version="1.1.0"
)
shared_memory = SharedMemory()
gemini_client = GeminiClient()  # Initialize the Gemini client
classifier = ClassifierAgent(shared_memory, gemini_client)
json_agent = JSONAgent(shared_memory, gemini_client)
email_agent = EmailAgent(shared_memory, gemini_client)
pdf_agent = PDFAgent(shared_memory, gemini_client)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/intake")
async def intake(request: Request, file: UploadFile = File(None), json_data: str = Form(None), email_text: str = Form(None)):
    try:
        print(f"Received request: file={file is not None}, json_data={json_data is not None}, email_text={email_text is not None}")
        
        if file and file.filename:
            content = await file.read()
            input_type = "file"
            input_data = content
            print(f"Processing file: {file.filename}, size: {len(content)} bytes")
        elif json_data and json_data.strip():
            try:
                input_data = json.loads(json_data)
                input_type = "json"
                print(f"Processing JSON data: {json_data[:100]}...")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON data: {e}")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid JSON data", "detail": str(e)}
                )
        elif email_text and email_text.strip():
            input_data = email_text
            input_type = "email"
            print(f"Processing email text: {email_text[:100]}...")
        else:
            print("No input provided")
            return JSONResponse(
                status_code=400,
                content={"error": "No input provided", "detail": "Please provide either a file, JSON data, or email text"}
            )

        # Classify input and route to the appropriate agent
        format_type, intent = await classifier.classify(input_data, input_type)
        print(f"Classified as format: {format_type}, intent: {intent}")
        
        # Log input and get the input_id
        input_id = shared_memory.log_input("api", input_type, format_type, intent)
        print(f"Logged input with ID: {input_id}")
        
        if format_type == "json":
            result = await json_agent.process(input_data, input_id)
        elif format_type == "email":
            result = await email_agent.process(input_data, input_id)
        elif format_type == "pdf":
            result = await pdf_agent.process(input_data, input_id)
        else:
            print(f"Unsupported format: {format_type}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Unsupported format: {format_type}"}
            )

        # Add input metadata to the response
        result["input_metadata"] = {
            "id": input_id,
            "format": format_type,
            "intent": intent,
            "timestamp": shared_memory.get_input_timestamp(input_id)
        }
        
        print(f"Returning result: {str(result)[:100]}...")
        return JSONResponse(content=result)
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multi-Format Intake Routing Agent</title>
        <style>
            :root {
                --primary-color: #8A2BE2;
                --secondary-color: #9370DB;
                --accent-color: #00BFFF;
                --dark-bg: #121212;
                --dark-card: #1E1E1E;
                --dark-content: #262626;
                --dark-border: #333333;
                --dark-text: #FFFFFF;
                --light-text: #F0F0F0;
                --border-radius: 10px;
                --card-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
                --transition-speed: 0.3s;
                --glow-color: rgba(138, 43, 226, 0.6);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: var(--dark-bg);
                color: var(--dark-text);
                line-height: 1.6;
                transition: all var(--transition-speed) ease;
                position: relative;
                overflow-x: hidden;
            }
            
            body::before {
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 20%, rgba(138, 43, 226, 0.15) 0%, transparent 30%),
                    radial-gradient(circle at 80% 80%, rgba(0, 191, 255, 0.1) 0%, transparent 30%);
                animation: gradientMove 20s ease infinite alternate;
                z-index: -1;
            }
            
            @keyframes gradientMove {
                0% { background-position: 0% 0%; }
                100% { background-position: 100% 100%; }
            }
            
            .container {
                max-width: 1100px;
                margin: 0 auto;
                padding: 2.5rem;
            }
            
            header {
                text-align: center;
                margin-bottom: 3.5rem;
                border-bottom: 1px solid var(--dark-border);
                padding-bottom: 2rem;
                animation: fadeIn 1s ease-in-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateX(-20px); }
                to { opacity: 1; transform: translateX(0); }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            @keyframes glow {
                0% { box-shadow: 0 0 5px var(--glow-color); }
                50% { box-shadow: 0 0 20px var(--glow-color); }
                100% { box-shadow: 0 0 5px var(--glow-color); }
            }
            
            h1 {
                color: var(--primary-color);
                margin: 0.8rem 0;
                font-size: 2.2rem;
                letter-spacing: 1px;
                text-shadow: 0 0 10px rgba(138, 43, 226, 0.4);
            }
            
            .subtitle {
                color: var(--secondary-color);
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 1rem;
            }
            
            .card {
                background-color: var(--dark-card);
                border-radius: var(--border-radius);
                box-shadow: var(--card-shadow);
                padding: 2.5rem;
                margin-bottom: 2.5rem;
                transition: all var(--transition-speed) ease;
                animation: slideIn 0.5s ease-out;
                border: 1px solid var(--dark-border);
                position: relative;
                overflow: hidden;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), 0 0 15px var(--glow-color);
            }
            
            .card::before {
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                border-radius: var(--border-radius);
                background: linear-gradient(45deg, var(--primary-color), var(--accent-color), var(--primary-color));
                z-index: -1;
                opacity: 0;
                transition: opacity 0.3s ease;
                box-shadow: 0 0 20px var(--glow-color);
            }
            
            .card:hover::before {
                opacity: 1;
                animation: gradientBorder 3s linear infinite;
            }
            
            @keyframes gradientBorder {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            .section-heading {
                color: var(--accent-color);
                margin-top: 1.8rem;
                margin-bottom: 1rem;
                font-size: 1.5rem;
                letter-spacing: 0.5px;
                text-shadow: 0 0 5px rgba(0, 191, 255, 0.3);
            }
            
            .feature-list {
                list-style: none;
                margin: 1.5rem 0;
            }
            
            .feature-item {
                padding: 0.8rem 0;
                border-bottom: 1px solid var(--dark-border);
                display: flex;
                align-items: flex-start;
                animation: slideIn 0.5s ease-out;
            }
            
            .feature-item:last-child {
                border-bottom: none;
            }
            
            .feature-icon {
                color: var(--accent-color);
                margin-right: 1rem;
                font-size: 1.2rem;
            }
            
            .feature-text h3 {
                color: var(--light-text);
                margin-bottom: 0.5rem;
                font-size: 1.1rem;
            }
            
            .feature-text p {
                color: var(--light-text);
                opacity: 0.8;
                font-size: 0.95rem;
            }
            
            .cta-button {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border: none;
                padding: 0.9rem 2rem;
                border-radius: var(--border-radius);
                cursor: pointer;
                font-size: 1.1rem;
                font-weight: 600;
                transition: all var(--transition-speed) ease;
                position: relative;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3);
                letter-spacing: 0.5px;
                text-transform: uppercase;
                display: inline-block;
                margin: 1rem 0;
                text-decoration: none;
            }
            
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(138, 43, 226, 0.4), 0 0 15px var(--glow-color);
            }
            
            .logo {
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1.5rem;
            }
            
            .logo-icon {
                position: relative;
                width: 50px;
                height: 50px;
                margin-right: 15px;
            }
            
            .logo-circle {
                position: absolute;
                width: 36px;
                height: 36px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border-radius: 50%;
                top: 0;
                left: 0;
                animation: pulse 3s infinite;
                box-shadow: 0 0 15px var(--glow-color);
            }
            
            .logo-square {
                position: absolute;
                width: 24px;
                height: 24px;
                background: linear-gradient(135deg, var(--accent-color), #2dd4bf);
                border-radius: 4px;
                bottom: 0;
                right: 0;
                animation: rotate 6s linear infinite;
                transform-origin: center;
                box-shadow: 0 0 15px rgba(0, 191, 255, 0.5);
            }
            
            @keyframes rotate {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .logo-text {
                font-size: 2.4rem;
                font-weight: 700;
                color: var(--light-text);
                letter-spacing: 3px;
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 15px var(--glow-color);
            }
            
            .api-section {
                background-color: var(--dark-content);
                border-radius: var(--border-radius);
                padding: 1.5rem;
                margin: 1.5rem 0;
                border-left: 4px solid var(--accent-color);
            }
            
            code {
                background-color: rgba(0, 0, 0, 0.3);
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                color: var(--accent-color);
                font-size: 0.9rem;
            }
            
            footer {
                text-align: center;
                margin-top: 5rem;
                padding: 2rem 0;
                border-top: 1px solid var(--dark-border);
                color: var(--secondary-color);
                opacity: 0.9;
                animation: fadeIn 1s ease-in-out;
                background: linear-gradient(to right, transparent, rgba(138, 43, 226, 0.1), transparent);
            }
            
            footer p {
                margin: 0.8rem 0;
                font-size: 0.95rem;
                letter-spacing: 0.5px;
            }
            
            .ai-badge {
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                color: white;
                font-size: 0.9rem;
                padding: 0.4rem 1rem;
                border-radius: 2rem;
                display: inline-block;
                margin-top: 1rem;
                box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3), 0 0 10px var(--glow-color);
                animation: pulse 2s infinite;
                letter-spacing: 0.8px;
                font-weight: 500;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo">
                    <div class="logo-icon">
                        <span class="logo-circle"></span>
                        <span class="logo-square"></span>
                    </div>
                    <div class="logo-text">MIRA</div>
                </div>
                <h1>Multi-Format Intake Routing Agent</h1>
                <p class="subtitle">Intelligent classification and routing for PDF, JSON, and Email data</p>
                <div class="ai-badge">Powered by Gemini AI</div>
            </header>
            
            <main>
                <div class="card">
                    <h2>Welcome to MIRA</h2>
                    <p>MIRA is an advanced document processing system that intelligently analyzes and extracts information from multiple data formats. Using the power of Gemini AI, it can understand the content and context of your documents, providing valuable insights and structured data.</p>
                    
                    <div class="section-heading">Key Features</div>
                    <ul class="feature-list">
                        <li class="feature-item">
                            <div class="feature-icon">✨</div>
                            <div class="feature-text">
                                <h3>Multi-Format Processing</h3>
                                <p>Seamlessly handle PDF documents, JSON data, and Email content through a unified interface.</p>
                            </div>
                        </li>
                        <li class="feature-item">
                            <div class="feature-icon">🧠</div>
                            <div class="feature-text">
                                <h3>AI-Powered Analysis</h3>
                                <p>Leverage Gemini AI to extract meaning, identify key information, and generate human-readable insights.</p>
                            </div>
                        </li>
                        <li class="feature-item">
                            <div class="feature-icon">🔍</div>
                            <div class="feature-text">
                                <h3>Intelligent Classification</h3>
                                <p>Automatically detect document types and route to specialized processing agents.</p>
                            </div>
                        </li>
                        <li class="feature-item">
                            <div class="feature-icon">📊</div>
                            <div class="feature-text">
                                <h3>Human-Readable Results</h3>
                                <p>Transform complex data into clear, structured information that's easy to understand.</p>
                            </div>
                        </li>
                    </ul>
                    
                    <a href="/static/index.html" class="cta-button">Launch Web Interface</a>
                </div>
                
                <div class="card">
                    <div class="section-heading">API Integration</div>
                    <p>MIRA provides a simple REST API for programmatic access to its document processing capabilities.</p>
                    
                    <div class="api-section">
                        <h3>Endpoint</h3>
                        <p><code>POST /intake</code></p>
                        
                        <h3>Parameters</h3>
                        <p><code>file</code> - Upload PDF, JSON, or Email files</p>
                        <p><code>json_data</code> - String containing JSON data</p>
                        <p><code>email_text</code> - String containing email content</p>
                        
                        <h3>Response</h3>
                        <p>Returns structured data with analysis results and metadata.</p>
                    </div>
                </div>
            </main>
            
            <footer>
                <p>Multi-Format Intake Routing Agent with Intelligent Classification</p>
                <div class="footer-links">
                    <a href="https://github.com/codexcherry" class="footer-link" target="_blank">GitHub</a>
                </div>
                <p class="copyright">© 2025 MIRA System</p>
            </footer>
        </div>
    </body>
    </html>
    """ 
