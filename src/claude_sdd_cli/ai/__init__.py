"""AI orchestration layer — constructs prompts, calls the LLM, enforces constraints."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from claude_sdd_cli.validators import validate_no_code

# ── System prompt (constitution-level constraint) ────────────────────

SYSTEM_PROMPT = """\
You are a planning-only engineering copilot operating under a strict constitution.

ABSOLUTE RULES — violation of any rule invalidates your output:
1. You MUST NOT produce executable code in any programming language.
2. You MUST NOT produce code fences containing implementation, test, config, or script content.
3. You MUST NOT produce copy-paste-ready snippets, shell commands, SQL queries, or DSL fragments.
4. You MUST NOT produce Dockerfiles, Makefiles, CI configs, or infrastructure-as-code.
5. You MAY use plain-English pseudostructure to describe logic at a high level.
6. You MAY produce Markdown tables, checklists, decision records, and prose descriptions.
7. When requirements are ambiguous, mark them with [NEEDS CLARIFICATION] instead of guessing.
8. Every statement you make should trace back to a user requirement or explicit assumption.

Your job is to help THINK through requirements and planning. Implementation is handled by Claude CLI, not by you.
"""


class AIOrchestrator:
    """Manages LLM calls with constitution enforcement."""

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        audit_dir: Optional[Path] = None,
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.audit_dir = audit_dir

    def _get_client(self):
        """Lazy-import openai so the rest of the CLI works without a key."""
        try:
            import openai
        except ImportError:
            raise RuntimeError(
                "The 'openai' package is required for AI commands. "
                "Install it with: pip install openai"
            )
        return openai.OpenAI(api_key=self.api_key)

    def _audit_log(self, role: str, content: str, feature: str) -> None:
        """Append to the audit trail if audit_dir is set."""
        if self.audit_dir is None:
            return
        log_file = self.audit_dir / f"{feature}-audit.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "model": self.model,
            "content_length": len(content),
            "content_preview": content[:500],
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def generate(
        self,
        user_prompt: str,
        *,
        feature: str = "unknown",
        extra_system: str = "",
        temperature: float = 0.4,
    ) -> str:
        """Send a prompt to the LLM, validate the response, return clean text.

        Raises ValueError if the response contains executable code.
        """
        system = SYSTEM_PROMPT
        if extra_system:
            system += "\n\n" + extra_system

        self._audit_log("user", user_prompt, feature)

        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = response.choices[0].message.content or ""
        self._audit_log("assistant", text, feature)

        # Constitution enforcement
        result = validate_no_code(text)
        if not result.passed:
            self._audit_log("violation", result.summary(), feature)
            raise ValueError(
                "AI response violated the no-code constitution.\n\n"
                + result.summary()
                + "\n\nThe output has been rejected. Retry or refine your prompt."
            )

        return text
