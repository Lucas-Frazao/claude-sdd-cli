"""Tests for the auth module — device flow, token management, and exceptions."""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from human_sdd_cli.auth.exceptions import (
    CopilotAuthError,
    CopilotNotEnabledError,
    DeviceFlowExpiredError,
    TokenRefreshError,
)


class TestExceptions:
    def test_hierarchy(self):
        assert issubclass(DeviceFlowExpiredError, CopilotAuthError)
        assert issubclass(TokenRefreshError, CopilotAuthError)
        assert issubclass(CopilotNotEnabledError, CopilotAuthError)

    def test_base_is_exception(self):
        assert issubclass(CopilotAuthError, Exception)


class TestDeviceFlow:
    def test_request_device_code(self):
        """Test that request_device_code sends correct request."""
        from human_sdd_cli.auth.device_flow import request_device_code

        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "device_code": "dc_123",
            "user_code": "ABCD-1234",
            "verification_uri": "https://github.com/login/device",
            "expires_in": 900,
            "interval": 5,
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("human_sdd_cli.auth.device_flow.requests.post", return_value=mock_resp) as mock_post:
            result = request_device_code("test-client-id")

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs.kwargs["json"]["client_id"] == "test-client-id"
        assert call_kwargs.kwargs["json"]["scope"] == "read:user"
        assert result["device_code"] == "dc_123"
        assert result["user_code"] == "ABCD-1234"

    def test_request_device_code_error(self):
        """Test error when response doesn't contain device_code."""
        from human_sdd_cli.auth.device_flow import request_device_code

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"error": "bad_request"}
        mock_resp.raise_for_status = MagicMock()

        with patch("human_sdd_cli.auth.device_flow.requests.post", return_value=mock_resp):
            with pytest.raises(CopilotAuthError, match="Unexpected response"):
                request_device_code()

    def test_poll_authorization_pending(self):
        """Test polling handles authorization_pending correctly."""
        from human_sdd_cli.auth.device_flow import poll_for_access_token

        responses = [
            {"error": "authorization_pending"},
            {"access_token": "ghu_test123"},
        ]
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(side_effect=responses)

        with patch("human_sdd_cli.auth.device_flow.requests.post", return_value=mock_resp):
            with patch("human_sdd_cli.auth.device_flow.time.sleep"):
                token = poll_for_access_token("dc_123", interval=0, expires_in=60)

        assert token == "ghu_test123"

    def test_poll_slow_down(self):
        """Test polling handles slow_down by increasing interval."""
        from human_sdd_cli.auth.device_flow import poll_for_access_token

        responses = [
            {"error": "slow_down", "interval": 10},
            {"access_token": "ghu_test456"},
        ]
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(side_effect=responses)

        with patch("human_sdd_cli.auth.device_flow.requests.post", return_value=mock_resp):
            with patch("human_sdd_cli.auth.device_flow.time.sleep"):
                token = poll_for_access_token("dc_123", interval=0, expires_in=60)

        assert token == "ghu_test456"

    def test_poll_expired_token(self):
        """Test polling raises on expired_token error."""
        from human_sdd_cli.auth.device_flow import poll_for_access_token

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"error": "expired_token"}

        with patch("human_sdd_cli.auth.device_flow.requests.post", return_value=mock_resp):
            with patch("human_sdd_cli.auth.device_flow.time.sleep"):
                with pytest.raises(DeviceFlowExpiredError):
                    poll_for_access_token("dc_123", interval=0, expires_in=60)

    def test_poll_access_denied(self):
        """Test polling raises on access_denied error."""
        from human_sdd_cli.auth.device_flow import poll_for_access_token

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"error": "access_denied"}

        with patch("human_sdd_cli.auth.device_flow.requests.post", return_value=mock_resp):
            with patch("human_sdd_cli.auth.device_flow.time.sleep"):
                with pytest.raises(CopilotAuthError, match="denied"):
                    poll_for_access_token("dc_123", interval=0, expires_in=60)

    def test_exchange_for_copilot_token_success(self):
        """Test successful token exchange."""
        from human_sdd_cli.auth.device_flow import exchange_for_copilot_token

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "token": "tid_copilot_token",
            "expires_at": 9999999999,
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("human_sdd_cli.auth.device_flow.requests.get", return_value=mock_resp):
            result = exchange_for_copilot_token("ghu_test")

        assert result["token"] == "tid_copilot_token"
        assert result["expires_at"] == 9999999999

    def test_exchange_401_raises(self):
        """Test 401 raises auth error."""
        from human_sdd_cli.auth.device_flow import exchange_for_copilot_token

        mock_resp = MagicMock()
        mock_resp.status_code = 401

        with patch("human_sdd_cli.auth.device_flow.requests.get", return_value=mock_resp):
            with pytest.raises(CopilotAuthError, match="invalid or expired"):
                exchange_for_copilot_token("ghu_bad")

    def test_exchange_403_raises_not_enabled(self):
        """Test 403 raises CopilotNotEnabledError."""
        from human_sdd_cli.auth.device_flow import exchange_for_copilot_token

        mock_resp = MagicMock()
        mock_resp.status_code = 403

        with patch("human_sdd_cli.auth.device_flow.requests.get", return_value=mock_resp):
            with pytest.raises(CopilotNotEnabledError):
                exchange_for_copilot_token("ghu_nope")

    def test_get_client_id_default(self):
        """Test default client ID."""
        from human_sdd_cli.auth.device_flow import get_client_id

        with patch.dict("os.environ", {}, clear=True):
            assert get_client_id() == "Iv1.b507a08c87ecfe98"

    def test_get_client_id_from_env(self):
        """Test client ID from env var."""
        from human_sdd_cli.auth.device_flow import get_client_id

        with patch.dict("os.environ", {"SDD_COPILOT_CLIENT_ID": "custom_id"}):
            assert get_client_id() == "custom_id"


