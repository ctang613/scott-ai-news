#!/usr/bin/env python3
"""Validate data.json against schema/digest.schema.json.

Uses the stdlib only. Exits 0 when the 2026-10-05 digest is well formed:
mustKnow, tech, and skills each have exactly five items.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data.json"
SCHEMA_PATH = ROOT / "schema" / "digest.schema.json"

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ITEM_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
HTTPS_URL = re.compile(r"^https://\S+$")
SECTIONS = ("mustKnow", "tech", "skills")
REQUIRED_ROOT = ("edition", "asOf", "title", "weekday", "intro", *SECTIONS)
REQUIRED_ITEM = ("id", "title", "summary", "source", "url", "published")
EDITION = "2026-10-05"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> object:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def expect_object(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        fail(f"{label} must be a JSON object")
    return value


def expect_nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def check_item(item: object, label: str, seen_ids: set[str]) -> None:
    body = expect_object(item, label)
    extra = set(body) - set(REQUIRED_ITEM)
    if extra:
        fail(f"{label} has unknown fields: {', '.join(sorted(extra))}")
    missing = [key for key in REQUIRED_ITEM if key not in body]
    if missing:
        fail(f"{label} missing fields: {', '.join(missing)}")

    item_id = expect_nonempty_string(body["id"], f"{label}.id")
    if not ITEM_ID.fullmatch(item_id):
        fail(f"{label}.id must match {ITEM_ID.pattern}")
    if item_id in seen_ids:
        fail(f"duplicate id {item_id}")
    seen_ids.add(item_id)

    expect_nonempty_string(body["title"], f"{label}.title")
    expect_nonempty_string(body["summary"], f"{label}.summary")
    expect_nonempty_string(body["source"], f"{label}.source")

    url = expect_nonempty_string(body["url"], f"{label}.url")
    if not HTTPS_URL.fullmatch(url):
        fail(f"{label}.url must be an https URL")

    published = expect_nonempty_string(body["published"], f"{label}.published")
    if not DATE.fullmatch(published):
        fail(f"{label}.published must be YYYY-MM-DD")


def check_data(data: object) -> None:
    root = expect_object(data, "data.json")
    extra = set(root) - set(REQUIRED_ROOT)
    if extra:
        fail(f"data.json has unknown fields: {', '.join(sorted(extra))}")
    missing = [key for key in REQUIRED_ROOT if key not in root]
    if missing:
        fail(f"data.json missing fields: {', '.join(missing)}")

    edition = expect_nonempty_string(root["edition"], "edition")
    as_of = expect_nonempty_string(root["asOf"], "asOf")
    if not DATE.fullmatch(edition):
        fail("edition must be YYYY-MM-DD")
    if not DATE.fullmatch(as_of):
        fail("asOf must be YYYY-MM-DD")
    if edition != EDITION or as_of != EDITION:
        fail(f"edition and asOf must both be {EDITION}")

    expect_nonempty_string(root["title"], "title")
    expect_nonempty_string(root["weekday"], "weekday")
    expect_nonempty_string(root["intro"], "intro")

    seen_ids: set[str] = set()
    for name in SECTIONS:
        section = root[name]
        if not isinstance(section, list):
            fail(f"{name} must be an array")
        if len(section) != 5:
            fail(f"{name} must contain exactly 5 items, found {len(section)}")
        for index, item in enumerate(section, start=1):
            check_item(item, f"{name}[{index}]", seen_ids)


def check_schema_file(schema: object) -> None:
    body = expect_object(schema, "schema")
    if body.get("type") != "object":
        fail("schema root type must be object")
    required = body.get("required")
    if not isinstance(required, list) or tuple(required) != REQUIRED_ROOT:
        fail("schema required fields must match data.json")
    section = body.get("$defs", {}).get("section", {})
    if section.get("minItems") != 5 or section.get("maxItems") != 5:
        fail("schema sections must require exactly 5 items")


def main() -> None:
    data = load_json(DATA_PATH)
    schema = load_json(SCHEMA_PATH)
    check_schema_file(schema)
    check_data(data)
    print(
        f"ok: {DATA_PATH.relative_to(ROOT)} edition {EDITION} "
        f"({', '.join(f'{name}=5' for name in SECTIONS)})"
    )


if __name__ == "__main__":
    main()
