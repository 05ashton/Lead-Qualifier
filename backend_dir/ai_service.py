import os
import json
from ollama import Client
from pydantic import BaseModel, Field
from typing import Literal

ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
client = Client(host=ollama_host)
MODEL_NAME = 'llama3.2:1b'

print(f"Checking for local open-source model {MODEL_NAME}...")
try:
    client.pull(MODEL_NAME)
    print(f"Success: {MODEL_NAME} is ready to use locally.")
except Exception as e:
    print(f"Warning: Could not automatically pull model: {e}")

# NEW: Upgraded schema with strict missing-data rules and the new advice field
class LeadQualification(BaseModel):
    budget: str = Field(description="The budget amount. If not explicitly mentioned, output EXACTLY 'Not Identified'.")
    authority: str = Field(description="Who holds purchasing power. If not mentioned, output EXACTLY 'Not Identified'.")
    need: str = Field(description="The problem they are solving. If not mentioned, output EXACTLY 'Not Identified'.")
    timeline: str = Field(description="When they intend to purchase. If not mentioned, output EXACTLY 'Not Identified'.")
    temperature_score: Literal["Cold", "Warm", "Hot"] = Field(description="Overall rating based on BANT presence.")
    recommended_action: str = Field(description="One highly specific actionable next step. You MUST start the sentence with a verb like 'Call', 'Email', 'Draft', or 'Schedule'. Reference specific BANT data.")
def qualify_lead(raw_notes):
    prompt = f"Read these raw notes and extract the BANT criteria. System: You must output valid JSON matching the schema.\n\nNotes: {raw_notes}"
    
    response = client.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.0}, 
        format=LeadQualification.model_json_schema() 
    )
    
    return response['message']['content']