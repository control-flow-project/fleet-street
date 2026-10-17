import json
import os
import stat
from pathlib import Path


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def invalid_constant(value: str) -> object:
    raise ValueError(f"Non-finite JSON value: {value}")


def canonical(path: Path) -> Path:
    absolute = Path(os.path.abspath(path))
    if absolute.resolve() != absolute:
        raise ValueError("Paths must not traverse symbolic links")
    return absolute


def read_json(path: Path) -> object:
    source = canonical(path)
    if not stat.S_ISREG(source.lstat().st_mode):
        raise ValueError("Input must be a regular file")
    with source.open("rb") as stream:
        content = stream.read(1024 * 1024 + 1)
    if len(content) > 1024 * 1024:
        raise ValueError("Structured example input exceeds 1 MiB")
    return json.loads(content.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=invalid_constant)


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n"


def write_new(path: Path, content: str) -> None:
    target = canonical(path)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
    except BaseException:
        target.unlink(missing_ok=True)
        raise
