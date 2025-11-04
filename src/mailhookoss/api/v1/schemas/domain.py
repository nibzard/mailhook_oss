"""Domain API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class DNSRecordResponse(BaseModel):
    """DNS record response model."""

    type: str = Field(..., description="DNS record type")
    name: str = Field(..., description="DNS record name (hostname)")
    value: str = Field(..., description="DNS record value")
    purpose: str = Field(..., description="Purpose of this DNS record")
    required: bool = Field(..., description="Whether this record is required for email functionality")
    description: str | None = Field(None, description="Human-readable description of what this record does")
    priority: int | None = Field(None, description="Priority (for MX records)")
    ttl: int = Field(..., description="Time to live in seconds")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class DomainInput(BaseModel):
    """Request model for creating/updating a domain."""

    domain: str = Field(
        ...,
        description="The domain name",
        examples=["acme.dev"],
    )
    active: bool = Field(
        default=True,
        description="Whether the domain is active (defaults to true for new domains, "
        "preserves current value for updates if not specified)",
    )


class DomainResponse(BaseModel):
    """Response model for domain."""

    id: str = Field(..., description="Unique identifier for the domain")
    tenant_id: str = Field(..., description="ID of the tenant that owns this domain")
    domain: str = Field(..., description="The domain name")
    unicode_domain: str = Field(..., description="The domain name in Unicode format for display")
    active: bool = Field(..., description="Whether the domain is active")
    verification_status: str = Field(..., description="Domain verification status")
    verification_method: str | None = Field(..., description="Method used for domain verification")
    verified_at: datetime | None = Field(..., description="Timestamp when the domain was verified (RFC3339 format)")
    dns_records: list[DNSRecordResponse] = Field(
        ...,
        description="DNS records required for domain verification and email routing",
    )
    created_at: datetime = Field(..., description="Timestamp when the domain was created (RFC3339 format)")
    updated_at: datetime = Field(..., description="Timestamp when the domain was last updated (RFC3339 format)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
