"""LLM client wrapper for Gemini API and local Ollama."""

from __future__ import annotations

import os

import requests


class LLMEngine:
    """Simple abstraction for either Gemini or Ollama generation."""

    def __init__(self, provider: str = "gemini") -> None:
        self.provider = provider.lower()

    def generate(self, prompt: str) -> str:
        if self.provider == "gemini":
            return self._generate_with_gemini(prompt)
        if self.provider == "ollama":
            return self._generate_with_ollama(prompt)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _generate_with_gemini(self, prompt: str) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        body = response.json()
        return (
            body.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )

    def _generate_with_ollama(self, prompt: str) -> str:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.1")
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        body = response.json()
        return str(body.get("response", "")).strip()
