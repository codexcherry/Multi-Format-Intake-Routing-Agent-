import json
from memory.shared_memory import SharedMemory
from utils.llm_client import GeminiClient


class ClassifierAgent:
    def __init__(self, shared_memory: SharedMemory, llm_client: GeminiClient = None):
        self.shared_memory = shared_memory
        self.llm_client = llm_client
    
    async def classify(self, input_data, input_type):
        """
        Classify the input data into a format and intent using a combination of
        rule-based classification and LLM-based classification when available.
        """
        # Detect format based on input type
        format_type = await self._detect_format(input_data, input_type)
        
        # Detect intent using Gemini if available, otherwise use rule-based approach
        intent = await self._detect_intent(input_data, format_type)
        
        return format_type, intent
    
    async def _detect_format(self, input_data, input_type):
        """Detect the format of the input."""
        if input_type == "file":
            # Try to detect if it's a PDF, JSON, or text file based on content
            if isinstance(input_data, bytes):
                # Check for PDF signature
                if input_data.startswith(b'%PDF'):
                    return "pdf"
                else:
                    # Try to parse as JSON
                    try:
                        # Convert first part of bytes to string to check
                        sample = input_data[:1000].decode('utf-8', errors='ignore')
                        if sample.strip().startswith('{') and sample.strip().endswith('}'):
                            return "json"
                        elif 'From:' in sample or 'Subject:' in sample:
                            return "email"
                        else:
                            return "unknown"
                    except:
                        return "unknown"
            else:
                return "unknown"
        elif input_type == "json":
            return "json"
        elif input_type == "email":
            return "email"
        else:
            return "unknown"
    
    async def _detect_intent(self, input_data, format_type):
        """
        Detect the intent of the input based on its content and format.
        Uses Gemini if available, otherwise falls back to rule-based approach.
        """
        # First, prepare text for classification
        if format_type == "json":
            if isinstance(input_data, dict):
                # Convert JSON to string for classification
                text_content = json.dumps(input_data)
            elif isinstance(input_data, bytes):
                try:
                    text_content = input_data.decode('utf-8', errors='ignore')
                except:
                    text_content = str(input_data)
            else:
                text_content = str(input_data)
                
        elif format_type == "email":
            # For emails, ensure it's text
            if isinstance(input_data, bytes):
                text_content = input_data.decode('utf-8', errors='ignore')
            else:
                text_content = str(input_data)
        
        elif format_type == "pdf":
            # For PDFs, we can only use the byte header for rule-based classification
            # as we can't extract text without a proper PDF parser
            return "unknown"
        else:
            return "unknown"
        
        # If we have Gemini client, use it for intent classification
        if self.llm_client and (format_type == "json" or format_type == "email"):
            try:
                # Define the possible intent categories
                intent_categories = ["rfq", "invoice", "complaint", "regulation", "inquiry", "unknown"]
                
                # Use LLM to classify the content
                intent = await self.llm_client.classify_content(
                    text_content, 
                    intent_categories
                )
                return intent
            except Exception as e:
                print(f"Error using LLM for classification: {str(e)}")
                # Fall back to rule-based approach
        
        # Rule-based approach (fallback)
        intent = "unknown"
        text_content = text_content.lower()
        
        if format_type == "json":
            # For JSON, check specific fields or patterns
            if "invoice" in text_content or "payment" in text_content or "bill" in text_content:
                intent = "invoice"
            elif "quote" in text_content or "rfq" in text_content or "request for quote" in text_content:
                intent = "rfq"
            elif "complaint" in text_content or "issue" in text_content or "problem" in text_content:
                intent = "complaint"
            elif "regulation" in text_content or "compliance" in text_content or "legal" in text_content:
                intent = "regulation"
            elif "inquiry" in text_content or "question" in text_content or "information" in text_content:
                intent = "inquiry"
        
        elif format_type == "email":
            # For emails, check content
            if "rfq" in text_content or "request for quote" in text_content or "quotation" in text_content:
                intent = "rfq"
            elif "invoice" in text_content or "payment" in text_content or "bill" in text_content:
                intent = "invoice"
            elif "complaint" in text_content or "issue" in text_content or "problem" in text_content:
                intent = "complaint"
            elif "regulation" in text_content or "compliance" in text_content or "legal" in text_content:
                intent = "regulation"
            elif "inquiry" in text_content or "question" in text_content or "information" in text_content:
                intent = "inquiry"
        
        return intent 