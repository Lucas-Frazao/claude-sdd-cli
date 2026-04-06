"""AI orchestration layer — constructs prompts, calls the LLM, enforces constraints."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from human_sdd_cli.validators import validate_no_code

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

Your job is to help the developer THINK, not to write their code for them.
"""

# Provider-specific model defaults
_MODEL_DEFAULTS = {
    "openai": "gpt-4o-mini",
    "copilot": "gpt-4o",
}

# Copilot API headers
_COPILOT_HEADERS = {
    "Copilot-Integration-Id": "vscode-chat",
    "editor-version": "Neovim/0.6.1",
    "editor-plugin-version": "copilot.vim/1.16.0",
}

COPILOT_BASE_URL = "https://api.githubcopilot.com"


def _resolve_provider(provider: str, api_key: Optional[str] = None) -> str:
    """Resolve 'auto' provider to a concrete provider name."""
    if provider != "auto":
        return provider

    # Check env var first
    env_provider = os.environ.get("SDD_PROVIDER", "").lower()
    if env_provider in ("openai", "copilot"):
        return env_provider

    # Check if OpenAI API key is available
    if api_key or os.environ.get("OPENAI_API_KEY"):
        return "openai"

    # Check if cached Copilot token exists
    try:
        from human_sdd_cli.auth import has_cached_token
        if has_cached_token():
            return "copilot"
    except ImportError:
        pass

    raise RuntimeError(
        "No AI provider configured. Either:\n"
        "  1. Set OPENAI_API_KEY for OpenAI, or\n"
        "  2. Run 'sdd auth login' for GitHub Copilot, or\n"
        "  3. Use --provider to specify explicitly."
    )


class AIOrchestrator:
    """Manages LLM calls with constitution enforcement."""

    def __init__(
        self,
        *,
        provider: str = "auto",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        audit_dir: Optional[Path] = None,
        project_root: Optional[Path] = None,
    ):
        # Load config if project_root provided
        config = {}
        if project_root is not None:
            try:
                from human_sdd_cli.config import load_config
                config = load_config(project_root)
            except Exception:
                pass

        ai_config = config.get("ai", {})

        # Resolve provider: CLI > env > config > auto-detect
        raw_provider = provider if provider != "auto" else ai_config.get("provider", "auto")
        self.provider = _resolve_provider(raw_provider, api_key)

        # Resolve model: explicit > env > config > provider default
        if model is not None:
            self.model = model
        else:
            env_model = os.environ.get("SDD_MODEL")
            if env_model:
                self.model = env_model
            elif ai_config.get("default_model"):
                self.model = ai_config["default_model"]
            else:
                self.model = _MODEL_DEFAULTS.get(self.provider, "gpt-4o-mini")

        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.audit_dir = audit_dir
        self._client = None

    def _get_client(self):
        """Lazy-import openai and build the appropriate client."""
        if self._client is not None:
            return self._client

        try:
            import openai
        except ImportError:
            raise RuntimeError(
                "The 'openai' package is required for AI commands. "
                "Install it with: pip install openai"
            )

        if self.provider == "copilot":
            from human_sdd_cli.auth import get_copilot_token
            token = get_copilot_token()
            self._client = openai.OpenAI(
                api_key=token,
                base_url=COPILOT_BASE_URL,
                default_headers=_COPILOT_HEADERS,
            )
        else:
            self._client = openai.OpenAI(api_key=self.api_key)

        return self._client

    def _invalidate_client(self) -> None:
        """Reset the cached client so the next call rebuilds it."""
        self._client = None

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
            "provider": self.provider,
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
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=messages,
            )
        except Exception as e:
            # Retry once on auth error for copilot (token may have expired)
            if self.provider == "copilot" and _is_auth_error(e):
                self._invalidate_client()
                client = self._get_client()
                response = client.chat.completions.create(
                    model=self.model,
                    temperature=temperature,
                    messages=messages,
                )
            else:
                raise

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


def _is_auth_error(exc: Exception) -> bool:
    """Check if an exception is an authentication error from the OpenAI SDK."""
    try:
        import openai
        return isinstance(exc, openai.AuthenticationError)
    except ImportError:
        return False
