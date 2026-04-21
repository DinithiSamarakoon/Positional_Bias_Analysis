from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


OPENROUTER_MODELS = {
    "gemini-2.0-flash-lite": "google/gemini-2.0-flash-lite-001",
    "gemini-2.0-flash": "google/gemini-2.0-flash-001",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4o": "openai/gpt-4o",
    "claude-3-haiku": "anthropic/claude-3-haiku",
    "claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
    "llama-3.2-3b-instruct": "meta-llama/llama-3.2-3b-instruct",
}

MODEL_ALIASES = {
    # User-friendly names
    "gemini 2.0 flash-lite": OPENROUTER_MODELS["gemini-2.0-flash-lite"],
    "gemini 2.0 flash": OPENROUTER_MODELS["gemini-2.0-flash"],
    "gpt-4o mini": OPENROUTER_MODELS["gpt-4o-mini"],
    "gpt 4o": OPENROUTER_MODELS["gpt-4o"],
    "claude 3 haiku": OPENROUTER_MODELS["claude-3-haiku"],
    "claude 3.7 sonnet": OPENROUTER_MODELS["claude-3.7-sonnet"],
    "llama 3.2 3b instruct": OPENROUTER_MODELS["llama-3.2-3b-instruct"],
    # Kebab-case aliases
    "gemini-2.0-flash-lite": OPENROUTER_MODELS["gemini-2.0-flash-lite"],
    "gemini-2.0-flash": OPENROUTER_MODELS["gemini-2.0-flash"],
    "gpt-4o-mini": OPENROUTER_MODELS["gpt-4o-mini"],
    "gpt-4o": OPENROUTER_MODELS["gpt-4o"],
    "claude-3-haiku": OPENROUTER_MODELS["claude-3-haiku"],
    "claude-3.7-sonnet": OPENROUTER_MODELS["claude-3.7-sonnet"],
}


@dataclass
class GenerationResult:
    text: str
    raw: dict | None = None


class BaseModelClient:
    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> GenerationResult:
        raise NotImplementedError

    @staticmethod
    def resolve_model(model: str) -> str:
        key = model.strip().lower()
        return MODEL_ALIASES.get(key, model)


class MockModelClient(BaseModelClient):
    """Deterministic local stub to validate experiment flow without API cost."""

    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> GenerationResult:
        lower = prompt.lower()
        mentions_negative = any(token in lower for token in ["negative", "complaint", "issue", "bad", "poor"])
        if mentions_negative:
            summary = (
                "Most reviews are positive about quality and overall experience, "
                "but one reviewer reports a negative issue that should be considered."
            )
        else:
            summary = "Reviews are mostly positive overall, with generally favorable customer sentiment."
        return GenerationResult(text=summary)


class OpenAIChatClient(BaseModelClient):
    def __init__(self):
        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError("Install the openai package: pip install openai") from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        self._client = OpenAI(api_key=api_key)

    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> GenerationResult:
        response = self._client.responses.create(
            model=self.resolve_model(model),
            input=prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        text = getattr(response, "output_text", "") or ""
        return GenerationResult(text=text, raw={"id": getattr(response, "id", None)})


<<<<<<< HEAD
class OpenRouterChatClient(BaseModelClient):
    def __init__(self):
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Install the openai package: pip install openai") from exc

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:  # pragma: no cover
            raise RuntimeError("OPENROUTER_API_KEY is not set.")

        site_url = os.getenv("OPENROUTER_SITE_URL", "http://localhost")
        app_name = os.getenv("OPENROUTER_APP_NAME", "nlp_project")

        self._client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": site_url,
                "X-Title": app_name,
            },
        )

    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> GenerationResult:
        resolved_model = self.resolve_model(model)
        response = self._client.responses.create(
            model=resolved_model,
            input=prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        text = getattr(response, "output_text", "") or ""
        return GenerationResult(
            text=text,
            raw={"id": getattr(response, "id", None), "model": resolved_model},
        )
=======
class TogetherAIChatClient(BaseModelClient):
    def __init__(self):
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise RuntimeError("TOGETHER_API_KEY is not set.")
        self._api_key = api_key
        self._endpoint = "https://api.together.ai/v1/chat/completions"

    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> GenerationResult:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        request = urllib.request.Request(
            self._endpoint,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Together.ai request failed: {exc.code} {exc.reason}: {body}") from exc

        text = ""
        if isinstance(data, dict):
            text = data.get("output_text", "") or ""
            if not text:
                choices = data.get("choices")
                if isinstance(choices, list) and choices:
                    first = choices[0]
                    if isinstance(first, dict):
                        message = first.get("message") or {}
                        text = message.get("content", "") or first.get("text", "")
        return GenerationResult(text=text, raw=data)


class HuggingFaceModelClient(BaseModelClient):
    def __init__(self):
        api_key = os.getenv("HF_TOKEN")
        if not api_key:
            raise RuntimeError("HF_TOKEN is not set.")
        self._api_key = api_key

    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> GenerationResult:
        endpoint = f"https://api-inference.huggingface.co/models/{model}"
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
            },
        }
        request = urllib.request.Request(
            endpoint,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Hugging Face request failed: {exc.code} {exc.reason}: {body}") from exc

        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(f"Hugging Face error: {data['error']}")

        text = ""
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                text = first.get("generated_text", "") or first.get("text", "")
        elif isinstance(data, dict):
            text = data.get("generated_text", "") or data.get("text", "")
        if not text and isinstance(data, str):
            text = data

        return GenerationResult(text=text, raw=data)


# ONLY ONE GroqClient - CORRECT VERSION
class GroqClient(BaseModelClient):
    """Free Groq Llama client - Uses model from command line"""
    
    def __init__(self):
        try:
            from groq import Groq
        except ImportError:
            raise RuntimeError("Install groq: pip install groq")
        
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not set.")
        
        self.client = Groq(api_key=self.api_key)
        print(f"GroqClient initialized. Ready to use models.")

    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> GenerationResult:
        # Use the model passed from run_experiments.py
        model_to_use = model if model else "llama-3.3-70b-versatile"
        print(f"Using model: {model_to_use}")
        
        try:
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = response.choices[0].message.content
            if text:
                print(f"✓ Generated {len(text)} chars")
                return GenerationResult(text=text, raw=response.model_dump())
            else:
                return GenerationResult(text="[No response from Groq]", raw={"error": "empty"})
        except Exception as e:
            print(f"❌ Groq API Error: {e}")
            return GenerationResult(text=f"[Groq API Error: {e}]", raw={"error": str(e)})
>>>>>>> 6e2b721 (Initial commit)


def build_model_client(provider: str) -> BaseModelClient:
    provider_norm = provider.strip().lower()
    if provider_norm == "mock":
        return MockModelClient()
    if provider_norm == "openrouter":
        return OpenRouterChatClient()
    if provider_norm == "openai":
        return OpenAIChatClient()
<<<<<<< HEAD
    raise ValueError(f"Unsupported provider '{provider}'. Use 'mock', 'openrouter', or 'openai'.")
=======
    if provider_norm == "together":
        return TogetherAIChatClient()
    if provider_norm == "huggingface":
        return HuggingFaceModelClient()
    if provider_norm == "groq":
        return GroqClient()
    raise ValueError(
        f"Unsupported provider '{provider}'. Use 'mock', 'openai', 'together', 'huggingface', or 'groq'."
    )
>>>>>>> 6e2b721 (Initial commit)
