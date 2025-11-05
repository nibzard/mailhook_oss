"""AWS SES email provider service."""

from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import aioboto3
from botocore.exceptions import ClientError

from mailhookoss.config import Settings
from mailhookoss.domain.emails.entities import Email
from mailhookoss.domain.emails.value_objects import EmailAddress


class SESEmailService:
    """Service for sending and managing emails via AWS SES."""

    def __init__(self, settings: Settings) -> None:
        """Initialize SES email service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.session = aioboto3.Session(
            aws_access_key_id=settings.ses_access_key,
            aws_secret_access_key=settings.ses_secret_key,
            region_name=settings.ses_region,
        )

    def _get_client(self):
        """Get SES client."""
        return self.session.client("sesv2", region_name=self.settings.ses_region)

    def _build_mime_message(
        self,
        from_addr: EmailAddress,
        to_addrs: list[EmailAddress],
        subject: str,
        text_body: str | None = None,
        html_body: str | None = None,
        cc_addrs: list[EmailAddress] | None = None,
        reply_to_addrs: list[EmailAddress] | None = None,
        attachments: list[tuple[str, str, bytes]] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> MIMEMultipart:
        """Build MIME message for sending.

        Args:
            from_addr: From email address
            to_addrs: To email addresses
            subject: Email subject
            text_body: Plain text body
            html_body: HTML body
            cc_addrs: CC email addresses
            reply_to_addrs: Reply-To email addresses
            attachments: List of (filename, content_type, bytes) tuples
            custom_headers: Custom email headers

        Returns:
            MIMEMultipart message
        """
        # Create message
        msg = MIMEMultipart("mixed")

        # Set headers
        if from_addr.name:
            msg["From"] = f'"{from_addr.name}" <{from_addr.addr}>'
        else:
            msg["From"] = from_addr.addr

        msg["To"] = ", ".join([addr.addr for addr in to_addrs])

        if cc_addrs:
            msg["Cc"] = ", ".join([addr.addr for addr in cc_addrs])

        if reply_to_addrs:
            msg["Reply-To"] = ", ".join([addr.addr for addr in reply_to_addrs])

        msg["Subject"] = subject

        # Add custom headers
        if custom_headers:
            for key, value in custom_headers.items():
                msg[key] = value

        # Create body container
        if html_body:
            # Multipart alternative for text and HTML
            body_part = MIMEMultipart("alternative")

            if text_body:
                body_part.attach(MIMEText(text_body, "plain", "utf-8"))

            body_part.attach(MIMEText(html_body, "html", "utf-8"))
            msg.attach(body_part)
        elif text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))

        # Add attachments
        if attachments:
            for filename, content_type, data in attachments:
                if content_type.startswith("image/"):
                    att = MIMEImage(data)
                else:
                    att = MIMEApplication(data)

                att.add_header("Content-Disposition", "attachment", filename=filename)
                att.add_header("Content-Type", content_type)
                msg.attach(att)

        return msg

    async def send_raw_email(
        self,
        from_addr: str,
        to_addrs: list[str],
        raw_message: bytes,
        configuration_set: str | None = None,
    ) -> str:
        """Send raw email via SES.

        Args:
            from_addr: From email address
            to_addrs: List of recipient addresses
            raw_message: Raw MIME message bytes
            configuration_set: SES configuration set name

        Returns:
            Message ID

        Raises:
            Exception: If sending fails
        """
        async with self._get_client() as ses_client:
            params = {
                "FromEmailAddress": from_addr,
                "Destination": {"ToAddresses": to_addrs},
                "Content": {"Raw": {"Data": raw_message}},
            }

            if configuration_set:
                params["ConfigurationSetName"] = configuration_set

            response = await ses_client.send_email(**params)
            return response["MessageId"]

    async def send_email(
        self,
        from_addr: EmailAddress,
        to_addrs: list[EmailAddress],
        subject: str,
        text_body: str | None = None,
        html_body: str | None = None,
        cc_addrs: list[EmailAddress] | None = None,
        reply_to_addrs: list[EmailAddress] | None = None,
        attachments: list[tuple[str, str, bytes]] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> str:
        """Send email via SES.

        Args:
            from_addr: From email address
            to_addrs: To email addresses
            subject: Email subject
            text_body: Plain text body
            html_body: HTML body
            cc_addrs: CC email addresses
            reply_to_addrs: Reply-To email addresses
            attachments: List of (filename, content_type, bytes) tuples
            custom_headers: Custom email headers

        Returns:
            Message ID

        Raises:
            Exception: If sending fails
        """
        # Build MIME message
        msg = self._build_mime_message(
            from_addr=from_addr,
            to_addrs=to_addrs,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            cc_addrs=cc_addrs,
            reply_to_addrs=reply_to_addrs,
            attachments=attachments,
            custom_headers=custom_headers,
        )

        # Convert to bytes
        raw_message = msg.as_bytes()

        # Build recipient list
        recipients = [addr.addr for addr in to_addrs]
        if cc_addrs:
            recipients.extend([addr.addr for addr in cc_addrs])

        # Send via SES
        return await self.send_raw_email(
            from_addr=from_addr.addr,
            to_addrs=recipients,
            raw_message=raw_message,
            configuration_set=self.settings.ses_configuration_set,
        )

    async def send_email_from_entity(
        self,
        email: Email,
        attachments: list[tuple[str, str, bytes]] | None = None,
    ) -> str:
        """Send email from Email entity.

        Args:
            email: Email entity
            attachments: Optional list of (filename, content_type, bytes) tuples

        Returns:
            Message ID

        Raises:
            Exception: If sending fails
        """
        return await self.send_email(
            from_addr=email.from_addr,
            to_addrs=email.to_addrs,
            subject=email.subject,
            text_body=email.text_body,
            html_body=email.html_body,
            cc_addrs=email.cc_addrs,
            reply_to_addrs=email.reply_to_addrs,
            attachments=attachments,
            custom_headers={
                "Message-ID": email.message_id,
                "In-Reply-To": email.in_reply_to or "",
                "References": " ".join(email.references) if email.references else "",
            },
        )

    async def verify_domain_identity(self, domain: str) -> dict[str, Any]:
        """Verify a domain identity in SES.

        Args:
            domain: Domain name to verify

        Returns:
            Dictionary with verification tokens

        Raises:
            Exception: If verification fails
        """
        async with self._get_client() as ses_client:
            try:
                response = await ses_client.create_email_identity(EmailIdentity=domain)

                # Get DKIM tokens
                dkim_response = await ses_client.get_email_identity(EmailIdentity=domain)

                return {
                    "identity_type": response.get("IdentityType"),
                    "verified": False,
                    "dkim_tokens": dkim_response.get("DkimAttributes", {}).get("Tokens", []),
                    "verification_status": dkim_response.get("VerificationStatus"),
                }
            except ClientError as e:
                if e.response["Error"]["Code"] == "AlreadyExists":
                    # Domain already exists, get current status
                    response = await ses_client.get_email_identity(EmailIdentity=domain)
                    return {
                        "identity_type": "DOMAIN",
                        "verified": response.get("VerifiedForSendingStatus", False),
                        "dkim_tokens": response.get("DkimAttributes", {}).get("Tokens", []),
                        "verification_status": response.get("VerificationStatus"),
                    }
                raise

    async def get_domain_verification_status(self, domain: str) -> dict[str, Any]:
        """Get domain verification status.

        Args:
            domain: Domain name

        Returns:
            Dictionary with verification status

        Raises:
            Exception: If fetching status fails
        """
        async with self._get_client() as ses_client:
            response = await ses_client.get_email_identity(EmailIdentity=domain)

            return {
                "verified": response.get("VerifiedForSendingStatus", False),
                "verification_status": response.get("VerificationStatus"),
                "dkim_enabled": response.get("DkimAttributes", {}).get("Status") == "SUCCESS",
                "dkim_tokens": response.get("DkimAttributes", {}).get("Tokens", []),
            }

    async def delete_domain_identity(self, domain: str) -> None:
        """Delete a domain identity from SES.

        Args:
            domain: Domain name

        Raises:
            Exception: If deletion fails
        """
        async with self._get_client() as ses_client:
            await ses_client.delete_email_identity(EmailIdentity=domain)

    async def get_send_quota(self) -> dict[str, float]:
        """Get SES sending quota.

        Returns:
            Dictionary with send quota info (max_24_hour_send, max_send_rate, sent_last_24_hours)

        Raises:
            Exception: If fetching quota fails
        """
        async with self._get_client() as ses_client:
            response = await ses_client.get_account()

            return {
                "max_24_hour_send": response.get("SendQuota", {}).get("Max24HourSend", 0),
                "max_send_rate": response.get("SendQuota", {}).get("MaxSendRate", 0),
                "sent_last_24_hours": response.get("SendQuota", {}).get("SentLast24Hours", 0),
            }

    async def get_send_statistics(self) -> list[dict]:
        """Get SES send statistics.

        Returns:
            List of data points with send statistics

        Raises:
            Exception: If fetching statistics fails
        """
        async with self._get_client() as ses_client:
            response = await ses_client.get_account()

            # Note: SES v2 API doesn't have direct send statistics
            # This would need CloudWatch metrics for detailed stats
            return []

    async def setup_ses_receipt_rule(
        self,
        rule_name: str,
        domain: str,
        s3_bucket: str,
        s3_prefix: str,
        sns_topic_arn: str | None = None,
    ) -> dict[str, Any]:
        """Set up SES receipt rule for inbound email.

        Args:
            rule_name: Name of the receipt rule
            domain: Domain to receive emails for
            s3_bucket: S3 bucket for storing emails
            s3_prefix: S3 prefix for email objects
            sns_topic_arn: Optional SNS topic ARN for notifications

        Returns:
            Receipt rule configuration

        Raises:
            Exception: If setup fails
        """
        # Note: Receipt rules are managed via SES v1 API
        # This would need separate implementation using boto3 (not v2)
        raise NotImplementedError("Receipt rules require SES v1 API implementation")

    async def test_connection(self) -> bool:
        """Test SES connection.

        Returns:
            True if connection successful
        """
        try:
            async with self._get_client() as ses_client:
                await ses_client.get_account()
                return True
        except Exception:
            return False
