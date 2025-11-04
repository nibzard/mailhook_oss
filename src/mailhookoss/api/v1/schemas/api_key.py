"""API Key API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class APIKeyInput(BaseModel):
    """Request model for creating an API key."""

    expires_at: datetime | None = Field(
        default=None,
        description="Optional expiration timestamp for the API key (RFC3339 format). "
        "Null or omitted means no expiration.",
    )
    note: str | None = Field(
        default=None,
        description="Optional note describing the purpose of this API key "
        "(can only be set on creation)",
        max_length=500,
    )


class APIKeyResponse(BaseModel):
    """Response model for API key (without secret)."""

    id: str = Field(..., description="Unique identifier for the API key")
    key_type: str = Field(
        ...,
        description="Type of API key. Tenant keys are scoped to a single tenant while "
        "internal keys can impersonate tenants when paired with the X-Mailhook-Tenant header.",
    )
    truncated_secret: str = Field(
        ...,
        description="First 12 characters of the API key secret for identification",
    )
    tenant_id: str | None = Field(
        ...,
        description="Identifier of the tenant that owns this key. Null for internal keys.",
    )
    note: str | None = Field(
        ...,
        description="Optional note describing the purpose of this API key",
    )
    expires_at: datetime | None = Field(
        ...,
        description="Expiration timestamp for the API key (RFC3339 format). "
        "Null means no expiration.",
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the API key was created (RFC3339 format)",
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class APIKeyWithSecretResponse(APIKeyResponse):
    """Response model for API key with secret (only shown when creating)."""

    secret: str = Field(
        ...,
        description="The API key secret (only shown when creating a new key). "
        "Tenant keys use the 'mhsec_' prefix while internal keys use the 'mhisec_' prefix.",
    )
