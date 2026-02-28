"""
MaterCare Homes - Model Module
===============================
Fine-tuned LLM for eldercare assistance.
"""

from typing import Optional, List, Dict, Any
import os

class MaterCareLLM:
    """Eldercare specialized LLM wrapper."""
    
    def __init__(
        self,
        model_path: str = "Taurus-AI-Corp/matercare-llama-3.2-3b",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        self.model_path = model_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
    
    def _init_client(self):
        """Lazy initialization of HuggingFace client."""
        try:
            from huggingface_hub import InferenceClient
            self._client = InferenceClient(self.model_path)
        except ImportError:
            raise ImportError("huggingface-hub required. Install: pip install huggingface-hub")
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send a chat message and get response."""
        if not self._client:
            self._init_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        response = self._client.chat_completion(
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content
    
    def generate(self, prompt: str) -> str:
        """Generate text from prompt."""
        if not self._client:
            self._init_client()
        
        return self._client.text_generation(
            prompt,
            temperature=self.temperature,
            max_new_tokens=self.max_tokens
        )


class CarePlanGenerator:
    """Generate personalized care plans."""
    
    def __init__(self, llm: MaterCareLLM):
        self.llm = llm
    
    def generate(
        self,
        patient_name: str,
        conditions: List[str],
        mobility: str,
        cognitive_status: str
    ) -> Dict[str, Any]:
        """Generate a care plan based on patient profile."""
        prompt = f"""Generate a comprehensive care plan for {patient_name}.
        
Conditions: {', '.join(conditions)}
Mobility: {mobility}
Cognitive Status: {cognitive_status}

Include:
1. Daily routine recommendations
2. Medication reminders
3. Safety precautions
4. Nutrition guidelines
5. Activities for engagement
6. Warning signs to monitor

Format as JSON."""
        
        response = self.llm.chat(prompt, system_prompt="You are a geriatric care specialist.")
        
        return {
            "patient": patient_name,
            "conditions": conditions,
            "plan": response,
            "generated_by": "MaterCare AI"
        }


def get_default_system_prompt() -> str:
    """Get the default system prompt for MaterCare."""
    return """You are MaterCare, an AI assistant specialized in geriatric care and elder wellness.
Provide compassionate, accurate information about eldercare, but always remind users to consult healthcare professionals for medical advice."""
