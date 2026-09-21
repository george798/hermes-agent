"""OpenCode Go session-affinity header for OmniRoute / Go hops."""

from agent.opencode_session import (
    attach_opencode_session_header,
    needs_opencode_session,
    resolve_opencode_session_id,
)
from agent.transports.chat_completions import ChatCompletionsTransport


def test_needs_session_for_omniroute_and_go():
    assert needs_opencode_session(provider="omniroute")
    assert needs_opencode_session(model="opencode-go/kimi-k3-max")
    assert needs_opencode_session(base_url="http://127.0.0.1:20128/v1")
    assert needs_opencode_session(base_url="https://opencode.ai/zen/go/v1")
    assert not needs_opencode_session(
        provider="ollama-launch",
        model="qwen3.6:35b-a3b-q4_K_M",
        base_url="http://127.0.0.1:11434/v1",
    )


def test_resolve_prefers_cache_scope_then_session():
    assert resolve_opencode_session_id("sess-1", "scope-root") == "scope-root"
    assert resolve_opencode_session_id("sess-1") == "sess-1"
    assert resolve_opencode_session_id() == "hermes-omniroute"


def test_attach_merges_session_and_user_agent():
    kwargs = {}
    attach_opencode_session_header(
        kwargs,
        provider="omniroute",
        model="opencode-go/kimi-k3-max",
        base_url="http://127.0.0.1:20128/v1",
        session_id="conv-abc",
    )
    headers = kwargs["extra_headers"]
    assert headers["x-opencode-session"] == "conv-abc"
    assert headers["User-Agent"].startswith("HermesAgent/")
    assert headers["X-Title"] == "Hermes Agent"


def test_attach_skips_unrelated_providers():
    kwargs = {}
    attach_opencode_session_header(
        kwargs,
        provider="ollama-launch",
        model="qwen3:8b",
        base_url="http://127.0.0.1:11434/v1",
        session_id="conv-abc",
    )
    assert "extra_headers" not in kwargs


def test_chat_completions_legacy_path_adds_header_for_omniroute():
    kwargs = ChatCompletionsTransport().build_kwargs(
        model="qwen3.7",
        messages=[{"role": "user", "content": "ping"}],
        base_url="http://127.0.0.1:20128/v1",
        provider_name="omniroute",
        session_id="sess-omni",
    )
    assert kwargs["extra_headers"]["x-opencode-session"] == "sess-omni"
