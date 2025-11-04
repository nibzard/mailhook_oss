"""Email domain entities."""

from datetime import datetime

from mailhookoss.domain.common.entity import AggregateRoot
from mailhookoss.domain.emails.value_objects import (
    Attachment,
    EmailAddress,
    EmailDirection,
    EmailHeaders,
    UserData,
)


class Email(AggregateRoot):
    """Email aggregate root."""

    def __init__(
        self,
        id: str,
        tenant_id: str,
        mailbox_id: str,
        thread_id: str,
        message_id: str,
        subject: str,
        from_addr: EmailAddress,
        to: list[EmailAddress],
        cc: list[EmailAddress],
        bcc: list[EmailAddress],
        text: str,
        html: str,
        original_text: str,
        original_html: str,
        headers: EmailHeaders,
        attachments: list[Attachment],
        labels: list[str],
        direction: EmailDirection,
        received_at: datetime,
        custom_summary: str,
        ai_summary: str,
        user_data: UserData,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        """Initialize Email entity.

        Args:
            id: Email identifier (eml_ prefix)
            tenant_id: Tenant identifier
            mailbox_id: Mailbox identifier
            thread_id: Thread identifier
            message_id: RFC Message-ID header value
            subject: Email subject
            from_addr: Sender email address
            to: List of recipient email addresses
            cc: List of CC email addresses
            bcc: List of BCC email addresses
            text: Plain text body (converted from HTML for better quality)
            html: HTML body (sanitized and UTF-8 encoded)
            original_text: Original MIME text part
            original_html: Original MIME HTML part
            headers: Raw email headers
            attachments: List of file attachments
            labels: List of labels (system and user-defined)
            direction: Email direction (inbound/outbound)
            received_at: Timestamp when email was received/sent
            custom_summary: User-managed summary text
            ai_summary: AI-generated summary text
            user_data: User-managed structured data
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._tenant_id = tenant_id
        self._mailbox_id = mailbox_id
        self._thread_id = thread_id
        self._message_id = message_id
        self._subject = subject
        self._from_addr = from_addr
        self._to = to
        self._cc = cc
        self._bcc = bcc
        self._text = text
        self._html = html
        self._original_text = original_text
        self._original_html = original_html
        self._headers = headers
        self._attachments = attachments
        self._labels = labels
        self._direction = direction
        self._received_at = received_at
        self._custom_summary = custom_summary
        self._ai_summary = ai_summary
        self._user_data = user_data

    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self._tenant_id

    @property
    def mailbox_id(self) -> str:
        """Get mailbox ID."""
        return self._mailbox_id

    @property
    def thread_id(self) -> str:
        """Get thread ID."""
        return self._thread_id

    @property
    def message_id(self) -> str:
        """Get message ID."""
        return self._message_id

    @property
    def subject(self) -> str:
        """Get subject."""
        return self._subject

    @property
    def from_addr(self) -> EmailAddress:
        """Get from address."""
        return self._from_addr

    @property
    def to(self) -> list[EmailAddress]:
        """Get to addresses."""
        return self._to.copy()

    @property
    def cc(self) -> list[EmailAddress]:
        """Get CC addresses."""
        return self._cc.copy()

    @property
    def bcc(self) -> list[EmailAddress]:
        """Get BCC addresses."""
        return self._bcc.copy()

    @property
    def text(self) -> str:
        """Get plain text body."""
        return self._text

    @property
    def html(self) -> str:
        """Get HTML body."""
        return self._html

    @property
    def original_text(self) -> str:
        """Get original text body."""
        return self._original_text

    @property
    def original_html(self) -> str:
        """Get original HTML body."""
        return self._original_html

    @property
    def headers(self) -> EmailHeaders:
        """Get email headers."""
        return self._headers

    @property
    def attachments(self) -> list[Attachment]:
        """Get attachments."""
        return self._attachments.copy()

    @property
    def labels(self) -> list[str]:
        """Get labels."""
        return self._labels.copy()

    @property
    def direction(self) -> EmailDirection:
        """Get direction."""
        return self._direction

    @property
    def received_at(self) -> datetime:
        """Get received timestamp."""
        return self._received_at

    @property
    def custom_summary(self) -> str:
        """Get custom summary."""
        return self._custom_summary

    @property
    def ai_summary(self) -> str:
        """Get AI summary."""
        return self._ai_summary

    @property
    def user_data(self) -> UserData:
        """Get user data."""
        return self._user_data

    def has_label(self, label: str) -> bool:
        """Check if email has a specific label."""
        return label in self._labels

    def add_label(self, label: str) -> None:
        """Add a label to the email."""
        if label not in self._labels:
            self._labels.append(label)
            self.touch()

    def remove_label(self, label: str) -> None:
        """Remove a label from the email."""
        if label in self._labels:
            self._labels.remove(label)
            self.touch()

    def update_custom_summary(self, summary: str) -> None:
        """Update custom summary."""
        self._custom_summary = summary
        self.touch()

    def update_user_data(self, user_data: UserData) -> None:
        """Update user data."""
        self._user_data = user_data
        self.touch()

    def is_system_label(self, label: str) -> bool:
        """Check if a label is a system label."""
        return label.startswith("$")


class Thread(AggregateRoot):
    """Thread aggregate root."""

    def __init__(
        self,
        id: str,
        tenant_id: str,
        mailbox_id: str,
        subject: str,
        participants: list[EmailAddress],
        labels: list[str],
        message_count: int,
        has_attachments: bool,
        has_hidden_messages: bool,
        first_message_at: datetime,
        last_message_at: datetime,
        custom_summary: str,
        ai_summary: str,
        user_data: UserData,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        """Initialize Thread entity.

        Args:
            id: Thread identifier (thr_ prefix)
            tenant_id: Tenant identifier
            mailbox_id: Mailbox identifier
            subject: Thread subject (from first/most relevant message)
            participants: List of all participant email addresses
            labels: List of labels aggregated from all messages
            message_count: Number of messages in thread
            has_attachments: Whether any message has attachments
            has_hidden_messages: Whether thread contains messages with hidden labels
            first_message_at: Timestamp of first message
            last_message_at: Timestamp of most recent message
            custom_summary: User-managed summary text
            ai_summary: AI-generated summary text
            user_data: User-managed structured data
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._tenant_id = tenant_id
        self._mailbox_id = mailbox_id
        self._subject = subject
        self._participants = participants
        self._labels = labels
        self._message_count = message_count
        self._has_attachments = has_attachments
        self._has_hidden_messages = has_hidden_messages
        self._first_message_at = first_message_at
        self._last_message_at = last_message_at
        self._custom_summary = custom_summary
        self._ai_summary = ai_summary
        self._user_data = user_data

    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self._tenant_id

    @property
    def mailbox_id(self) -> str:
        """Get mailbox ID."""
        return self._mailbox_id

    @property
    def subject(self) -> str:
        """Get subject."""
        return self._subject

    @property
    def participants(self) -> list[EmailAddress]:
        """Get participants."""
        return self._participants.copy()

    @property
    def labels(self) -> list[str]:
        """Get labels."""
        return self._labels.copy()

    @property
    def message_count(self) -> int:
        """Get message count."""
        return self._message_count

    @property
    def has_attachments(self) -> bool:
        """Check if thread has attachments."""
        return self._has_attachments

    @property
    def has_hidden_messages(self) -> bool:
        """Check if thread has hidden messages."""
        return self._has_hidden_messages

    @property
    def first_message_at(self) -> datetime:
        """Get first message timestamp."""
        return self._first_message_at

    @property
    def last_message_at(self) -> datetime:
        """Get last message timestamp."""
        return self._last_message_at

    @property
    def custom_summary(self) -> str:
        """Get custom summary."""
        return self._custom_summary

    @property
    def ai_summary(self) -> str:
        """Get AI summary."""
        return self._ai_summary

    @property
    def user_data(self) -> UserData:
        """Get user data."""
        return self._user_data

    def add_label(self, label: str) -> None:
        """Add a label to the thread."""
        if label not in self._labels:
            self._labels.append(label)
            self.touch()

    def remove_label(self, label: str) -> None:
        """Remove a label from the thread."""
        if label in self._labels:
            self._labels.remove(label)
            self.touch()

    def update_custom_summary(self, summary: str) -> None:
        """Update custom summary."""
        self._custom_summary = summary
        self.touch()

    def update_user_data(self, user_data: UserData) -> None:
        """Update user data."""
        self._user_data = user_data
        self.touch()

    def is_system_label(self, label: str) -> bool:
        """Check if a label is a system label."""
        return label.startswith("$")
