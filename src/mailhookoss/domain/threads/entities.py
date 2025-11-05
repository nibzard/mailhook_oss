"""Thread domain entities (already defined in emails/entities.py).

Note: The Thread entity is currently defined in domain/emails/entities.py
to avoid circular dependencies. This file serves as a reference point
for thread-related entity documentation.

The Thread aggregate root includes:
- id: Thread identifier
- tenant_id: Tenant ownership
- mailbox_id: Mailbox scope
- subject: Thread subject (normalized)
- participants: List of participant email addresses
- labels: Aggregated labels from all emails
- message_count: Number of emails in thread
- first_message_at: Timestamp of first email
- last_message_at: Timestamp of last email
- created_at: Thread creation timestamp
- updated_at: Last update timestamp

For the actual implementation, see:
- mailhookoss.domain.emails.entities.Thread
"""