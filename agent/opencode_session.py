"""OpenCode Go session-affinity header for Hermes → OmniRoute / Go hops.

OpenCode Go rejects chat requests that omit ``x-opencode-session``
(HTTP 400, Console Go). Hermes' built-in ``opencode-go`` profile did not
send it before the upstream post-v0.21.0 fix, and this machine's default
path is OmniRoute (``http://127.0.0.1:20128/v1``), which is a custom
provider — so the official profile hook never ran.

Attach a stable per-conversation value on every request that may land on
Go (direct ``opencode-go/*`` models, the OmniRoute ``qwen3.7`` /
``deepseek-v4-pro`` combos, or the built-in Go endpoint). OmniRoute
forwards ``x-opencode-*`` to the upstream hop.
"""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional

_URL_MARKERS = (":20128",)
_FALLBACK_SESSION = "hermes-omniroute"


def needs_opencode_session(
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> bool:
    """Return True when this request goes through OmniRoute.

    Official OpenCode Zen/Go targets are covered by ``agent.opencode_affinity``.
    OmniRoute (``127.0.0.1:20128``) is a custom provider, so that path never
    runs, and Go rejects the hop without ``x-opencode-session``.
    """
    del model  # model id is not enough; the proxy URL or provider name is
    provider_id = (provider or "").strip().lower()
    url = (base_url or "").strip().lower()
    if provider_id == "omniroute":
        return True
    return any(marker in url for marker in _URL_MARKERS)


def resolve_opencode_session_id(
    session_id: Optional[str] = None,
    cache_scope_id: Optional[str] = None,
) -> str:
    """Stable opaque session id: cache-scope, then session, then ambient, then fallback."""
    try:
        from agent.portal_tags import get_conversation_context

        ambient = get_conversation_context()
    except Exception:
        ambient = None
    raw = cache_scope_id or session_id or ambient or _FALLBACK_SESSION
    try:
        from agent.transports.codex import _cache_scope_from_session_id

        scoped = _cache_scope_from_session_id(str(raw))
    except Exception:
        scoped = str(raw).strip()
    return scoped or _FALLBACK_SESSION


def attach_opencode_session_header(
    kwargs: MutableMapping[str, Any],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    session_id: Optional[str] = None,
    cache_scope_id: Optional[str] = None,
) -> None:
    """Merge ``x-opencode-session`` (and Hermes User-Agent) onto create() kwargs."""
    if not needs_opencode_session(provider=provider, model=model, base_url=base_url):
        return

    existing = kwargs.get("extra_headers")
    headers = dict(existing) if isinstance(existing, Mapping) else {}
    headers["x-opencode-session"] = resolve_opencode_session_id(
        session_id, cache_scope_id
    )
    try:
        from hermes_cli import __version__

        user_agent = f"HermesAgent/{__version__}"
    except Exception:
        user_agent = "HermesAgent"
    headers.setdefault("User-Agent", user_agent)
    headers.setdefault("X-Title", "Hermes Agent")
    kwargs["extra_headers"] = headers
