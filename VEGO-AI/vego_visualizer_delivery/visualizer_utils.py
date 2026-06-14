"""Pure matching helpers for the VEGO-AI compliance visualizer.

These helpers intentionally do not import tkinter. They protect the UI from
quietly displaying an Agent C result with the wrong model file.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


UNKNOWN_MATCH = "unknown"

_AGENTC_CASE_RE = re.compile(r"^agentC_case_([^./\\]+)\.json$", re.IGNORECASE)
_LEADING_CASE_RE = re.compile(r"^([0-9A-Za-z]+)(?:_|$)")

_CHEERS_KEYWORDS = (
    "cheers",
    "wine",
    "winery",
    "manufacturer",
    "sales staff",
    "salesstaff",
    "marketing employee",
    "marketingemployee",
    "product catalog",
)

_PARKWISE_KEYWORDS = (
    "parkwise",
    "parking",
    "parking lot",
    "vehicle",
    "permit",
    "gate",
    "garage",
    "resident",
    "visitor",
)

_UCD_MARKERS = (
    "ucd",
    "uc",
    "ucs",
    "usecase",
    "use_case",
    "use-case",
    "use case",
)

_CD_MARKERS = (
    "classdiagram",
    "class_diagram",
    "class-diagram",
    "class diagram",
    "cd",
)


def extract_case_id_from_filename(path_or_name: str | os.PathLike[str] | None) -> str | None:
    """Return the pipeline case id from a model-like filename.

    The project convention is the substring before the first underscore. A
    leading alphanumeric token is accepted so filenames such as
    ``70229_._ex1...`` still map to case ``70229``.
    """

    if not path_or_name:
        return None
    stem = Path(str(path_or_name)).name
    if not stem:
        return None
    stem = Path(stem).stem.strip()
    if not stem:
        return None
    first_token = stem.split("_", 1)[0].strip()
    if first_token:
        match = _LEADING_CASE_RE.match(first_token)
        if match:
            return match.group(1)
    match = _LEADING_CASE_RE.match(stem)
    return match.group(1) if match else None


def extract_case_id_from_agentc_filename(path_or_name: str | os.PathLike[str] | None) -> str | None:
    """Return the case id from an ``agentC_case_<case_id>.json`` filename."""

    if not path_or_name:
        return None
    name = Path(str(path_or_name)).name.strip()
    match = _AGENTC_CASE_RE.match(name)
    return match.group(1) if match else None


def extract_case_id_from_json(data: Any) -> str | None:
    """Return a case id from Agent output JSON if present."""

    if not isinstance(data, dict):
        return None
    for key in ("case_id", "caseId", "case"):
        value = data.get(key)
        if value not in (None, ""):
            return str(value).strip()
    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        for key in ("case_id", "caseId", "case"):
            value = metadata.get(key)
            if value not in (None, ""):
                return str(value).strip()
    return None


def detect_model_result_match(
    model_path: str | os.PathLike[str] | None,
    result_path: str | os.PathLike[str] | None,
    result_json: Any | None = None,
) -> dict[str, Any]:
    """Detect whether a model file and Agent C result belong together."""

    model_case_id = extract_case_id_from_filename(model_path)
    result_case_id = (
        extract_case_id_from_json(result_json)
        or extract_case_id_from_agentc_filename(result_path)
        or extract_case_id_from_filename(result_path)
    )
    model_domain = infer_domain(model_path, None, model_case_id)
    result_domain = infer_domain(result_path, result_json, result_case_id)
    model_diagram = infer_diagram_type(model_path, None)
    result_diagram = infer_diagram_type(result_path, result_json)

    base = {
        "model_case_id": model_case_id,
        "result_case_id": result_case_id,
        "matched": UNKNOWN_MATCH,
        "mismatch_type": "none",
        "model_domain": model_domain,
        "result_domain": result_domain,
        "model_diagram_type": model_diagram,
        "result_diagram_type": result_diagram,
        "warning_message": "",
        "recommended_action": "",
    }

    if result_case_id and not model_path:
        return _with_warning(
            base,
            matched=False,
            mismatch_type="no_matching_model_found",
            warning=(
                f"No matching model found for result case {result_case_id}. "
                "The previous model selection has been cleared."
            ),
            action="Select the correct models folder or load a model whose filename starts with the result case id.",
        )

    if not model_case_id:
        return _with_warning(
            base,
            matched=UNKNOWN_MATCH,
            mismatch_type="missing_model_case_id",
            warning="The selected model filename does not expose a pipeline case id.",
            action="Rename/select a model file that starts with the case id followed by an underscore.",
        )

    if not result_case_id:
        return _with_warning(
            base,
            matched=UNKNOWN_MATCH,
            mismatch_type="missing_result_case_id",
            warning="The selected result does not expose a case id.",
            action="Select an Agent C result named agentC_case_<case_id>.json or containing case_id.",
        )

    if model_case_id != result_case_id:
        return _with_warning(
            base,
            matched=False,
            mismatch_type="case_id_mismatch",
            warning=f"Model case {model_case_id} does not match result case {result_case_id}.",
            action=f"Auto-load or select a model file beginning with {result_case_id}_.",
        )

    if model_domain and result_domain and model_domain != result_domain:
        return _with_warning(
            base,
            matched=False,
            mismatch_type="possible_domain_mismatch",
            warning=(
                f"Case ids match ({result_case_id}), but model domain appears to be "
                f"{model_domain} while result domain appears to be {result_domain}."
            ),
            action="Verify the model/result source folders before interpreting the assessment.",
        )

    if model_diagram and result_diagram and model_diagram != result_diagram:
        return _with_warning(
            base,
            matched=False,
            mismatch_type="possible_diagram_mismatch",
            warning=(
                f"Case ids match ({result_case_id}), but model diagram appears to be "
                f"{model_diagram} while result diagram appears to be {result_diagram}."
            ),
            action="Load the model for the same diagram type as the Agent C result.",
        )

    base.update(
        {
            "matched": True,
            "mismatch_type": "none",
            "warning_message": f"Matched model/result for case {result_case_id}.",
            "recommended_action": "Proceed with review.",
        }
    )
    return base


def find_matching_model_for_result(
    models_dir: str | os.PathLike[str] | None,
    result_case_id: str | None,
    extensions: tuple[str, ...] = (".txt", ".puml"),
) -> str | None:
    """Find a model whose filename starts with ``<case_id>_``."""

    if not models_dir or not result_case_id:
        return None
    root = Path(models_dir)
    if not root.exists() or not root.is_dir():
        return None
    prefix = f"{result_case_id}_".lower()
    matches = []
    for candidate in root.iterdir():
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() not in extensions:
            continue
        if candidate.name.lower().startswith(prefix):
            matches.append(candidate)
    return str(sorted(matches, key=lambda p: p.name.lower())[0]) if matches else None


def infer_domain(
    path_or_name: str | os.PathLike[str] | None = None,
    data: Any | None = None,
    case_id: str | None = None,
) -> str | None:
    """Infer the likely case domain from ids, filenames, folders, and JSON text."""

    text = _combined_text(path_or_name, data)
    lower = text.lower()
    if _contains_any(lower, _CHEERS_KEYWORDS):
        return "Cheers"
    if _contains_any(lower, _PARKWISE_KEYWORDS):
        return "ParkWise"
    if case_id:
        cid = str(case_id)
        if cid.startswith("68"):
            return "Cheers"
        if cid.startswith("70"):
            return "ParkWise"
    return None


def infer_diagram_type(path_or_name: str | os.PathLike[str] | None = None, data: Any | None = None) -> str | None:
    """Infer UCD/CD from filenames, folders, common result fields, or JSON text."""

    explicit = _first_string_field(
        data,
        (
            "diagram_type",
            "diagramType",
            "model_type",
            "modelType",
            "assessment_type",
            "assessmentType",
            "uml_type",
            "umlType",
        ),
    )
    candidates = [explicit, _combined_text(path_or_name, data)]
    for value in candidates:
        if not value:
            continue
        lower = _normalize_marker_text(str(value))
        if _contains_marker(lower, _UCD_MARKERS):
            return "UCD"
        if _contains_marker(lower, _CD_MARKERS):
            return "CD"
    return None


def _with_warning(
    base: dict[str, Any],
    *,
    matched: bool | str,
    mismatch_type: str,
    warning: str,
    action: str,
) -> dict[str, Any]:
    updated = dict(base)
    updated.update(
        {
            "matched": matched,
            "mismatch_type": mismatch_type,
            "warning_message": warning,
            "recommended_action": action,
        }
    )
    return updated


def _combined_text(path_or_name: str | os.PathLike[str] | None, data: Any | None) -> str:
    pieces: list[str] = []
    if path_or_name:
        pieces.extend(Path(str(path_or_name)).parts)
    if data is not None:
        try:
            pieces.append(json.dumps(data, ensure_ascii=False, sort_keys=True))
        except TypeError:
            pieces.append(str(data))
    return " ".join(pieces)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    tokens = set(re.split(r"[^a-z0-9]+", text))
    for marker in markers:
        normalized = _normalize_marker_text(marker)
        if len(normalized) <= 3:
            if normalized in tokens:
                return True
            continue
        if normalized in tokens or normalized in text:
            return True
    return False


def _normalize_marker_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _first_string_field(data: Any, keys: tuple[str, ...]) -> str | None:
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        for key in keys:
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None
