"""ID generation utilities using ULID."""

from ulid import ULID


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with optional prefix.

    Args:
        prefix: Optional prefix for the ID (e.g., 'tn' for tenant)

    Returns:
        A unique ID string, optionally prefixed

    Examples:
        >>> generate_id("tn")
        'tn_01HQ5KXJ8Z8N9M2K5D6P7R3S4T'
        >>> generate_id()
        '01HQ5KXJ8Z8N9M2K5D6P7R3S4T'
    """
    ulid = str(ULID())
    return f"{prefix}_{ulid}" if prefix else ulid


def generate_tenant_id() -> str:
    """Generate a tenant ID."""
    return generate_id("tn")


def generate_domain_id() -> str:
    """Generate a domain ID."""
    return generate_id("dom")


def generate_mailbox_id() -> str:
    """Generate a mailbox ID."""
    return generate_id("mb")


def generate_email_id() -> str:
    """Generate an email ID."""
    return generate_id("eml")


def generate_attachment_id() -> str:
    """Generate an attachment ID."""
    return generate_id("att")


def generate_thread_id() -> str:
    """Generate a thread ID."""
    return generate_id("thr")


def generate_webhook_id() -> str:
    """Generate a webhook ID."""
    return generate_id("wh")


def generate_webhook_delivery_id() -> str:
    """Generate a webhook delivery ID."""
    return generate_id("whd")


def generate_api_key_id() -> str:
    """Generate an API key ID."""
    return generate_id("key")


def generate_api_key_secret(is_internal: bool = False) -> str:
    """
    Generate an API key secret.

    Args:
        is_internal: Whether this is an internal key

    Returns:
        API key secret with appropriate prefix
    """
    prefix = "mhisec" if is_internal else "mhsec"
    return generate_id(prefix)


def generate_webhook_secret() -> str:
    """Generate a webhook secret."""
    return generate_id("whsec")
