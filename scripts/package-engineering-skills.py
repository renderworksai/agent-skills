#!/usr/bin/env python3
"""Build and read back the V1 skills-only ZIP using existing Python and Ruby.

No third-party dependencies. The supplied canonical manifest schema is checked
with a deliberately limited evaluator covering every assertion in that schema;
unknown schema keywords fail closed. This is not a general JSON Schema engine.
"""

import argparse
import hashlib
import json
import re
import stat
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
NAME = "engineering-planning-integrity"
VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_schema(value, schema, location="$ "):
    """Evaluate the canonical schema's complete, small assertion vocabulary."""
    supported = {"$schema", "$id", "title", "description", "type", "properties",
                 "required", "additionalProperties", "const", "minLength",
                 "maxLength", "pattern", "items"}
    require(not set(schema) - supported, "Unsupported schema keywords")
    kinds = {"object": dict, "array": list, "string": str}
    if "type" in schema:
        require(schema["type"] in kinds, "Unsupported schema type")
        require(isinstance(value, kinds[schema["type"]]), location + "wrong type")
    if "const" in schema:
        require(value == schema["const"], location + "wrong constant")
    if isinstance(value, str):
        require(len(value) >= schema.get("minLength", 0), location + "too short")
        require(len(value) <= schema.get("maxLength", len(value)), location + "too long")
        if "pattern" in schema:
            require(re.search(schema["pattern"], value) is not None, location + "pattern mismatch")
    if isinstance(value, dict):
        require(set(schema.get("required", [])) <= set(value), location + "missing fields")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                check_schema(item, properties[key], location + key + ".")
            else:
                additional = schema.get("additionalProperties", True)
                require(additional is not False, location + "unexpected field: " + key)
                if isinstance(additional, dict):
                    check_schema(item, additional, location + key + ".")
    if isinstance(value, list) and "items" in schema:
        for item in value:
            check_schema(item, schema["items"], location)


def frontmatter(data):
    text = data.decode("utf-8", errors="strict")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    require(match is not None, "Missing YAML frontmatter")
    ruby = 'print JSON.generate(YAML.safe_load(STDIN.read, permitted_classes: [], permitted_symbols: [], aliases: false))'
    parsed = subprocess.run(["ruby", "-rjson", "-ryaml", "-e", ruby],
                            input=match.group(1), text=True, capture_output=True, check=True)
    metadata = json.loads(parsed.stdout)
    require(isinstance(metadata, dict), "Frontmatter must be an object")
    require(metadata.get("name") == "planning-integrity", "Wrong skill name")
    require(isinstance(metadata.get("description"), str) and metadata["description"].strip(), "Missing description")
    # V1 is intentionally self-contained and has no supporting references.
    require(not re.search(r"\]\((?!https?://|#)[^)]+\)", text), "New local reference requires packaging support")
    return metadata


def source_members(root=ROOT):
    sources = {
        "plugin.json": root / "docs/engineering-skills-v1/plugin.json",
        "skills/planning-integrity/SKILL.md": root / "skills/planning-integrity/SKILL.md",
        "LICENSE": root / "LICENSE",
        "NOTICE": root / "docs/engineering-skills-v1/NOTICE",
    }
    for source in sources.values():
        require(source.is_file() and not source.is_symlink(), "Source must be a regular file")
        require(not any(p.is_symlink() for p in source.parents), "Symlink in source path")
    return {f"{NAME}/{key}": value.read_bytes() for key, value in sources.items()}


def audit_archive(archive, expected, schema):
    require(schema.get("$id") == SCHEMA, "Wrong canonical schema identity")
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        require(len(names) == len(set(names)), "Duplicate ZIP members")
        for entry in package.infolist():
            name = entry.filename
            path = PurePosixPath(name)
            require(not path.is_absolute() and ".." not in path.parts and "\\" not in name,
                    "Unsafe ZIP member path")
            require(not entry.is_dir(), "Unexpected directory entry")
            mode = entry.external_attr >> 16
            require(stat.S_ISREG(mode), "ZIP member must be regular, never a symlink")
        require(set(names) == set(expected), "Unexpected or missing ZIP members")
        for name, data in expected.items():
            actual = package.read(name)
            require(actual == data, "Source-byte mismatch: " + name)
            actual.decode("utf-8", errors="strict")
            require(not re.search(rb"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|/Users/)", actual),
                    "Potential secret or private host path")
        manifest = json.loads(package.read(f"{NAME}/plugin.json"))
        check_schema(manifest, schema)
        require(manifest["name"] == NAME and manifest["version"] == VERSION, "Wrong package identity")
        interface = manifest["extensions"]["com.openai"]["interface"]
        require(set(manifest["extensions"]) == {"com.openai"}, "Unexpected extension")
        for key in ["displayName", "shortDescription", "longDescription", "developerName"]:
            require(isinstance(interface.get(key), str) and interface[key].strip(), "Invalid interface text")
        require(len(interface["shortDescription"]) <= 30, "Subtitle exceeds 30 characters")
        require(isinstance(interface.get("capabilities"), list) and
                all(isinstance(x, str) and x.strip() for x in interface["capabilities"]), "Invalid capabilities")
        frontmatter(package.read(f"{NAME}/skills/planning-integrity/SKILL.md"))
        require(b"Copyright (c) 2025 Addy Osmani" in package.read(f"{NAME}/LICENSE"), "Missing MIT attribution")
    return {"state": "READY_FOR_UPLOAD", "members": names,
            "sha256": hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
            "source_sha256": {key: hashlib.sha256(value).hexdigest() for key, value in expected.items()}}


def build(output, schema):
    output.mkdir(parents=True, exist_ok=True)
    expected = source_members()
    package_dir = output / NAME
    if package_dir.exists():
        require(not package_dir.is_symlink(), "Package directory is a symlink")
        present = {p.relative_to(output).as_posix() for p in package_dir.rglob("*") if p.is_file() or p.is_symlink()}
        require(present <= set(expected), "Existing package contains unrelated files")
    for name, data in expected.items():
        target = output / name
        require(not target.is_symlink(), "Package target is a symlink")
        target.parent.mkdir(parents=True, exist_ok=True)
        require(not any(p.is_symlink() for p in target.parents), "Symlink in output path")
        if target.exists():
            require(target.read_bytes() == data, "Existing package differs; use a fresh output directory")
        else:
            target.write_bytes(data)
    archive = output / f"{NAME}-{VERSION}.zip"
    require(not archive.exists(), "Archive already exists; use a fresh output directory")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, data in sorted(expected.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 19, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(entry, data)
    result = audit_archive(archive, expected, schema)
    result["archive"] = str(archive.resolve())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    args = parser.parse_args()
    schema_bytes = args.schema.read_bytes()
    result = build(args.out.resolve(), json.loads(schema_bytes))
    result["schema_sha256"] = hashlib.sha256(schema_bytes).hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
