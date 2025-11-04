"""Mailbox API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class MailboxFiltersResponse(BaseModel):
    """Mailbox filters response model."""

    allow: list[str] = Field(
        ...,
        description="List of email addresses allowed to send to this mailbox (whitelist). "
        "If not empty, only these addresses can send emails.",
    )
    deny: list[str] = Field(
        ...,
        description="List of email addresses denied from sending to this mailbox (blacklist). "
        "These addresses cannot send emails.",
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class MailboxInput(BaseModel):
    """Request model for creating/updating a mailbox."""

    local_part: str = Field(
        ...,
        description="The local part of the email address (part before @)",
        examples=["support"],
        min_length=1,
        max_length=64,
    )
    active: bool = Field(
        default=True,
        description="Whether the mailbox is active (defaults to true for new mailboxes, "
        "preserves current value for updates if not specified)",
    )
    sender_name: str = Field(
        default="",
        description="Display name used when sending emails from this mailbox (empty string for new mailboxes, "
        "preserves current value for updates if not specified)",
        max_length=255,
    )
    spam_policy: str = Field(
        default="mark",
        description="Default spam handling policy for the mailbox. `mark` applies the `$junk` label "
        "when spam is detected. `delete` drops spam during receipt. When omitted, the existing policy "
        "is preserved (defaults to `mark` for new mailboxes).",
        pattern="^(mark|delete)$",
    )
    inbound_policy: str = Field(
        default="thread_trust",
        description="Inbound participant trust policy. `thread_trust` permits trusted participants on "
        "existing threads while labeling brand-new senders as `$rejected`; `permitted_only` restricts "
        "delivery to allow-listed senders and labels others as `$untrusted`. When omitted, the existing "
        "policy is preserved (defaults to `thread_trust` for new mailboxes).",
        pattern="^(thread_trust|permitted_only)$",
    )
    # Filter operations
    add_allow: list[str] = Field(
        default=[],
        description="Add these email addresses to the existing allow list",
    )
    add_deny: list[str] = Field(
        default=[],
        description="Add these email addresses to the existing deny list",
    )
    remove_allow: list[str] = Field(
        default=[],
        description="Remove these email addresses from the existing allow list",
    )
    remove_deny: list[str] = Field(
        default=[],
        description="Remove these email addresses from the existing deny list",
    )
    set_allow: list[str] | None = Field(
        default=None,
        description="Replace the entire allow list with these email addresses",
    )
    set_deny: list[str] | None = Field(
        default=None,
        description="Replace the entire deny list with these email addresses",
    )


class MailboxResponse(BaseModel):
    """Response model for mailbox."""

    id: str = Field(..., description="Unique identifier for the mailbox")
    tenant_id: str = Field(..., description="ID of the tenant that owns this mailbox")
    domain_id: str = Field(..., description="ID of the domain this mailbox belongs to")
    local_part: str = Field(..., description="The local part of the email address (part before @)")
    active: bool = Field(..., description="Whether the mailbox is active")
    sender_name: str = Field(..., description="Display name used when sending emails from this mailbox")
    spam_policy: str = Field(..., description="Default spam handling policy for inbound messages")
    inbound_policy: str = Field(..., description="Inbound participant trust policy")
    filters: MailboxFiltersResponse = Field(..., description="Email filter lists for a mailbox")
    created_at: datetime = Field(..., description="Timestamp when the mailbox was created (RFC3339 format)")
    updated_at: datetime = Field(..., description="Timestamp when the mailbox was last updated (RFC3339 format)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
