"""Email value objects."""

from dataclasses import dataclass
from enum import Enum

from mailhookoss.domain.common.value_object import ValueObject


class EmailDirection(str, Enum):
    """Email direction enumeration."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


@dataclass(frozen=True)
class EmailAddress(ValueObject):
    """Email address value object."""

    addr: str
    name: str = ""

    def __post_init__(self) -> None:
        """Validate email address."""
        if not self.addr or "@" not in self.addr:
            raise ValueError(f"Invalid email address: {self.addr}")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "addr": self.addr,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmailAddress":
        """Create from dictionary."""
        return cls(
            addr=data["addr"],
            name=data.get("name", ""),
        )


@dataclass(frozen=True)
class Attachment(ValueObject):
    """Email attachment value object."""

    id: str
    filename: str
    content_type: str
    size: int
    content_id: str | None = None
    charset: str | None = None
    custom_summary: str = ""
    ai_summary: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "filename": self.filename,
            "content_type": self.content_type,
            "size": self.size,
            "content_id": self.content_id,
            "charset": self.charset,
            "custom_summary": self.custom_summary,
            "ai_summary": self.ai_summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Attachment":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            filename=data["filename"],
            content_type=data["content_type"],
            size=data["size"],
            content_id=data.get("content_id"),
            charset=data.get("charset"),
            custom_summary=data.get("custom_summary", ""),
            ai_summary=data.get("ai_summary", ""),
        )


@dataclass(frozen=True)
class EmailHeaders(ValueObject):
    """Email headers value object (preserves order and duplicates)."""

    headers: list[tuple[str, str]]

    def to_dict(self) -> list[list[str]]:
        """Convert to list of [key, value] pairs for JSON serialization."""
        return [[k, v] for k, v in self.headers]

    @classmethod
    def from_dict(cls, data: list[list[str]]) -> "EmailHeaders":
        """Create from list of [key, value] pairs."""
        return cls(headers=[(item[0], item[1]) for item in data])

    def get_header(self, name: str) -> str | None:
        """Get first header value by name (case-insensitive)."""
        name_lower = name.lower()
        for key, value in self.headers:
            if key.lower() == name_lower:
                return value
        return None

    def get_all_headers(self, name: str) -> list[str]:
        """Get all header values by name (case-insensitive)."""
        name_lower = name.lower()
        return [value for key, value in self.headers if key.lower() == name_lower]


@dataclass(frozen=True)
class UserData(ValueObject):
    """User-managed data structure for emails and threads."""

    data: dict

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return self.data

    @classmethod
    def from_dict(cls, data: dict) -> "UserData":
        """Create from dictionary."""
        return cls(data=data)

    @classmethod
    def empty(cls) -> "UserData":
        """Create empty user data."""
        return cls(data={})
