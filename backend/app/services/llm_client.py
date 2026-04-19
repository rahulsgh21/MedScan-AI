"""
LLM Client — Unified interface for multiple LLM providers.

Design Decision: We wrap all LLM providers behind a single interface.
This means switching from Gemini -> Groq -> Ollama is a config change,
not a code rewrite.

Interview talking point:
  "We use a provider-agnostic LLM client with a unified interface.
   The application code doesn't know or care which LLM is running
   behind it. This follows the Dependency Inversion Principle."
"""

import json
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """
    Unified LLM client that supports Gemini, Groq, and Ollama.

    Usage:
        client = LLMClient()
        response = client.generate("Explain hemoglobin")
        structured = client.generate_json("Parse this report...", schema_hint="...")
    """

    def __init__(self):
        self.provider = settings.llm_provider
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize the appropriate LLM client based on config."""
        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "groq":
            self._init_groq()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _init_gemini(self):
        """Initialize Google Gemini client (new google-genai SDK)."""
        from google import genai

        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in .env file")

        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model
        logger.info(f"Initialized Gemini client with model: {self._model}")

    def _init_groq(self):
        """Initialize Groq client."""
        from groq import Groq

        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY not set in .env file")

        self._client = Groq(api_key=settings.groq_api_key)
        logger.info(f"Initialized Groq client with model: {settings.groq_model}")

    def _init_ollama(self):
        """Initialize Ollama client (local models)."""
        logger.info(f"Initialized Ollama client at: {settings.ollama_base_url}")

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        """
        Generate a text response from the LLM.

        Args:
            prompt: The user prompt
            system_instruction: Optional system-level instruction

        Returns:
            The LLM's text response
        """
        if self.provider == "gemini":
            return self._generate_gemini(prompt, system_instruction)
        elif self.provider == "groq":
            return self._generate_groq(prompt, system_instruction)
        elif self.provider == "ollama":
            return self._generate_ollama(prompt, system_instruction)

    def generate_json(self, prompt: str, system_instruction: str = "", response_schema=None) -> dict:
        """
        Generate a JSON response from the LLM.
        Parses the response and returns a Python dict.

        Args:
            prompt: The prompt (should ask for JSON output)
            system_instruction: Optional system instruction
            response_schema: Optional dict representing JSON schema

        Returns:
            Parsed JSON as a dictionary
        """
        if self.provider == "gemini":
            response_text = self._generate_gemini(prompt, system_instruction, response_schema)
        elif self.provider == "groq":
            response_text = self._generate_groq(prompt, system_instruction, json_mode=True)
        elif self.provider == "ollama":
            response_text = self._generate_ollama(prompt, system_instruction)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

        # Clean up the response — LLMs often wrap JSON in markdown code blocks
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]} ... {response_text[-500:]}")
            raise ValueError(
                f"LLM returned invalid JSON. This can happen occasionally. "
                f"Please try again. Error: {e}"
            )

    # ── Provider-specific implementations ───────────────────

    def _generate_gemini(self, prompt: str, system_instruction: str, response_schema=None) -> str:
        """Generate using Google Gemini (new google-genai SDK) with automatic retry."""
        from google.genai import types
        import time

        contents = prompt
        config = types.GenerateContentConfig(
            temperature=0.1,  # Low temperature for structured extraction
            max_output_tokens=8192,  # Enough for large reports
            response_mime_type="application/json",  # Forces clean JSON output
        )
        if system_instruction:
            config.system_instruction = system_instruction
        if response_schema:
            config.response_schema = response_schema

        # Retry logic for transient 503/429 errors from Gemini
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=contents,
                    config=config,
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                is_retryable = "503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower()
                
                if is_retryable and attempt < max_retries:
                    wait_time = 5 * (2 ** (attempt - 1))  # 5s, 10s, 20s
                    logger.warning(
                        f"Gemini API error (attempt {attempt}/{max_retries}): {error_str[:100]}... "
                        f"Retrying in {wait_time}s."
                    )
                    time.sleep(wait_time)
                else:
                    raise  # Not retryable or out of retries

    def _generate_groq(self, prompt: str, system_instruction: str, json_mode: bool = False) -> str:
        """Generate using Groq with optional JSON mode and automatic retry."""
        import time

        messages = []
        if system_instruction:
            # When using JSON mode, Groq requires the system prompt to mention JSON
            sys_content = system_instruction
            if json_mode and "json" not in sys_content.lower():
                sys_content += "\nYou MUST respond with valid JSON only."
            messages.append({"role": "system", "content": sys_content})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": settings.groq_model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 8192,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        # Retry logic for Groq rate limits (free tier: 30 RPM, 6000 TPM)
        max_retries = 4
        for attempt in range(1, max_retries + 1):
            try:
                response = self._client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                error_str = str(e)
                is_retryable = "429" in error_str or "rate_limit" in error_str or "too_many" in error_str.lower()

                if is_retryable and attempt < max_retries:
                    wait_time = 15 * attempt  # 15s, 30s, 45s — Groq rate limits reset quickly
                    logger.warning(
                        f"Groq rate limit (attempt {attempt}/{max_retries}): "
                        f"Retrying in {wait_time}s."
                    )
                    time.sleep(wait_time)
                else:
                    raise

    def _generate_ollama(self, prompt: str, system_instruction: str) -> str:
        """Generate using Ollama (local)."""
        import requests

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = requests.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.1},
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


# Singleton client — import this
llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create the singleton LLM client."""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client
