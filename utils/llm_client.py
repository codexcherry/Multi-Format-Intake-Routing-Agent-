import google.generativeai as genai
import os
from typing import Dict, List, Any, Optional

# Configure the Gemini API with the provided key
API_KEY = "AIzaSyCMEfoX-jyVFslgNRxhbxm1PbXITd-0BU8"
genai.configure(api_key=API_KEY)

class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini client.
        
        Args:
            model_name: The name of the Gemini model to use.
        """
        self.model = genai.GenerativeModel(model_name)
    
    async def classify_content(self, content: str, categories: List[str]) -> str:
        """
        Classify content into one of the given categories using Gemini.
        
        Args:
            content: The text content to classify
            categories: List of possible categories
            
        Returns:
            The most likely category from the provided list
        """
        prompt = f"""
        Classify the following content into one of these categories: {', '.join(categories)}.
        Respond with only the category name, nothing else.
        
        Content:
        {content[:4000]}  # Limiting content length to avoid token limits
        """
        
        response = await self.model.generate_content_async(prompt)
        result = response.text.strip().lower()
        
        # Make sure the result is one of the valid categories
        if result in [cat.lower() for cat in categories]:
            # Return the original case version
            for cat in categories:
                if cat.lower() == result:
                    return cat
        
        # Default to the first category if no match
        return categories[0]
    
    async def extract_email_metadata(self, email_text: str) -> Dict[str, Any]:
        """
        Extract metadata from an email text using Gemini.
        
        Args:
            email_text: The raw email text
            
        Returns:
            Dictionary with sender, subject, intent, urgency, and summary
        """
        prompt = f"""
        Extract the following information from this email:
        - Sender: The email address or name of the sender
        - Subject: The email subject line
        - Intent: The purpose of the email (options: rfq, invoice, complaint, regulation, inquiry, other)
        - Urgency: How urgent is this email (options: high, normal, low)
        - Summary: A brief 1-2 sentence summary of the email content
        
        Format your response as a clean JSON object with the keys 'sender', 'subject', 'intent', 'urgency', and 'summary'.
        Don't include any markdown formatting, just pure JSON.
        
        Email:
        {email_text[:4000]}
        """
        
        response = await self.model.generate_content_async(prompt)
        response_text = response.text.strip()
        
        # Try to extract JSON if it's enclosed in backticks or other markers
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
        
        try:
            # Try to parse as JSON
            import json
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini: {e}")
            print(f"Raw response: {response_text}")
            
            # If JSON parsing fails, use a simple extraction
            result = {}
            
            # Try to extract key-value pairs from the response
            lines = response_text.split('\n')
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip().lower()] = value.strip()
            
            # Ensure all required fields
            for field in ["sender", "subject", "intent", "urgency", "summary"]:
                if field not in result:
                    result[field] = "unknown"
        
        return result
    
    async def analyze_json_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze JSON data using Gemini to extract key insights.
        
        Args:
            json_data: The JSON data to analyze
            
        Returns:
            Dictionary with analysis results
        """
        # Convert JSON to string representation for the prompt
        import json
        json_str = json.dumps(json_data, indent=2)
        
        prompt = f"""
        Analyze this JSON data and provide a comprehensive analysis in clear, simple English:
        
        1. Main entities: List the primary objects or entities represented in this data
        2. Structure analysis: Describe the overall structure and organization of this JSON
        3. Key data points: Identify the most important information contained in this data
        4. Missing fields: Identify any critical fields that appear to be missing
        5. Data quality: Assess the completeness and quality of the data (good, fair, poor)
        6. Purpose: What is the likely purpose or use case for this data?
        7. Insights: Extract 3-4 key insights from this data that would be valuable to a user
        8. Summary: Provide a 2-3 sentence plain English summary explaining what this JSON represents
        
        Format your response as a clean JSON object with these keys:
        - 'main_entities' (as array)
        - 'structure_description' (as string)
        - 'key_data_points' (as array)
        - 'missing_fields' (as array)
        - 'data_quality' (as string)
        - 'likely_purpose' (as string)
        - 'insights' (as array)
        - 'summary' (as string)
        
        Don't include any markdown formatting, just pure JSON.
        
        JSON Data:
        {json_str[:4000]}
        """
        
        response = await self.model.generate_content_async(prompt)
        response_text = response.text.strip()
        
        # Try to extract JSON if it's enclosed in backticks or other markers
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
        
        try:
            # Try to parse as JSON
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini: {e}")
            print(f"Raw response: {response_text}")
            
            # If JSON parsing fails, create a structured response
            result = {
                "main_entities": ["Data Object"],
                "structure_description": "This appears to be a structured JSON document.",
                "key_data_points": ["Contains structured information"],
                "missing_fields": [],
                "data_quality": "unknown",
                "likely_purpose": "Data storage or transfer",
                "insights": ["This JSON contains structured data"],
                "summary": "This is a JSON document containing structured data."
            }
        
        # Ensure all fields are properly formatted
        if isinstance(result.get("main_entities"), str):
            result["main_entities"] = [result["main_entities"]]
            
        if isinstance(result.get("missing_fields"), str):
            result["missing_fields"] = [result["missing_fields"]]
            
        if isinstance(result.get("insights"), str):
            result["insights"] = [result["insights"]]
            
        if isinstance(result.get("key_data_points"), str):
            result["key_data_points"] = [result["key_data_points"]]
            
        # Make sure we have all the expected fields
        for field in ["main_entities", "structure_description", "key_data_points", "missing_fields", 
                      "data_quality", "likely_purpose", "insights", "summary"]:
            if field not in result:
                if field in ["main_entities", "missing_fields", "insights", "key_data_points"]:
                    result[field] = []
                else:
                    result[field] = "unknown"
        
        return result
    
    async def extract_pdf_content(self, pdf_text: str, file_size: int) -> Dict[str, Any]:
        """
        Analyze PDF content using Gemini.
        
        Args:
            pdf_text: Text extracted from the PDF
            file_size: Size of the PDF in bytes
            
        Returns:
            Dictionary with analysis of the PDF
        """
        prompt = f"""
        Based on this extracted PDF content, analyze the document and provide:
        - Likely document type: (report, invoice, manual, article, etc.)
        - Key content summary: A brief 2-3 sentence summary of the main content
        - Topics: 2-3 likely topics covered in this document
        - Recommended next steps: What should be done with this document
        
        Format your response as a clean JSON object with the keys 'likely_document_type', 'content_summary', 'topics' (as array), and 'recommended_next_steps' (as array).
        Don't include any markdown formatting, just pure JSON.
        
        PDF Content:
        {pdf_text}
        Size: {file_size} bytes
        """
        
        response = await self.model.generate_content_async(prompt)
        response_text = response.text.strip()
        
        # Try to extract JSON if it's enclosed in backticks or other markers
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
        
        try:
            # Try to parse as JSON
            import json
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini: {e}")
            print(f"Raw response: {response_text}")
            
            # If JSON parsing fails, create a structured response manually
            result = {
                "likely_document_type": "Report",
                "content_summary": "This document contains information that could not be fully analyzed.",
                "topics": ["Document Analysis", "Information Extraction"],
                "recommended_next_steps": ["Review document contents", "Extract relevant information"]
            }
        
        # Ensure all fields are properly formatted
        if isinstance(result.get("topics"), str):
            result["topics"] = [result["topics"]]
            
        if isinstance(result.get("recommended_next_steps"), str):
            result["recommended_next_steps"] = [result["recommended_next_steps"]]
            
        # Make sure we have all the expected fields
        for field in ["likely_document_type", "content_summary", "topics", "recommended_next_steps"]:
            if field not in result:
                if field in ["topics", "recommended_next_steps"]:
                    result[field] = []
                else:
                    result[field] = "Unknown"
        
        return result 