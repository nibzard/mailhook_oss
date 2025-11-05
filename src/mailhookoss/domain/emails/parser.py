"""Email parser service for MIME message parsing."""

import email
import re
from collections.abc import Iterator
from email.message import Message
from email.policy import default as default_policy
from typing import Any

from mailhookoss.domain.emails.value_objects import Attachment, EmailAddress, EmailHeaders
from mailhookoss.utils.id_generator import generate_attachment_id


class EmailParserService:
    """Service for parsing MIME email messages."""

    @staticmethod
    def parse_email_from_bytes(raw_email: bytes) -> Message:
        """Parse raw email bytes into email.Message object.

        Args:
            raw_email: Raw email bytes (RFC 822 format)

        Returns:
            Parsed email Message object
        """
        return email.message_from_bytes(raw_email, policy=default_policy)

    @staticmethod
    def parse_email_from_string(raw_email: str) -> Message:
        """Parse raw email string into email.Message object.

        Args:
            raw_email: Raw email string (RFC 822 format)

        Returns:
            Parsed email Message object
        """
        return email.message_from_string(raw_email, policy=default_policy)

    @staticmethod
    def extract_headers(message: Message) -> EmailHeaders:
        """Extract all headers from email message.

        Args:
            message: Email message

        Returns:
            EmailHeaders value object with all headers
        """
        headers: list[tuple[str, str]] = []
        for key, value in message.items():
            if value:
                headers.append((key, str(value)))
        return EmailHeaders(headers=headers)

    @staticmethod
    def extract_message_id(message: Message) -> str:
        """Extract Message-ID header.

        Args:
            message: Email message

        Returns:
            Message-ID value (without angle brackets)
        """
        message_id = message.get("Message-ID", "")
        # Remove angle brackets if present
        return message_id.strip("<>")

    @staticmethod
    def extract_subject(message: Message) -> str:
        """Extract subject from email message.

        Args:
            message: Email message

        Returns:
            Subject string
        """
        return str(message.get("Subject", ""))

    @staticmethod
    def extract_from_address(message: Message) -> EmailAddress:
        """Extract From address from email message.

        Args:
            message: Email message

        Returns:
            EmailAddress value object

        Raises:
            ValueError: If From header is missing or invalid
        """
        from_header = message.get("From")
        if not from_header:
            raise ValueError("Missing From header")

        # Parse email address using email library
        from email.utils import parseaddr

        name, addr = parseaddr(str(from_header))
        if not addr:
            raise ValueError(f"Invalid From address: {from_header}")

        return EmailAddress(addr=addr, name=name)

    @staticmethod
    def extract_to_addresses(message: Message) -> list[EmailAddress]:
        """Extract To addresses from email message.

        Args:
            message: Email message

        Returns:
            List of EmailAddress value objects
        """
        from email.utils import getaddresses

        to_headers = message.get_all("To", [])
        addresses = getaddresses([str(h) for h in to_headers])
        return [EmailAddress(addr=addr, name=name) for name, addr in addresses if addr]

    @staticmethod
    def extract_cc_addresses(message: Message) -> list[EmailAddress]:
        """Extract CC addresses from email message.

        Args:
            message: Email message

        Returns:
            List of EmailAddress value objects
        """
        from email.utils import getaddresses

        cc_headers = message.get_all("Cc", [])
        addresses = getaddresses([str(h) for h in cc_headers])
        return [EmailAddress(addr=addr, name=name) for name, addr in addresses if addr]

    @staticmethod
    def extract_reply_to_addresses(message: Message) -> list[EmailAddress]:
        """Extract Reply-To addresses from email message.

        Args:
            message: Email message

        Returns:
            List of EmailAddress value objects
        """
        from email.utils import getaddresses

        reply_to_headers = message.get_all("Reply-To", [])
        addresses = getaddresses([str(h) for h in reply_to_headers])
        return [EmailAddress(addr=addr, name=name) for name, addr in addresses if addr]

    @staticmethod
    def extract_in_reply_to(message: Message) -> str | None:
        """Extract In-Reply-To header.

        Args:
            message: Email message

        Returns:
            In-Reply-To message ID (without angle brackets) or None
        """
        in_reply_to = message.get("In-Reply-To")
        if not in_reply_to:
            return None
        return str(in_reply_to).strip("<>")

    @staticmethod
    def extract_references(message: Message) -> list[str]:
        """Extract References header.

        Args:
            message: Email message

        Returns:
            List of message IDs (without angle brackets)
        """
        references = message.get("References", "")
        if not references:
            return []

        # Split by whitespace and remove angle brackets
        message_ids = []
        for ref in str(references).split():
            ref = ref.strip("<>")
            if ref:
                message_ids.append(ref)
        return message_ids

    @staticmethod
    def extract_date(message: Message) -> str | None:
        """Extract Date header.

        Args:
            message: Email message

        Returns:
            Date string or None
        """
        date = message.get("Date")
        return str(date) if date else None

    @staticmethod
    def extract_body_parts(message: Message) -> tuple[str, str]:
        """Extract text and HTML body parts from email.

        Args:
            message: Email message

        Returns:
            Tuple of (text_body, html_body)
        """
        text_body = ""
        html_body = ""

        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                try:
                    if content_type == "text/plain":
                        text_body += part.get_content()
                    elif content_type == "text/html":
                        html_body += part.get_content()
                except Exception:
                    # Skip parts that can't be decoded
                    continue
        else:
            # Single part message
            content_type = message.get_content_type()
            try:
                if content_type == "text/plain":
                    text_body = message.get_content()
                elif content_type == "text/html":
                    html_body = message.get_content()
            except Exception:
                pass

        return text_body.strip(), html_body.strip()

    @staticmethod
    def extract_attachments(message: Message, tenant_id: str) -> list[tuple[Attachment, bytes]]:
        """Extract attachments from email message.

        Args:
            message: Email message
            tenant_id: Tenant ID for generating attachment IDs

        Returns:
            List of tuples (Attachment value object, attachment bytes)
        """
        attachments: list[tuple[Attachment, bytes]] = []

        if not message.is_multipart():
            return attachments

        for part in message.walk():
            # Check if this is an attachment
            content_disposition = str(part.get("Content-Disposition", ""))
            content_type = part.get_content_type()

            # Skip text/html and text/plain parts that aren't attachments
            if content_type in ("text/plain", "text/html") and "attachment" not in content_disposition:
                continue

            # Check if it's an attachment or inline content with filename
            is_attachment = "attachment" in content_disposition or "inline" in content_disposition
            filename = part.get_filename()

            if not is_attachment and not filename:
                continue

            # Get attachment data
            try:
                attachment_data = part.get_payload(decode=True)
                if not attachment_data:
                    continue
            except Exception:
                continue

            # Generate attachment ID
            attachment_id = generate_attachment_id()

            # Get Content-ID for inline attachments
            content_id = part.get("Content-ID")
            if content_id:
                content_id = content_id.strip("<>")

            # Get charset
            charset = part.get_content_charset()

            # Create Attachment value object
            attachment = Attachment(
                id=attachment_id,
                filename=filename or "untitled",
                content_type=content_type,
                size=len(attachment_data),
                content_id=content_id,
                charset=charset,
            )

            attachments.append((attachment, attachment_data))

        return attachments

    @staticmethod
    def extract_all_recipients(message: Message) -> list[EmailAddress]:
        """Extract all recipient addresses (To, Cc, Bcc).

        Args:
            message: Email message

        Returns:
            List of unique EmailAddress value objects
        """
        recipients: list[EmailAddress] = []
        seen_addresses: set[str] = set()

        # Extract To, Cc, Bcc
        to_addrs = EmailParserService.extract_to_addresses(message)
        cc_addrs = EmailParserService.extract_cc_addresses(message)

        # Bcc is typically not in received emails, but check anyway
        from email.utils import getaddresses

        bcc_headers = message.get_all("Bcc", [])
        bcc_addrs = [EmailAddress(addr=addr, name=name) for name, addr in getaddresses([str(h) for h in bcc_headers]) if addr]

        # Combine and deduplicate
        for addr in to_addrs + cc_addrs + bcc_addrs:
            if addr.addr.lower() not in seen_addresses:
                seen_addresses.add(addr.addr.lower())
                recipients.append(addr)

        return recipients

    @staticmethod
    def normalize_subject(subject: str) -> str:
        """Normalize subject for threading (remove Re:, Fwd:, etc.).

        Args:
            subject: Email subject

        Returns:
            Normalized subject
        """
        # Remove common prefixes (Re:, Fwd:, Fw:, etc.)
        normalized = re.sub(r"^(re|fwd?|fw):\s*", "", subject, flags=re.IGNORECASE)
        # Repeat to handle multiple prefixes
        while True:
            new_normalized = re.sub(r"^(re|fwd?|fw):\s*", "", normalized, flags=re.IGNORECASE)
            if new_normalized == normalized:
                break
            normalized = new_normalized

        return normalized.strip()

    @staticmethod
    def extract_verdicts(message: Message) -> dict[str, Any]:
        """Extract email verdicts from headers (SPF, DKIM, DMARC, spam scores).

        Args:
            message: Email message

        Returns:
            Dictionary with verdict information
        """
        verdicts: dict[str, Any] = {}

        # Extract Authentication-Results header
        auth_results = message.get("Authentication-Results")
        if auth_results:
            verdicts["authentication_results"] = str(auth_results)

            # Parse SPF
            if "spf=" in str(auth_results).lower():
                match = re.search(r"spf=(\w+)", str(auth_results), re.IGNORECASE)
                if match:
                    verdicts["spf"] = match.group(1).lower()

            # Parse DKIM
            if "dkim=" in str(auth_results).lower():
                match = re.search(r"dkim=(\w+)", str(auth_results), re.IGNORECASE)
                if match:
                    verdicts["dkim"] = match.group(1).lower()

            # Parse DMARC
            if "dmarc=" in str(auth_results).lower():
                match = re.search(r"dmarc=(\w+)", str(auth_results), re.IGNORECASE)
                if match:
                    verdicts["dmarc"] = match.group(1).lower()

        # Extract spam score (X-Spam-Score, X-Spam-Level, etc.)
        spam_score = message.get("X-Spam-Score")
        if spam_score:
            try:
                verdicts["spam_score"] = float(spam_score)
            except ValueError:
                pass

        spam_level = message.get("X-Spam-Level")
        if spam_level:
            verdicts["spam_level"] = str(spam_level)

        spam_status = message.get("X-Spam-Status")
        if spam_status:
            verdicts["spam_status"] = str(spam_status)

        return verdicts

    @staticmethod
    def parse_full_email(raw_email: bytes, tenant_id: str) -> dict[str, Any]:
        """Parse a complete email and extract all components.

        Args:
            raw_email: Raw email bytes
            tenant_id: Tenant ID for generating IDs

        Returns:
            Dictionary with all parsed email components
        """
        message = EmailParserService.parse_email_from_bytes(raw_email)

        # Extract all components
        headers = EmailParserService.extract_headers(message)
        message_id = EmailParserService.extract_message_id(message)
        subject = EmailParserService.extract_subject(message)
        from_addr = EmailParserService.extract_from_address(message)
        to_addrs = EmailParserService.extract_to_addresses(message)
        cc_addrs = EmailParserService.extract_cc_addresses(message)
        reply_to_addrs = EmailParserService.extract_reply_to_addresses(message)
        in_reply_to = EmailParserService.extract_in_reply_to(message)
        references = EmailParserService.extract_references(message)
        date = EmailParserService.extract_date(message)
        text_body, html_body = EmailParserService.extract_body_parts(message)
        attachments = EmailParserService.extract_attachments(message, tenant_id)
        verdicts = EmailParserService.extract_verdicts(message)

        return {
            "headers": headers,
            "message_id": message_id,
            "subject": subject,
            "from_addr": from_addr,
            "to_addrs": to_addrs,
            "cc_addrs": cc_addrs,
            "reply_to_addrs": reply_to_addrs,
            "in_reply_to": in_reply_to,
            "references": references,
            "date": date,
            "text_body": text_body,
            "html_body": html_body,
            "attachments": attachments,  # List of (Attachment, bytes) tuples
            "verdicts": verdicts,
        }
