import re
from memory.shared_memory import SharedMemory
from utils.llm_client import GeminiClient


class EmailAgent:
    def __init__(self, shared_memory: SharedMemory, llm_client: GeminiClient = None):
        self.shared_memory = shared_memory
        self.llm_client = llm_client

    async def process(self, email_text, input_id):
        # Convert bytes to string if needed
        if isinstance(email_text, bytes):
            email_text = email_text.decode('utf-8')
        
        # Make sure email_text is a string
        email_text = str(email_text)
        
        # Use Gemini for enhanced email extraction if available
        if self.llm_client:
            try:
                llm_result = await self.llm_client.extract_email_metadata(email_text)
                
                # Clean up the results for display
                clean_result = {}
                
                # Process sender
                clean_result["sender"] = llm_result.get("sender", "Unknown").strip()
                
                # Process subject
                clean_result["subject"] = llm_result.get("subject", "").strip()
                
                # Process intent - validate it's one of the allowed values
                intent = llm_result.get("intent", "unknown").lower().strip()
                valid_intents = ["rfq", "invoice", "complaint", "regulation", "inquiry", "other"]
                if intent in valid_intents:
                    clean_result["intent"] = intent
                else:
                    clean_result["intent"] = "other"
                
                # Process urgency - validate it's one of the allowed values
                urgency = llm_result.get("urgency", "normal").lower().strip()
                valid_urgencies = ["high", "normal", "low"]
                if urgency in valid_urgencies:
                    clean_result["urgency"] = urgency
                else:
                    clean_result["urgency"] = "normal"
                
                # Process summary
                clean_result["summary"] = llm_result.get("summary", "").strip()
                
                # Create CRM-style record from cleaned LLM extraction
                crm_record = {
                    "sender": clean_result["sender"],
                    "subject": clean_result["subject"],
                    "intent": clean_result["intent"],
                    "urgency": clean_result["urgency"],
                    "summary": clean_result["summary"],
                    "body": email_text,
                    "processed_at": self.shared_memory.get_input_timestamp(input_id),
                    "ai_enhanced": True
                }
                
                # Generate conversation_id for this email
                conversation_id = f"email_{input_id}"
                
                # Log extracted fields to shared memory
                self.shared_memory.log_extracted_fields(input_id, "email_agent", crm_record, conversation_id)
                
                return crm_record
                
            except Exception as e:
                print(f"Error using LLM for email extraction: {str(e)}")
                # Fall back to regex extraction
        
        # Fallback: Use regex extraction (original implementation)
        # Extract sender (looking for the From: line)
        sender_match = re.search(r"From:\s*(.*?)(?:\n|$)", email_text)
        sender = sender_match.group(1).strip() if sender_match else "Unknown"

        # Extract subject
        subject_match = re.search(r"Subject:\s*(.*?)(?:\n|$)", email_text)
        subject = subject_match.group(1).strip() if subject_match else ""

        # Extract intent (simplified example)
        intent = "unknown"
        if "RFQ" in email_text or "Request for Quote" in email_text:
            intent = "rfq"
        elif "invoice" in email_text.lower() or "payment" in email_text.lower():
            intent = "invoice"
        elif "complaint" in email_text.lower() or "issue" in email_text.lower():
            intent = "complaint"
        elif "regulation" in email_text.lower() or "compliance" in email_text.lower():
            intent = "regulation"

        # Extract urgency (simplified example)
        urgency = "normal"
        if "URGENT" in email_text.upper() or "ASAP" in email_text.upper():
            urgency = "high"
        elif "low priority" in email_text.lower() or "when you have time" in email_text.lower():
            urgency = "low"

        # Create CRM-style record
        crm_record = {
            "sender": sender,
            "subject": subject,
            "intent": intent,
            "urgency": urgency,
            "body": email_text,
            "processed_at": self.shared_memory.get_input_timestamp(input_id),
            "ai_enhanced": False
        }

        # Generate conversation_id for this email
        conversation_id = f"email_{input_id}"

        # Log extracted fields to shared memory
        self.shared_memory.log_extracted_fields(input_id, "email_agent", crm_record, conversation_id)

        return crm_record 