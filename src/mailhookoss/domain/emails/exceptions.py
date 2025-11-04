"""Email domain exceptions."""


class EmailNotFoundError(Exception):
    """Raised when email is not found."""

    def __init__(self, email_id: str) -> None:
        """Initialize exception."""
        super().__init__(f"Email not found: {email_id}")
        self.email_id = email_id


class ThreadNotFoundError(Exception):
    """Raised when thread is not found."""

    def __init__(self, thread_id: str) -> None:
        """Initialize exception."""
        super().__init__(f"Thread not found: {thread_id}")
        self.thread_id = thread_id


class AttachmentNotFoundError(Exception):
    """Raised when attachment is not found."""

    def __init__(self, attachment_id: str) -> None:
        """Initialize exception."""
        super().__init__(f"Attachment not found: {attachment_id}")
        self.attachment_id = attachment_id


class InvalidEmailError(Exception):
    """Raised when email data is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize exception."""
        super().__init__(message)
