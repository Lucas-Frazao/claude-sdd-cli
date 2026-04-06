"""Tests for AIOrchestrator — provider detection, client construction, model defaults."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from human_sdd_cli.ai import AIOrchestrator, _resolve_provider, COPILOT_BASE_URL


class TestProviderResolution:
    def test_explicit_openai(self):
        assert _resolve_provider("openai") == "openai"

    def test_explicit_copilot(self):
        assert _resolve_provider("copilot") == "copilot"

    def test_auto_from_env_var(self):
        with patch.dict(os.environ, {"SDD_PROVIDER": "copilot"}):
            assert _resolve_provider("auto") == "copilot"

    def test_auto_from_openai_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=False):
            # Remove SDD_PROVIDER if set
            env = dict(os.environ)
            env.pop("SDD_PROVIDER", None)
            with patch.dict(os.environ, env, clear=True):
                assert _resolve_provider("auto") == "openai"

    def test_auto_from_cached_token(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("human_sdd_cli.auth.has_cached_token", return_value=True):
                assert _resolve_provider("auto") == "copilot"

    def test_auto_no_provider_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("human_sdd_cli.auth.token_manager.has_cached_token", return_value=False):
                with pytest.raises(RuntimeError, match="No AI provider configured"):
                    _resolve_provider("auto")


class TestAIOrchestratorInit:
    def test_default_model_openai(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
            ai = AIOrchestrator(provider="openai")
            assert ai.model == "gpt-4o-mini"
            assert ai.provider == "openai"

    def test_default_model_copilot(self):
        with patch.dict(os.environ, {}, clear=True):
            ai = AIOrchestrator(provider="copilot")
            assert ai.model == "gpt-4o"
            assert ai.provider == "copilot"

    def test_explicit_model_overrides_default(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
            ai = AIOrchestrator(provider="openai", model="gpt-4")
            assert ai.model == "gpt-4"

    def test_env_model_override(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test", "SDD_MODEL": "gpt-3.5-turbo"}, clear=True):
            ai = AIOrchestrator(provider="openai")
            assert ai.model == "gpt-3.5-turbo"


class TestCopilotClientConstruction:
    def test_copilot_client_uses_correct_base_url(self):
        """Test that copilot provider constructs client with correct base URL."""
        mock_token = "tid_test_token"

        with patch("human_sdd_cli.auth.get_copilot_token", return_value=mock_token):
            with patch("openai.OpenAI") as mock_openai_cls:
                ai = AIOrchestrator(provider="copilot")
                ai._get_client()

                mock_openai_cls.assert_called_once()
                call_kwargs = mock_openai_cls.call_args.kwargs
                assert call_kwargs["api_key"] == mock_token
                assert call_kwargs["base_url"] == COPILOT_BASE_URL
                assert "Copilot-Integration-Id" in call_kwargs["default_headers"]
                assert call_kwargs["default_headers"]["Copilot-Integration-Id"] == "vscode-chat"

    def test_openai_client_uses_api_key(self):
        """Test that openai provider constructs standard client."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
            with patch("openai.OpenAI") as mock_openai_cls:
                ai = AIOrchestrator(provider="openai")
                ai._get_client()

                mock_openai_cls.assert_called_once()
                call_kwargs = mock_openai_cls.call_args.kwargs
                assert call_kwargs["api_key"] == "sk-test"
                assert "base_url" not in call_kwargs

    def test_client_is_cached(self):
        """Test that _get_client caches the client instance."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
            with patch("openai.OpenAI") as mock_openai_cls:
                ai = AIOrchestrator(provider="openai")
                client1 = ai._get_client()
                client2 = ai._get_client()
                assert client1 is client2
                mock_openai_cls.assert_called_once()

    def test_invalidate_client_resets_cache(self):
        """Test that _invalidate_client forces a new client on next call."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
            with patch("openai.OpenAI") as mock_openai_cls:
                ai = AIOrchestrator(provider="openai")
                ai._get_client()
                ai._invalidate_client()
                ai._get_client()
                assert mock_openai_cls.call_count == 2


class TestGenerateRetry:
    def test_copilot_retries_on_auth_error(self):
        """Test that generate retries once on auth error for copilot."""
        import openai

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Just prose, no code here."

        mock_client = MagicMock()
        # First call raises AuthenticationError, second succeeds
        mock_client.chat.completions.create.side_effect = [
            openai.AuthenticationError(
                message="Unauthorized",
                response=MagicMock(status_code=401),
                body=None,
            ),
            mock_response,
        ]

        with patch.dict(os.environ, {}, clear=True):
            ai = AIOrchestrator(provider="copilot")
            ai._client = mock_client

            # Mock _get_client to return a fresh working client on retry
            fresh_client = MagicMock()
            fresh_client.chat.completions.create.return_value = mock_response

            original_get = ai._get_client
            call_count = [0]

            def patched_get():
                call_count[0] += 1
                if call_count[0] == 1:
                    return mock_client  # This won't be called since _client is set
                return fresh_client

            with patch.object(ai, "_get_client", side_effect=patched_get):
                result = ai.generate("test prompt")
                assert result == "Just prose, no code here."


class TestConfigIntegration:
    def test_project_config_sets_provider(self):
        """Test that project config can set the provider."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sdd_dir = root / ".sdd"
            sdd_dir.mkdir()
            (sdd_dir / "config.toml").write_text('[ai]\nprovider = "copilot"\n')

            with patch.dict(os.environ, {}, clear=True):
                ai = AIOrchestrator(project_root=root)
                assert ai.provider == "copilot"

    def test_project_config_sets_model(self):
        """Test that project config can set the default model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sdd_dir = root / ".sdd"
            sdd_dir.mkdir()
            (sdd_dir / "config.toml").write_text(
                '[ai]\nprovider = "openai"\ndefault_model = "gpt-4"\n'
            )

            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
                ai = AIOrchestrator(project_root=root)
                assert ai.model == "gpt-4"
