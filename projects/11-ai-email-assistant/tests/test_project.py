"""Tests for Project 11: AI Email Assistant."""

import importlib.util
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "reference", "main.py"
)


def _load_module(path: str):
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    with patch("requests.post"):
        return _load_module(SOLUTION_PATH)


# ── chat ──────────────────────────────────────────────────────


class TestChat:
    """Tests for the chat helper."""

    def test_chat_returns_content(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "Dear Sir"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp):
            result = mod.chat([{"role": "user", "content": "hi"}])
            assert result == "Dear Sir"

    def test_chat_sends_messages_and_model(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "ok"}}
        mock_resp.raise_for_status = MagicMock()

        messages = [{"role": "user", "content": "test"}]
        with patch.object(mod.requests, "post", return_value=mock_resp) as mock_post:
            mod.chat(messages)
            body = mock_post.call_args[1]["json"]
            assert body["model"] == mod.MODEL
            assert body["messages"] == messages
            assert body["stream"] is False

    def test_chat_raises_on_http_error(self, mod):
        import requests as real_requests

        with patch.object(
            mod.requests, "post", side_effect=real_requests.ConnectionError("down")
        ):
            with pytest.raises(Exception):
                mod.chat([{"role": "user", "content": "hi"}])


# ── generate_email ────────────────────────────────────────────


class TestGenerateEmail:
    """Tests for the generate_email function."""

    def test_returns_email_and_conversation(self, mod):
        with patch.object(mod, "chat", return_value="Subject: Hello\n\nDear Team,..."):
            email, conversation = mod.generate_email("meeting tomorrow", "professional")
            assert "Subject: Hello" in email
            assert isinstance(conversation, list)

    def test_conversation_has_system_user_assistant(self, mod):
        with patch.object(mod, "chat", return_value="Draft email"):
            _, conversation = mod.generate_email("notes here", "friendly")
            roles = [m["role"] for m in conversation]
            assert roles == ["system", "user", "assistant"]

    def test_tone_appears_in_system_prompt(self, mod):
        with patch.object(mod, "chat", return_value="email") as mock_chat:
            mod.generate_email("notes", "casual")
            messages_sent = mock_chat.call_args[0][0]
            system_msg = messages_sent[0]["content"]
            assert "casual" in system_msg

    def test_notes_appear_in_user_message(self, mod):
        with patch.object(mod, "chat", return_value="email") as mock_chat:
            mod.generate_email("discuss budget Q3", "formal")
            messages_sent = mock_chat.call_args[0][0]
            user_msg = messages_sent[1]["content"]
            assert "discuss budget Q3" in user_msg


# ── refine_email ──────────────────────────────────────────────


class TestRefineEmail:
    """Tests for the refine_email function."""

    def test_refine_appends_feedback_and_returns_new_email(self, mod):
        conversation = [
            {"role": "system", "content": "You are an email writer."},
            {"role": "user", "content": "Write email from notes"},
            {"role": "assistant", "content": "Draft v1"},
        ]
        with patch.object(mod, "chat", return_value="Draft v2"):
            result = mod.refine_email(conversation, "make it shorter")
            assert result == "Draft v2"

    def test_refine_grows_conversation(self, mod):
        conversation = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "write"},
            {"role": "assistant", "content": "v1"},
        ]
        with patch.object(mod, "chat", return_value="v2"):
            mod.refine_email(conversation, "shorter please")
            # Should now have 5 messages: system, user, assistant, user(feedback), assistant(v2)
            assert len(conversation) == 5
            assert conversation[3]["role"] == "user"
            assert "shorter please" in conversation[3]["content"]
            assert conversation[4]["role"] == "assistant"
            assert conversation[4]["content"] == "v2"

    def test_refine_sends_full_conversation_to_chat(self, mod):
        conversation = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "write"},
            {"role": "assistant", "content": "v1"},
        ]
        with patch.object(mod, "chat", return_value="v2") as mock_chat:
            mod.refine_email(conversation, "add greeting")
            sent = mock_chat.call_args[0][0]
            # The full conversation including the new feedback message
            assert len(sent) == 4
