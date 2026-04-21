from __future__ import annotations

import os
from .model_client import BaseModelClient, GenerationResult


class GroqClient(BaseModelClient):
    """Free Groq Llama client - Corrected to use new model names"""
    
    def __init__(self):
        try:
            from groq import Groq
        except ImportError:
            raise RuntimeError("Install groq: pip install groq")
        
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not set.")
        
        self.client = Groq(api_key=self.api_key)
        # --- CHANGE IS HERE ---
        # Define the correct, active model name as the default.
        # This overrides any other model name passed to the generate method.
        self.active_model = "llama-3.3-70b-versatile"
        # ----------------------
        print(f"GroqClient initialized. Using model: {self.active_model}")

    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> GenerationResult:
        # --- CHANGE IS HERE ---
        # Ignore the 'model' argument passed from the command line
        # and ALWAYS use the active_model we defined.
        model_to_use = self.active_model
        # ----------------------
        
        try:
            response = self.client.chat.completions.create(
                model=model_to_use, # Use the correct model
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = response.choices[0].message.content
            if text:
                print(f"✓ Generated {len(text)} chars using {model_to_use}")
                return GenerationResult(text=text, raw=response.model_dump())
            else:
                return GenerationResult(text="[No response from Groq]", raw={"error": "empty"})
        except Exception as e:
            print(f"❌ Groq API Error: {e}")
            # Return a clearly marked error message
            return GenerationResult(text=f"[Groq API Error: {e}]", raw={"error": str(e)})