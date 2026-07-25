"""
llm_client.py — thin async wrapper around the OpenAI SDK.

All agent skill modules return {"system": str, "user": str} dicts.
Pass them directly to `call()`.

API key: set OPENAI_API_KEY in the environment. Plaintext keys passed through
configuration are rejected.

Interaction log
---------------
When an interaction log path is supplied, metadata-only logging is the default.
Full prompt/response logging requires an explicit ``full_content`` mode.
Metadata entries contain:
  timestamp     ISO-8601 UTC
  agent         e.g. "agent1", "agentA"   (derived from the label prefix)
  skill         e.g. "build_language_template"  (rest of the label)
  prompt hashes and lengths (never prompt text)
  response hash and length (never response text)
  requested and returned model identifiers
  token usage, retry, parse status, and system fingerprint when available
  label         full label string as passed by the caller
"""

from __future__ import annotations

import importlib.metadata
import json
import logging
import os
import re
import stat
import time
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI, OpenAIError

logger = logging.getLogger(__name__)

MODEL = "gpt-4o"
MAX_TOKENS = 16384
MAX_PARSE_RETRIES = 2   # total attempts = 1 + MAX_PARSE_RETRIES
INTERACTION_LOG_MODES = frozenset({"off", "metadata_only", "full_content"})
DEFAULT_INTERACTION_LOG_MODE = "metadata_only"
DEFAULT_LOG_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_LOG_BACKUPS = 3
DEFAULT_LOG_RETENTION_DAYS = 30
DEFAULT_RUNTIME_CONFIG = (
    Path(__file__).resolve().parents[2] / "configs" / "hlayer-runtime.json"
)
_SECRET_RES = (
    re.compile(
        r"\b(?:(?:sk|sess)-[A-Za-z0-9_-]{12,}|"
        r"gh[pousr]_[A-Za-z0-9]{12,}|"
        r"github_pat_[A-Za-z0-9_]{40,})\b"
    ),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(
        r"-----BEGIN (?:(?:RSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
        r"[\s\S]*?"
        r"-----END (?:(?:RSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
    ),
    re.compile(
        r"-----BEGIN (?:(?:RSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
    ),
)


def _is_link_or_reparse_point(path: Path) -> bool:
    """Return True for symbolic links and Windows reparse points."""

    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    file_attributes = getattr(info, "st_file_attributes", 0)
    return stat.S_ISLNK(info.st_mode) or bool(
        reparse_flag and file_attributes & reparse_flag
    )


def _assert_link_free_path(path: Path) -> None:
    """Reject a log path when any existing component redirects elsewhere."""

    absolute = Path(os.path.abspath(os.fspath(path)))
    components = [absolute, *absolute.parents]
    for component in reversed(components):
        if os.path.lexists(component) and _is_link_or_reparse_point(component):
            raise OSError(
                "interaction log path contains a symbolic link or reparse point: "
                f"{component}"
            )


def _load_interaction_log_policy() -> dict[str, Any]:
    configured = os.getenv("VEGO_HLAYER_RUNTIME_CONFIG")
    path = Path(configured).expanduser() if configured else DEFAULT_RUNTIME_CONFIG
    if not path.is_file():
        if configured:
            raise ValueError(f"VEGO_HLAYER_RUNTIME_CONFIG does not exist: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid H-layer runtime configuration: {path}") from exc
    h_layer = payload.get("h_layer")
    if not isinstance(h_layer, dict):
        raise ValueError("H-layer runtime configuration must contain an h_layer object")
    interaction_log = h_layer.get("interaction_log") or {}
    if not isinstance(interaction_log, dict):
        raise ValueError("h_layer.interaction_log must be an object")
    return {
        "mode": h_layer.get("interaction_log_mode"),
        **interaction_log,
    }


