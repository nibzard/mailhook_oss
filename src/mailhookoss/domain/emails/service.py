"""Email domain service for email business logic."""

from datetime import datetime

from mailhookoss.domain.emails.entities import Email
from mailhookoss.domain.emails.parser import EmailParserService
from mailhookoss.domain.emails.value_objects import EmailAddress, EmailDirection
from mailhookoss.utils.id_generator import generate_email_id


class EmailService:
    """Domain service for email operations."""

    @staticmethod
    def create_email_from_raw(
        raw_email: bytes,
        tenant_id: str,
        mailbox_id: str,
        direction: EmailDirection = EmailDirection.INBOUND,
        thread_id: str | None = None,
    ) -> tuple[Email, list[tuple[str, str, bytes]]]:
        """Create Email entity from raw email bytes.

        Args:
            raw_email: Raw email bytes (RFC 822 format)
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            direction: Email direction (inbound/outbound)
            thread_id: Optional thread ID

        Returns:
            Tuple of (Email entity, list of (attachment_id, filename, bytes))
        """
        # Parse the email
        parsed = EmailParserService.parse_full_email(raw_email, tenant_id)

        # Generate email ID
        email_id = generate_email_id()

        # Extract attachment data separately
        attachment_files: list[tuple[str, str, bytes]] = []
        attachment_objects = []
        for att, att_bytes in parsed["attachments"]:
            attachment_files.append((att.id, att.filename, att_bytes))
            attachment_objects.append(att)

        # Determine received_at timestamp
        received_at = datetime.utcnow()
        if parsed["date"]:
            try:
                from email.utils import parsedate_to_datetime

                received_at = parsedate_to_datetime(parsed["date"])
            except Exception:
                # If parsing fails, use current time
                pass

        # Create Email entity
        email_entity = Email(
            id=email_id,
            tenant_id=tenant_id,
            mailbox_id=mailbox_id,
            thread_id=thread_id,
            message_id=parsed["message_id"],
            from_addr=parsed["from_addr"],
            to_addrs=parsed["to_addrs"],
            cc_addrs=parsed["cc_addrs"],
            reply_to_addrs=parsed["reply_to_addrs"],
            subject=parsed["subject"],
            text_body=parsed["text_body"],
            html_body=parsed["html_body"],
            original_text=parsed["text_body"],  # Store original
            original_html=parsed["html_body"],  # Store original
            headers=parsed["headers"],
            attachments=attachment_objects,
            verdicts=parsed["verdicts"],
            direction=direction,
            in_reply_to=parsed["in_reply_to"],
            references=parsed["references"],
            received_at=received_at,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return email_entity, attachment_files

    @staticmethod
    def should_filter_email(
        email: Email,
        allow_list: list[str],
        deny_list: list[str],
    ) -> tuple[bool, str | None]:
        """Check if email should be filtered based on allow/deny lists.

        Args:
            email: Email entity
            allow_list: List of allowed email patterns
            deny_list: List of denied email patterns

        Returns:
            Tuple of (should_filter, reason)
            - should_filter: True if email should be blocked/filtered
            - reason: Reason for filtering (or None if allowed)
        """
        from_addr = email.from_addr.addr.lower()

        # Check deny list first
        for pattern in deny_list:
            if EmailService._matches_pattern(from_addr, pattern.lower()):
                return True, f"Sender {from_addr} matches deny pattern {pattern}"

        # If allow list exists and is not empty, check it
        if allow_list:
            for pattern in allow_list:
                if EmailService._matches_pattern(from_addr, pattern.lower()):
                    return False, None  # Explicitly allowed
            # Not in allow list = filtered
            return True, f"Sender {from_addr} not in allow list"

        # No filter lists or email passed checks
        return False, None

    @staticmethod
    def _matches_pattern(email_addr: str, pattern: str) -> bool:
        """Check if email address matches a pattern.

        Supports:
        - Exact match: user@example.com
        - Domain wildcard: *@example.com
        - User wildcard: user@*

        Args:
            email_addr: Email address to check
            pattern: Pattern to match against

        Returns:
            True if email matches pattern
        """
        if pattern == email_addr:
            return True

        if pattern.startswith("*@"):
            # Domain wildcard
            domain = pattern[2:]
            return email_addr.endswith(f"@{domain}")

        if pattern.endswith("@*"):
            # User wildcard
            user = pattern[:-2]
            return email_addr.startswith(f"{user}@")

        if pattern == "*":
            # Match all
            return True

        return False

    @staticmethod
    def extract_thread_key(email: Email) -> str | None:
        """Extract thread key from email for threading.

        Uses In-Reply-To or normalized subject.

        Args:
            email: Email entity

        Returns:
            Thread key or None
        """
        # Prefer In-Reply-To for threading
        if email.in_reply_to:
            return email.in_reply_to

        # Fallback to first reference
        if email.references and len(email.references) > 0:
            return email.references[0]

        # Fallback to normalized subject
        if email.subject:
            normalized = EmailParserService.normalize_subject(email.subject)
            if normalized:
                return f"subject:{normalized}"

        return None

    @staticmethod
    def is_auto_reply(email: Email) -> bool:
        """Check if email is an auto-reply.

        Args:
            email: Email entity

        Returns:
            True if email is an auto-reply
        """
        # Check common auto-reply headers
        headers = email.headers

        # Auto-Submitted header
        auto_submitted = headers.get_header("Auto-Submitted")
        if auto_submitted and auto_submitted.lower() != "no":
            return True

        # X-Autoreply header
        x_autoreply = headers.get_header("X-Autoreply")
        if x_autoreply:
            return True

        # X-Autorespond header
        x_autorespond = headers.get_header("X-Autorespond")
        if x_autorespond:
            return True

        # Precedence: auto-reply
        precedence = headers.get_header("Precedence")
        if precedence and "auto" in precedence.lower():
            return True

        return False

    @staticmethod
    def extract_quoted_text(text_body: str) -> tuple[str, str]:
        """Extract quoted text from email body.

        Args:
            text_body: Email text body

        Returns:
            Tuple of (new_text, quoted_text)
        """
        lines = text_body.split("\n")
        new_lines = []
        quoted_lines = []
        in_quoted = False

        for line in lines:
            # Common quote markers
            if (
                line.startswith(">")
                or line.startswith("On ")
                and " wrote:" in line
                or line.strip().startswith("-----Original Message-----")
            ):
                in_quoted = True

            if in_quoted:
                quoted_lines.append(line)
            else:
                new_lines.append(line)

        return "\n".join(new_lines).strip(), "\n".join(quoted_lines).strip()

    @staticmethod
    def create_reply_email(
        original_email: Email,
        reply_from: EmailAddress,
        reply_to: list[EmailAddress],
        subject: str,
        text_body: str,
        html_body: str,
        tenant_id: str,
        mailbox_id: str,
        include_original: bool = True,
    ) -> Email:
        """Create a reply email entity.

        Args:
            original_email: Original email being replied to
            reply_from: Reply from address
            reply_to: Reply to addresses
            subject: Reply subject
            text_body: Reply text body
            html_body: Reply HTML body
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            include_original: Whether to include original message

        Returns:
            New Email entity for reply
        """
        # Generate email ID and message ID
        email_id = generate_email_id()
        message_id = f"{email_id}@mailhook.internal"

        # Build references chain
        references = original_email.references.copy() if original_email.references else []
        if original_email.message_id and original_email.message_id not in references:
            references.append(original_email.message_id)

        # Add original message if requested
        final_text_body = text_body
        final_html_body = html_body

        if include_original and original_email.text_body:
            final_text_body += f"\n\n> On {original_email.received_at}, {original_email.from_addr.addr} wrote:\n"
            for line in original_email.text_body.split("\n"):
                final_text_body += f"> {line}\n"

        # Create reply entity
        from mailhookoss.domain.emails.value_objects import EmailHeaders

        reply_email = Email(
            id=email_id,
            tenant_id=tenant_id,
            mailbox_id=mailbox_id,
            thread_id=original_email.thread_id,
            message_id=message_id,
            from_addr=reply_from,
            to_addrs=reply_to,
            cc_addrs=[],
            reply_to_addrs=[],
            subject=subject if subject.startswith("Re:") else f"Re: {subject}",
            text_body=final_text_body,
            html_body=final_html_body,
            original_text=text_body,
            original_html=html_body,
            headers=EmailHeaders(headers=[]),  # Will be filled by SMTP sender
            attachments=[],
            verdicts={},
            direction=EmailDirection.OUTBOUND,
            in_reply_to=original_email.message_id,
            references=references,
            received_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return reply_email