class TestTokenManager:
    def test_save_and_load_token(self):
        """Test token persistence to a temp directory."""
        from human_sdd_cli.auth import token_manager

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir) / "tokens"
            token_file = tmpdir_path / "copilot-token.json"

            with patch.object(token_manager, "TOKEN_DIR", tmpdir_path), \
                 patch.object(token_manager, "TOKEN_FILE", token_file):
                token_manager.save_token("ghu_oauth", "tid_copilot", 9999999999)

                assert token_file.exists()
                # Check permissions (owner read/write only)
                import stat
                mode = token_file.stat().st_mode
                assert mode & stat.S_IRUSR  # owner can read
                assert mode & stat.S_IWUSR  # owner can write

                data = token_manager.load_token()
                assert data is not None
                assert data["oauth_token"] == "ghu_oauth"
                assert data["copilot_token"] == "tid_copilot"
                assert data["copilot_token_expires_at"] == 9999999999

    def test_load_token_missing(self):
        """Test load_token returns None when file doesn't exist."""
        from human_sdd_cli.auth import token_manager

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(token_manager, "TOKEN_FILE", Path(tmpdir) / "nope.json"):
                assert token_manager.load_token() is None

    def test_delete_token(self):
        """Test token deletion."""
        from human_sdd_cli.auth import token_manager

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            token_file = tmpdir_path / "copilot-token.json"
            token_file.write_text("{}")

            with patch.object(token_manager, "TOKEN_FILE", token_file):
                assert token_manager.delete_token() is True
                assert not token_file.exists()
                assert token_manager.delete_token() is False

    def test_is_copilot_token_valid(self):
        """Test token validity checking."""
        from human_sdd_cli.auth.token_manager import is_copilot_token_valid

        # Valid: expires far in the future
        assert is_copilot_token_valid({"copilot_token_expires_at": time.time() + 3600})

        # Expired
        assert not is_copilot_token_valid({"copilot_token_expires_at": time.time() - 60})

        # About to expire (within buffer)
        assert not is_copilot_token_valid({"copilot_token_expires_at": time.time() + 60})

    def test_has_cached_token(self):
        """Test has_cached_token check."""
        from human_sdd_cli.auth import token_manager

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            token_file = tmpdir_path / "copilot-token.json"

            with patch.object(token_manager, "TOKEN_DIR", tmpdir_path), \
                 patch.object(token_manager, "TOKEN_FILE", token_file):
                assert not token_manager.has_cached_token()

                token_manager.save_token("ghu_x", "tid_x", 9999999999)
                assert token_manager.has_cached_token()

    def test_get_valid_token_cached_valid(self):
        """Test get_valid_token returns cached token when valid."""
        from human_sdd_cli.auth import token_manager

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir) / "tokens"
            token_file = tmpdir_path / "copilot-token.json"

            with patch.object(token_manager, "TOKEN_DIR", tmpdir_path), \
                 patch.object(token_manager, "TOKEN_FILE", token_file):
                token_manager.save_token("ghu_x", "tid_cached", int(time.time()) + 3600)
                result = token_manager.get_valid_token()
                assert result == "tid_cached"

    def test_get_valid_token_refreshes_expired(self):
        """Test get_valid_token refreshes an expired copilot token."""
        from human_sdd_cli.auth import token_manager

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir) / "tokens"
            token_file = tmpdir_path / "copilot-token.json"

            with patch.object(token_manager, "TOKEN_DIR", tmpdir_path), \
                 patch.object(token_manager, "TOKEN_FILE", token_file):
                # Save expired token
                token_manager.save_token("ghu_x", "tid_old", int(time.time()) - 60)

                # Mock the exchange (patched where it's defined, lazy-imported by token_manager)
                with patch(
                    "human_sdd_cli.auth.device_flow.exchange_for_copilot_token",
                    return_value={"token": "tid_refreshed", "expires_at": int(time.time()) + 3600},
                ):
                    result = token_manager.get_valid_token()
                    assert result == "tid_refreshed"
