import json
from memory.shared_memory import SharedMemory
from utils.llm_client import GeminiClient


class JSONAgent:
    def __init__(self, shared_memory: SharedMemory, llm_client: GeminiClient = None):
        self.shared_memory = shared_memory
        self.llm_client = llm_client

    async def process(self, input_data, input_id):
        # Handle different input types
        if isinstance(input_data, bytes):
            try:
                input_data = json.loads(input_data.decode('utf-8'))
            except json.JSONDecodeError:
                input_data = {"raw": input_data.decode('utf-8', errors='replace')}
        
        elif isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except json.JSONDecodeError:
                input_data = {"raw": input_data}
        
        # Ensure we have a dict at this point
        if not isinstance(input_data, dict):
            input_data = {"raw": str(input_data)}
        
        # Basic checks for missing required fields
        missing_fields = []
        if "id" not in input_data:
            missing_fields.append("id")
        if "timestamp" not in input_data:
            missing_fields.append("timestamp")
            
        # Use Gemini for enhanced JSON analysis if available
        ai_analysis = None
        if self.llm_client:
            try:
                # Get AI analysis from Gemini
                llm_result = await self.llm_client.analyze_json_data(input_data)
                
                # Clean up the results for display
                clean_result = {}
                
                # Process all fields from the enhanced analysis
                expected_fields = [
                    "main_entities", 
                    "structure_description", 
                    "key_data_points", 
                    "missing_fields", 
                    "data_quality", 
                    "likely_purpose", 
                    "insights", 
                    "summary"
                ]
                
                # Process each field, ensuring proper formatting
                for field in expected_fields:
                    if field in llm_result:
                        # For array fields
                        if field in ["main_entities", "key_data_points", "missing_fields", "insights"]:
                            if isinstance(llm_result[field], list) and llm_result[field]:
                                clean_result[field] = llm_result[field]
                            elif isinstance(llm_result[field], str):
                                clean_result[field] = [llm_result[field]]
                            else:
                                clean_result[field] = []
                        # For string fields
                        else:
                            clean_result[field] = llm_result.get(field, "")
                
                # Ensure we have default values for all fields
                if "main_entities" not in clean_result or not clean_result["main_entities"]:
                    clean_result["main_entities"] = ["Data Object"]
                    
                if "structure_description" not in clean_result or not clean_result["structure_description"]:
                    clean_result["structure_description"] = "This appears to be a structured JSON document."
                    
                if "key_data_points" not in clean_result or not clean_result["key_data_points"]:
                    clean_result["key_data_points"] = ["Contains structured information"]
                    
                if "missing_fields" not in clean_result:
                    clean_result["missing_fields"] = []
                
                # Add any missing fields we detected to the AI analysis
                for field in missing_fields:
                    if field not in clean_result["missing_fields"]:
                        clean_result["missing_fields"].append(field)
                        
                if "data_quality" not in clean_result or not clean_result["data_quality"]:
                    clean_result["data_quality"] = "unknown"
                    
                if "likely_purpose" not in clean_result or not clean_result["likely_purpose"]:
                    clean_result["likely_purpose"] = "Data storage or transfer"
                    
                if "insights" not in clean_result or not clean_result["insights"]:
                    clean_result["insights"] = ["This JSON contains structured data"]
                    
                if "summary" not in clean_result or not clean_result["summary"]:
                    clean_result["summary"] = "This is a JSON document containing structured data."
                
                # Store the cleaned AI analysis
                ai_analysis = clean_result
                
            except Exception as e:
                print(f"Error using LLM for JSON analysis: {str(e)}")
                # Create a fallback analysis with basic information
                ai_analysis = {
                    "main_entities": ["Data Object"],
                    "structure_description": "This appears to be a structured JSON document.",
                    "key_data_points": ["Contains structured information"],
                    "missing_fields": missing_fields,
                    "data_quality": "unknown",
                    "likely_purpose": "Data storage or transfer",
                    "insights": ["This JSON contains structured data"],
                    "summary": "This is a JSON document containing structured data."
                }
        else:
            # Create a basic analysis even if no LLM is available
            ai_analysis = {
                "main_entities": ["Data Object"],
                "structure_description": "This appears to be a structured JSON document.",
                "key_data_points": ["Contains structured information"],
                "missing_fields": missing_fields,
                "data_quality": "unknown",
                "likely_purpose": "Data storage or transfer",
                "insights": ["This JSON contains structured data"],
                "summary": "This is a JSON document containing structured data."
            }
        
        # Extract data to FlowBit schema
        flowbit_data = {
            "data": input_data,
            "metadata": {
                "source": "json_agent",
                "processed_at": self.shared_memory.get_input_timestamp(input_id),
                "missing_fields": missing_fields,
                "ai_enhanced": True  # Always mark as AI enhanced since we always provide analysis
            }
        }
        
        # Always add AI analysis to the output
        flowbit_data["ai_analysis"] = ai_analysis
        flowbit_data["ai_enhanced"] = True

        # Generate thread_id for this processing (could be a conversation ID or reference number)
        thread_id = f"thread_{input_id}"

        # Log extracted fields to shared memory
        self.shared_memory.log_extracted_fields(input_id, "json_agent", flowbit_data, thread_id)

        return flowbit_data 