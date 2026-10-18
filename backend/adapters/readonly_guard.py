"""Rejects any query that could change data. Applied before every execution."""
import re

ALLOWED_PREFIXES = ("SELECT ", "WITH ", "TAG:R,", "ALARMVIEW:SELECT ")
FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|TRUNCATE|EXEC|EXECUTE|GRANT|REVOKE|DENY|"
    r"BACKUP|RESTORE|ATTACH|DETACH|DBCC|SHUTDOWN|KILL|INTO|OPENROWSET|OPENQUERY|OPENDATASOURCE)\b"
    r"|\b(SP|XP)_\w+",
    re.IGNORECASE,
)


class ReadOnlyViolation(ValueError):
    pass


def assert_read_only(query: str) -> str:
    text = " ".join(query.split())
    if not text:
        raise ReadOnlyViolation("Empty query")
    if ";" in text.rstrip(";") or "--" in text or "/*" in text:
        raise ReadOnlyViolation("Multiple statements and comments are not allowed")
    if not text.upper().startswith(ALLOWED_PREFIXES):
        raise ReadOnlyViolation("Only SELECT, WITH, TAG:R and ALARMVIEW:SELECT are allowed")
    if FORBIDDEN.search(text):
        raise ReadOnlyViolation("Query contains a write or admin keyword")
    return text.rstrip(";")
