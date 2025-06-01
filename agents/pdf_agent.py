from memory.shared_memory import SharedMemory
from utils.llm_client import GeminiClient
import re
import io
import PyPDF2

class PDFAgent:
    def __init__(self, shared_memory: SharedMemory, llm_client: GeminiClient = None):
        self.shared_memory = shared_memory
        self.llm_client = llm_client

    async def process(self, pdf_data, input_id):
        """
        Process a PDF file and extract text content and metadata.
        If Gemini is available, it will be used for enhanced analysis.
        """
        # PDF metadata and content extraction
        pdf_text = ""
        extracted_text = ""
        pdf_version = "Unknown"
        title = "Untitled"
        page_count = 0
        
        try:
            # Create a PDF file reader object
            pdf_file = io.BytesIO(pdf_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Get page count
            page_count = len(pdf_reader.pages)
            
            # Extract text from the first few pages (limit to 5 pages to avoid memory issues)
            max_pages = min(5, page_count)
            extracted_text = ""
            for i in range(max_pages):
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    extracted_text += f"--- Page {i+1} ---\n{page_text}\n\n"
            
            # If we couldn't extract text or it's too short, indicate that
            if not extracted_text or len(extracted_text.strip()) < 50:
                extracted_text = "The PDF appears to contain mainly images or non-extractable content."
            
            # Truncate if it's too long (for display purposes)
            if len(extracted_text) > 5000:
                extracted_text = extracted_text[:5000] + "... (content truncated)"
            
            # Get PDF version from metadata if available
            try:
                if pdf_reader.pdf_header:
                    version_match = re.search(r'%PDF-(\d+\.\d+)', pdf_reader.pdf_header)
                    if version_match:
                        pdf_version = version_match.group(1)
            except:
                # Fallback to regex on raw data for version extraction
                sample = pdf_data[:1000].decode('utf-8', errors='ignore')
                version_match = re.search(r'%PDF-(\d+\.\d+)', sample)
                pdf_version = version_match.group(1) if version_match else "Unknown"
            
            # Try to get title from document info
            try:
                if pdf_reader.metadata:
                    if pdf_reader.metadata.get('/Title'):
                        title = pdf_reader.metadata.get('/Title')
            except:
                # Fallback to regex for title extraction
                title_match = re.search(r'/Title\s*\(([^)]+)\)', pdf_data[:2000].decode('utf-8', errors='ignore'))
                title = title_match.group(1) if title_match else "Untitled"
            
            # Get approximate size
            size_kb = len(pdf_data) / 1024
            
            pdf_text = f"PDF document (version {pdf_version}), {page_count} pages, size: {size_kb:.1f} KB"
            
        except Exception as e:
            pdf_text = f"Unable to extract PDF content: {str(e)}"
            extracted_text = "Failed to extract text content from this PDF file."
            pdf_version = "Unknown"
            title = "Unknown"
        
        # Create structured output
        pdf_record = {
            "document_type": "pdf",
            "size_bytes": len(pdf_data),
            "version": pdf_version,
            "title": title,
            "page_count": page_count,
            "content_preview": pdf_text,
            "extracted_text": extracted_text,
            "processed_at": self.shared_memory.get_input_timestamp(input_id),
            "ai_enhanced": False
        }
        
        # Use Gemini for enhanced PDF analysis if available
        if self.llm_client:
            try:
                # Get enhanced analysis from Gemini using the extracted text
                analysis_text = pdf_text
                if extracted_text and len(extracted_text) > 100:
                    # Use the extracted text for better analysis
                    analysis_text = extracted_text[:4000]  # Limit to avoid token limits
                
                llm_result = await self.llm_client.extract_pdf_content(analysis_text, len(pdf_data))
                
                # Clean up the results for display
                clean_result = {}
                
                # Process likely_document_type
                if llm_result.get("likely_document_type"):
                    clean_result["likely_document_type"] = llm_result["likely_document_type"]
                    if clean_result["likely_document_type"] != "unknown":
                        pdf_record["document_type"] = clean_result["likely_document_type"]
                
                # Process estimated_page_count
                if llm_result.get("estimated_page_count"):
                    clean_result["estimated_page_count"] = llm_result["estimated_page_count"]
                else:
                    clean_result["estimated_page_count"] = str(page_count)
                
                # Process content summary if available
                if llm_result.get("content_summary"):
                    clean_result["content_summary"] = llm_result["content_summary"]
                    # Add to main record for easier access
                    pdf_record["content_summary"] = llm_result["content_summary"]
                
                # Process topics - ensure it's a list of strings
                if llm_result.get("topics"):
                    topics = llm_result["topics"]
                    if isinstance(topics, list) and topics:
                        clean_result["topics"] = topics
                    else:
                        clean_result["topics"] = ["Unknown"]
                else:
                    clean_result["topics"] = ["Unknown"]
                
                # Process recommended_next_steps - ensure it's a list of strings
                if llm_result.get("recommended_next_steps"):
                    steps = llm_result["recommended_next_steps"]
                    if isinstance(steps, list) and steps:
                        clean_result["recommended_next_steps"] = steps
                    else:
                        clean_result["recommended_next_steps"] = ["Review document contents"]
                else:
                    clean_result["recommended_next_steps"] = ["Review document contents"]
                
                # Add AI analysis to the record with clean results
                pdf_record["ai_analysis"] = clean_result
                pdf_record["ai_enhanced"] = True
                
                # Add topics to main record if available
                if clean_result.get("topics"):
                    pdf_record["topics"] = clean_result["topics"]
                    
                # Add recommendations to main record if available
                if clean_result.get("recommended_next_steps"):
                    pdf_record["recommendations"] = clean_result["recommended_next_steps"]
                    
            except Exception as e:
                print(f"Error using LLM for PDF analysis: {str(e)}")

        # Generate a document ID for this PDF
        document_id = f"pdf_{input_id}"

        # Log extracted fields to shared memory
        self.shared_memory.log_extracted_fields(input_id, "pdf_agent", pdf_record, document_id)

        return pdf_record 