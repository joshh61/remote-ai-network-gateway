"""Small wrapper around the Anthropic API.

The networking project is the local gateway. This module is the AI backend
that the gateway calls after receiving a request from a network client.
"""

import os

from anthropic import Anthropic


DEFAULT_MODEL = "claude-haiku-4-5"


class AnthropicBackend:
    """Calls Anthropic's Messages API and returns plain text responses."""

    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
            )

        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)

    def ask(self, message: str) -> str:
        """Send a user message to Claude and return the text answer."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=(
                "You are a concise AI assistant running behind a computer networks "
                "class demo gateway. Answer clearly and briefly."
            ),
            messages=[{"role": "user", "content": message}],
        )

        parts: list[str] = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)

        return "\n".join(parts).strip()