class LLMClient:
    """Async OpenAI client shared across the entire pipeline run."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = MODEL,
        interaction_log: Path | None = None,
        interaction_log_mode: str | None = None,
        interaction_log_max_bytes: int | None = None,
        interaction_log_backups: int | None = None,
        interaction_log_retention_days: int | None = None,
    ) -> None:
        if api_key:
            raise ValueError(
                "Plaintext API keys are not accepted; use OPENAI_API_KEY or a project secret."
            )
        policy = _load_interaction_log_policy()
        self._client = AsyncOpenAI(api_key=None)
        self.model = model
        self._log_path = interaction_log
        self._log_mode = (
            interaction_log_mode
            or os.getenv("VEGO_INTERACTION_LOG_MODE")
            or policy.get("mode")
            or DEFAULT_INTERACTION_LOG_MODE
        )
        interaction_log_max_bytes = (
            interaction_log_max_bytes
            if interaction_log_max_bytes is not None
            else policy.get("max_bytes", DEFAULT_LOG_MAX_BYTES)
        )
        interaction_log_backups = (
            interaction_log_backups
            if interaction_log_backups is not None
            else policy.get("backups", DEFAULT_LOG_BACKUPS)
        )
        interaction_log_retention_days = (
            interaction_log_retention_days
            if interaction_log_retention_days is not None
            else policy.get("retention_days", DEFAULT_LOG_RETENTION_DAYS)
        )
        if self._log_mode not in INTERACTION_LOG_MODES:
            raise ValueError(
                f"interaction_log_mode must be one of {sorted(INTERACTION_LOG_MODES)}"
            )
        if not isinstance(interaction_log_max_bytes, int) or interaction_log_max_bytes < 1:
            raise ValueError("interaction_log_max_bytes must be a positive integer")
        if not isinstance(interaction_log_backups, int) or interaction_log_backups < 1:
            raise ValueError("interaction_log_backups must be a positive integer")
        if (
            not isinstance(interaction_log_retention_days, int)
            or not 1 <= interaction_log_retention_days <= 365
        ):
            raise ValueError("interaction_log_retention_days must be between 1 and 365")
        self._log_max_bytes = interaction_log_max_bytes
        self._log_backups = interaction_log_backups
        self._log_retention_days = interaction_log_retention_days
        if self._log_mode == "full_content":
            if policy.get("redaction_enabled", True) is not True:
                raise ValueError("full-content interaction logging requires redaction")
            if policy.get("full_content_local_only", True) is not True:
                raise ValueError("full-content interaction logging must remain local-only")
        if interaction_log:
            if str(interaction_log).startswith(("\\\\", "//")):
                raise ValueError("interaction logs must use local storage")
            _assert_link_free_path(interaction_log.parent)
            log_directory_created = not interaction_log.parent.exists()
            interaction_log.parent.mkdir(parents=True, exist_ok=True)
            _assert_link_free_path(interaction_log)
            if log_directory_created:
                try:
                    interaction_log.parent.chmod(0o700)
                except OSError:
                    logger.debug(
                        "Could not restrict newly created interaction-log "
                        "directory permissions."
                    )
            logger.info("Interaction log (%s) → %s", self._log_mode, interaction_log)
            if self._log_mode == "full_content":
                logger.warning(
                    "Full-content interaction logging is enabled explicitly. "
                    "Redaction is best effort; retain locally for at most %d days.",
                    self._log_retention_days,
                )

    async def call(
        self,
        prompt: dict[str, str],
        *,
        label: str = "",
        max_tokens: int = MAX_TOKENS,
    ) -> dict[str, Any]:
        """
        Send a prompt dict and return the parsed JSON response.

        Parameters
        ----------
        prompt     : {"system": str, "user": str} as returned by skill *_prompt() helpers.
        label      : Dot-separated label: "<agent>/<skill>"
                     e.g. "agent1/build_language_template"
                          "agentA/map_and_assign"
                          "agent3/case-01/map"
        max_tokens : Override max_tokens for this call.

        Returns
        -------
        Parsed JSON dict from the model's text response.

        Raises
        ------
        ValueError  if the model returns non-JSON text after all retry attempts.
        """
        tag = f"[{label}] " if label else ""
        total_attempts = 1 + MAX_PARSE_RETRIES

        for attempt in range(1, total_attempts + 1):
            logger.info("%sCalling %s (attempt %d/%d)…", tag, self.model, attempt, total_attempts)

            try:
                response = await self._client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": prompt["system"]},
                        {"role": "user",   "content": prompt["user"]},
                    ],
                )
            except OpenAIError as exc:
                self._write_interaction(
                    label=label,
                    prompt=prompt,
                    raw="",
                    parsed=None,
                    parse_error=None,
                    api_error=type(exc).__name__,
                    response=None,
                    attempt=attempt,
                    max_tokens=max_tokens,
                )
                raise

            raw = response.choices[0].message.content or ""
            logger.debug("%sRaw response (%d chars)", tag, len(raw))

            parsed: dict[str, Any] | None = None
            parse_error: str | None = None
            try:
                parsed = self._parse_json(raw, label=label)
            except ValueError as exc:
                parse_error = str(exc)
                # Always log this attempt, then decide whether to retry or raise
                self._write_interaction(
                    label=label,
                    prompt=prompt,
                    raw=raw,
                    parsed=None,
                    parse_error=parse_error,
                    api_error=None,
                    response=response,
                    attempt=attempt,
                    max_tokens=max_tokens,
                )
                if attempt < total_attempts:
                    logger.warning(
                        "%sParse failed (attempt %d/%d) — retrying…",
                        tag, attempt, total_attempts,
                    )
                    continue
                raise
            else:
                self._write_interaction(
                    label=label,
                    prompt=prompt,
                    raw=raw,
                    parsed=parsed,
                    parse_error=None,
                    api_error=None,
                    response=response,
                    attempt=attempt,
                    max_tokens=max_tokens,
                )
                return parsed

        # Unreachable — the loop always returns or raises, but satisfies type checkers.
        raise RuntimeError("call() exited retry loop without returning")

    # ------------------------------------------------------------------
    # Interaction log
    # ------------------------------------------------------------------

    def _write_interaction(
        self,
        *,
        label: str,
        prompt: dict[str, str],
        raw: str,
        parsed: dict | None,
        parse_error: str | None,
        api_error: str | None = None,
        response: Any,
        attempt: int,
        max_tokens: int = MAX_TOKENS,
    ) -> None:
        """Append one JSONL entry to the interaction log (if enabled)."""
        if not self._log_path or self._log_mode == "off":
            return

        # Derive agent and skill from label: "agent1/build_template" → agent1, build_template
        # Labels with 3 parts like "agent3/case-01/map" → agent3, case-01/map
        parts = label.split("/", 1)
        agent = parts[0] if parts else ""
        skill = parts[1] if len(parts) > 1 else ""

        usage = getattr(response, "usage", None) if response is not None else None
        config = {"model": self.model, "max_tokens": max_tokens}
        logged_parse_error = (
            "invalid_json_response"
            if parse_error is not None
            else None
        )
        entry: dict[str, Any] = {
            "schema_version": "model-execution-manifest-v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent":     agent,
            "skill":     skill,
            "label":     label,
            "requested_model": self.model,
            "returned_model": getattr(response, "model", None) if response else None,
            "endpoint": "chat.completions",
            "sdk_version": importlib.metadata.version("openai"),
            "system_fingerprint": (
                getattr(response, "system_fingerprint", None) if response else None
            ),
            "attempt": attempt,
            "retry_count": attempt - 1,
            "config_sha256": self._text_hash(
                json.dumps(config, sort_keys=True, separators=(",", ":"))
            ),
            "parameters": {"max_tokens": max_tokens},
            "prompt_system_sha256": self._text_hash(prompt.get("system", "")),
            "prompt_system_chars": len(prompt.get("system", "")),
            "prompt_user_sha256": self._text_hash(prompt.get("user", "")),
            "prompt_user_chars": len(prompt.get("user", "")),
            "response_sha256": self._text_hash(raw),
            "response_chars": len(raw),
            "response_parsed": parsed is not None,
            # Metadata-only logs must not retain malformed response excerpts.
            # The full response remains available only in explicit full-content
            # mode, where it is redacted below.
            "parse_error": logged_parse_error,
            "api_error": api_error,
            "token_usage": {
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            },
        }
        if self._log_mode == "full_content":
            entry["prompt_system"] = self._redact(prompt.get("system", ""))
            entry["prompt_user"] = self._redact(prompt.get("user", ""))
            entry["response_raw"] = self._redact(raw)
            entry["response_parsed_content"] = self._redact_value(parsed)

        serialized_entry = json.dumps(entry, ensure_ascii=False) + "\n"
        pending_bytes = len(serialized_entry.encode("utf-8"))
        try:
            _assert_link_free_path(self._log_path)
            self._rotate_interaction_log(pending_bytes=pending_bytes)
            descriptor = self._open_interaction_log()
            with os.fdopen(descriptor, "a", encoding="utf-8") as fh:
                fh.write(serialized_entry)
        except OSError as exc:
            logger.warning("Could not write to interaction log: %s", exc)

    @staticmethod
    def _text_hash(value: str) -> str:
        return sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _redact(value: str) -> str:
        for pattern in _SECRET_RES:
            value = pattern.sub("[REDACTED_SECRET]", value)
        return value

    @classmethod
    def _redact_value(cls, value: Any) -> Any:
        if isinstance(value, str):
            return cls._redact(value)
        if isinstance(value, dict):
            return {
                cls._redact(key) if isinstance(key, str) else key: cls._redact_value(
                    item
                )
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [cls._redact_value(item) for item in value]
        return value

    def _open_interaction_log(self) -> int:
        """Open the log for append without following a substituted final link."""

        if not self._log_path:
            raise OSError("interaction log path is not configured")
        _assert_link_free_path(self._log_path)
        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(self._log_path, flags, 0o600)
        try:
            # Recheck after opening for platforms without O_NOFOLLOW and detect
            # a path swap before any content is written.
            _assert_link_free_path(self._log_path)
            path_info = os.stat(self._log_path, follow_symlinks=False)
            descriptor_info = os.fstat(descriptor)
            if not stat.S_ISREG(descriptor_info.st_mode):
                raise OSError("interaction log target must be a regular file")
            if not os.path.samestat(path_info, descriptor_info):
                raise OSError("interaction log target changed while opening")
            try:
                os.fchmod(descriptor, 0o600)
            except (AttributeError, OSError):
                logger.debug("Could not restrict interaction-log file permissions.")
        except BaseException:
            os.close(descriptor)
            raise
        return descriptor

    def _rotate_interaction_log(self, *, pending_bytes: int = 0) -> None:
        if not self._log_path:
            return
        _assert_link_free_path(self._log_path)
        cutoff = time.time() - (self._log_retention_days * 24 * 60 * 60)
        backup_prefix = f"{self._log_path.name}."
        for backup in self._log_path.parent.glob(f"{self._log_path.name}.*"):
            index_text = backup.name.removeprefix(backup_prefix)
            if not index_text.isdecimal():
                continue
            index = int(index_text)
            if _is_link_or_reparse_point(backup):
                backup.unlink()
                continue
            if not backup.is_file():
                continue
            if index > self._log_backups or backup.stat().st_mtime < cutoff:
                backup.unlink()
        if not self._log_path.exists():
            return
        if self._log_path.stat().st_mtime < cutoff:
            self._log_path.unlink()
            return
        current_size = self._log_path.stat().st_size
        if (
            current_size == 0
            or current_size + pending_bytes <= self._log_max_bytes
        ):
            return
        oldest = self._log_path.with_suffix(
            f"{self._log_path.suffix}.{self._log_backups}"
        )
        if oldest.exists():
            oldest.unlink()
        for index in range(self._log_backups - 1, 0, -1):
            source = self._log_path.with_suffix(f"{self._log_path.suffix}.{index}")
            target = self._log_path.with_suffix(f"{self._log_path.suffix}.{index + 1}")
            if source.exists():
                source.replace(target)
        self._log_path.replace(
            self._log_path.with_suffix(f"{self._log_path.suffix}.1")
        )

    # ------------------------------------------------------------------
    # JSON parsing
    # ------------------------------------------------------------------

    def _parse_json(self, text: str, *, label: str = "") -> dict[str, Any]:
        """Strip markdown fences and parse JSON.

        Falls back to brace-extraction when the model prefixes the JSON block
        with prose (e.g. "I will begin the evaluation...\n{...}").
        """
        # 1. Strip markdown code fences (```json … ```)
        #    Only remove the single opening fence at the very start and the single
        #    closing fence at the very end — MULTILINE must NOT be used here because
        #    it would cause ^ and $ to match interior line boundaries and corrupt any
        #    JSON string value that happens to start with ```.
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        # 2. Try a direct parse first (fast path — covers well-behaved responses)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 3. Extract the first top-level JSON object or array from the text.
        #    This handles "I will begin...\n{ ... }" style responses.
        logger.warning(
            "[%s] Direct JSON parse failed — brace-extraction fallback. Starts with: %r",
            label, cleaned[:120],
        )
        open_char, close_char = ("{", "}")
        start = cleaned.find("{")
        array_start = cleaned.find("[")
        if array_start != -1 and (start == -1 or array_start < start):
            start = array_start
            open_char, close_char = ("[", "]")

        candidate: str | None = None
        if start != -1:
            depth = 0
            in_string = False
            escape_next = False
            for i, ch in enumerate(cleaned[start:], start=start):
                if escape_next:
                    escape_next = False
                    continue
                if ch == "\\" and in_string:
                    escape_next = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == open_char:
                    depth += 1
                elif ch == close_char:
                    depth -= 1
                    if depth == 0:
                        candidate = cleaned[start : i + 1]
                        break  # always capture; attempt parse + repair below

        if candidate is not None:
            # Direct parse of extracted candidate
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

            # Repair pass 1: remove trailing commas before } or ]
            # Repair pass 2: strip control characters illegal inside JSON strings
            repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
            repaired = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", repaired)
            try:
                result = json.loads(repaired)
                logger.warning("[%s] JSON repaired successfully.", label)
                return result
            except json.JSONDecodeError as exc:
                logger.error("[%s] JSON repair failed: %s", label, exc)

        raise ValueError(
            f"[{label}] Model returned non-JSON output: {cleaned[:300]!r}"
        )
