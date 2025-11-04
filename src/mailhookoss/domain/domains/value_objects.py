"""Domain value objects."""

from enum import Enum

from mailhookoss.domain.common.value_object import ValueObject


class VerificationStatus(str, Enum):
    """Domain verification status."""

    PENDING = "pending"
    PROCESSING = "processing"
    VERIFIED = "verified"
    FAILED = "failed"


class VerificationMethod(str, Enum):
    """Domain verification method."""

    DNS = "dns"
    EMAIL = "email"
    API = "api"


class DNSRecordType(str, Enum):
    """DNS record type."""

    TXT = "TXT"
    MX = "MX"
    CNAME = "CNAME"
    A = "A"
    AAAA = "AAAA"


class DNSRecordPurpose(str, Enum):
    """DNS record purpose."""

    DOMAIN_VERIFICATION = "domain_verification"
    DKIM = "dkim"
    SPF = "spf"
    MX = "mx"
    DMARC = "dmarc"


class DNSRecord(ValueObject):
    """DNS record value object."""

    def __init__(
        self,
        record_type: DNSRecordType,
        name: str,
        value: str,
        purpose: DNSRecordPurpose,
        required: bool,
        description: str | None = None,
        priority: int | None = None,
        ttl: int = 300,
    ) -> None:
        """Initialize DNS record.

        Args:
            record_type: DNS record type
            name: DNS record name (hostname)
            value: DNS record value
            purpose: Purpose of this DNS record
            required: Whether this record is required
            description: Human-readable description
            priority: Priority (for MX records)
            ttl: Time to live in seconds
        """
        self.record_type = record_type
        self.name = name
        self.value = value
        self.purpose = purpose
        self.required = required
        self.description = description
        self.priority = priority
        self.ttl = ttl

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        result = {
            "type": self.record_type.value,
            "name": self.name,
            "value": self.value,
            "purpose": self.purpose.value,
            "required": self.required,
            "ttl": self.ttl,
        }
        if self.description:
            result["description"] = self.description
        if self.priority is not None:
            result["priority"] = self.priority
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "DNSRecord":
        """Create DNS record from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            DNSRecord instance
        """
        return cls(
            record_type=DNSRecordType(data["type"]),
            name=data["name"],
            value=data["value"],
            purpose=DNSRecordPurpose(data["purpose"]),
            required=data["required"],
            description=data.get("description"),
            priority=data.get("priority"),
            ttl=data.get("ttl", 300),
        )
