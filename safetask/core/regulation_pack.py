import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


LEGACY_ENTRY_FIELDS = {"code", "title", "summary", "keywords"}
PACK_FIELDS = {
    "id",
    "domain",
    "jurisdiction",
    "issuing_authority",
    "source_policy",
    "source_review_model",
    "official_source_domains",
    "default_language",
    "supported_languages",
    "source_url",
    "review_status",
    "entries",
}
APPROVED_CONFIDENCE = "reviewed_operational_interpretation"
OFFICIAL_SOURCE_POLICY = "official_public_sources_only"
OPERATIONAL_REVIEW_MODEL = "official_source_plus_reviewed_operational_interpretation"
PLACEHOLDER_VALUES = {"", "TBD", "TODO", "REPLACE_ME"}
ENTRY_FIELDS = {
    "citation",
    "title",
    "topic_tags",
    "source_language",
    "source_url",
    "source_text",
    "literal_translation",
    "operational_interpretation",
    "authority_lanes",
    "confidence",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_entries(payload: Any) -> list[dict[str, Any]]:
    entries = payload if isinstance(payload, list) else payload.get("entries", [])
    normalized = []

    for entry in entries:
        normalized.append(
            {
                **entry,
                "code": entry.get("code") or entry.get("citation") or "Uncoded Source",
                "title": entry.get("title") or entry.get("citation") or "Untitled Source",
                "summary": entry.get("summary")
                or _first_text(entry.get("operational_interpretation"))
                or _first_text(entry.get("literal_translation"))
                or entry.get("source_text", ""),
                "keywords": entry.get("keywords") or entry.get("topic_tags") or [],
            }
        )

    return normalized


def validate_pack(payload: Any) -> list[str]:
    if isinstance(payload, list):
        return _validate_legacy_entries(payload)

    if not isinstance(payload, dict):
        return ["Regulation pack must be a JSON object or legacy entry array."]

    errors = _missing_field_errors(payload, PACK_FIELDS, "pack")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("pack.entries must be a non-empty array.")
        return errors

    for index, entry in enumerate(entries):
        errors.extend(_validate_pack_entry(entry, index))

    return errors


def validate_approved_pack(payload: Any) -> list[str]:
    errors = validate_pack(payload)
    if errors:
        return errors

    if isinstance(payload, list):
        return ["Legacy regulation arrays cannot be approved packs. Use the regulation pack object schema."]

    if payload.get("review_status") != "approved":
        errors.append("pack.review_status must be approved for operator-facing use.")

    if payload.get("source_policy") != OFFICIAL_SOURCE_POLICY:
        errors.append(f"pack.source_policy must be {OFFICIAL_SOURCE_POLICY}.")

    if payload.get("source_review_model") != OPERATIONAL_REVIEW_MODEL:
        errors.append(f"pack.source_review_model must be {OPERATIONAL_REVIEW_MODEL}.")

    if _is_placeholder(payload.get("source_url")):
        errors.append("pack.source_url must point to an official public source before approval.")

    official_domains = payload.get("official_source_domains", [])
    if not isinstance(official_domains, list) or not official_domains:
        errors.append("pack.official_source_domains must list allowed official source domains.")
        official_domains = []
    elif not _is_allowed_source_url(payload.get("source_url", ""), official_domains):
        errors.append("pack.source_url must match an allowed official source domain.")

    for index, entry in enumerate(payload["entries"]):
        errors.extend(_validate_approved_entry(entry, index, official_domains))

    return errors


def _validate_legacy_entries(entries: list[Any]) -> list[str]:
    errors = []
    if not entries:
        return ["Legacy regulation array must contain at least one entry."]

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"legacy entry {index} must be an object.")
            continue
        errors.extend(_missing_field_errors(entry, LEGACY_ENTRY_FIELDS, f"legacy entry {index}"))
        if "keywords" in entry and not isinstance(entry["keywords"], list):
            errors.append(f"legacy entry {index}.keywords must be an array.")

    return errors


def _validate_pack_entry(entry: Any, index: int) -> list[str]:
    if not isinstance(entry, dict):
        return [f"entry {index} must be an object."]

    errors = _missing_field_errors(entry, ENTRY_FIELDS, f"entry {index}")
    if "topic_tags" in entry and not isinstance(entry["topic_tags"], list):
        errors.append(f"entry {index}.topic_tags must be an array.")
    if "authority_lanes" in entry and not isinstance(entry["authority_lanes"], list):
        errors.append(f"entry {index}.authority_lanes must be an array.")
    if "literal_translation" in entry and not isinstance(entry["literal_translation"], dict):
        errors.append(f"entry {index}.literal_translation must be an object.")
    if "operational_interpretation" in entry and not isinstance(entry["operational_interpretation"], dict):
        errors.append(f"entry {index}.operational_interpretation must be an object.")

    return errors


def _validate_approved_entry(
    entry: dict[str, Any], index: int, official_domains: list[str]
) -> list[str]:
    errors = []
    for field in ["source_url", "source_text", "translation_reviewed_by", "interpretation_reviewed_by"]:
        if _is_placeholder(entry.get(field)):
            errors.append(f"entry {index}.{field} must be completed before approval.")

    if not _is_allowed_source_url(entry.get("source_url", ""), official_domains):
        errors.append(f"entry {index}.source_url must match an allowed official source domain.")

    if entry.get("confidence") != APPROVED_CONFIDENCE:
        errors.append(f"entry {index}.confidence must be {APPROVED_CONFIDENCE}.")

    for language, text in entry.get("literal_translation", {}).items():
        if _is_placeholder(text):
            errors.append(f"entry {index}.literal_translation.{language} must be completed before approval.")

    for language, text in entry.get("operational_interpretation", {}).items():
        if _is_placeholder(text):
            errors.append(
                f"entry {index}.operational_interpretation.{language} must be completed before approval."
            )

    return errors


def _missing_field_errors(data: dict[str, Any], fields: set[str], label: str) -> list[str]:
    return [f"{label}.{field} is required." for field in sorted(fields) if field not in data]


def _first_text(text_map: Any) -> str:
    if isinstance(text_map, dict):
        for value in text_map.values():
            if isinstance(value, str) and value:
                return value
    return ""


def _is_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return value is None
    stripped = value.strip()
    return stripped in PLACEHOLDER_VALUES or stripped.startswith("TBD ")


def _is_allowed_source_url(source_url: str, official_domains: list[str]) -> bool:
    if _is_placeholder(source_url):
        return False

    parsed = urlparse(source_url)
    hostname = parsed.hostname or ""
    if parsed.scheme not in {"http", "https"} or not hostname:
        return False

    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in official_domains)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a SafeTask regulation pack JSON file.")
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--approved",
        action="store_true",
        help="Require reviewed operational interpretation fields for operator-facing use.",
    )
    args = parser.parse_args()

    payload = load_json(args.path)
    errors = validate_approved_pack(payload) if args.approved else validate_pack(payload)
    if errors:
        print(f"Invalid regulation pack: {args.path}")
        for error in errors:
            print(f"- {error}")
        return 1

    entries = normalize_entries(payload)
    print(f"Valid regulation pack: {args.path} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
