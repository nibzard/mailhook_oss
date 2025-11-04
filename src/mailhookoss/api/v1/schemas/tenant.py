"""Tenant API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class TenantCreateRequest(BaseModel):
    """Request model for creating a tenant."""

    name: str = Field(
        ...,
        description="Human-readable tenant name",
        examples=["Acme Inc"],
        min_length=1,
        max_length=255,
    )


class TenantUpdateRequest(BaseModel):
    """Request model for updating a tenant."""

    name: str = Field(
        ...,
        description="Updated tenant name",
        examples=["Acme Corporation"],
        min_length=1,
        max_length=255,
    )


class TenantResponse(BaseModel):
    """Response model for tenant."""

    id: str = Field(..., description="Unique identifier for the tenant")
    name: str = Field(..., description="Human-readable tenant name")
    created_at: datetime = Field(..., description="Timestamp when the tenant was created")
    updated_at: datetime = Field(..., description="Timestamp when the tenant was last updated")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
