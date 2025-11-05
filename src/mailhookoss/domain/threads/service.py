"""Thread domain service for thread operations."""

from datetime import datetime

from mailhookoss.domain.emails.entities import Email, Thread
from mailhookoss.domain.emails.parser import EmailParserService
from mailhookoss.domain.threads.threading_algorithm import ThreadingAlgorithm, ThreadNode
from mailhookoss.utils.id_generator import generate_thread_id


class ThreadService:
    """Domain service for thread operations."""

    @staticmethod
    def create_thread_from_email(email: Email) -> Thread:
        """Create a new thread from a single email.

        Args:
            email: Email entity to create thread from

        Returns:
            New Thread entity
        """
        thread_id = generate_thread_id()

        # Normalize subject for threading
        normalized_subject = EmailParserService.normalize_subject(email.subject)

        # Extract participants
        participants = [email.from_addr.addr.lower()]
        for addr in email.to_addrs:
            if addr.addr.lower() not in participants:
                participants.append(addr.addr.lower())
        for addr in email.cc_addrs:
            if addr.addr.lower() not in participants:
                participants.append(addr.addr.lower())

        thread = Thread(
            id=thread_id,
            tenant_id=email.tenant_id,
            mailbox_id=email.mailbox_id,
            subject=normalized_subject,
            participants=participants,
            labels=email.labels.copy() if email.labels else [],
            message_count=1,
            first_message_at=email.received_at,
            last_message_at=email.received_at,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return thread

    @staticmethod
    def update_thread_with_email(thread: Thread, email: Email) -> Thread:
        """Update thread with a new email.

        Args:
            thread: Existing Thread entity
            email: New Email entity to add

        Returns:
            Updated Thread entity
        """
        # Update participants
        new_participants = thread.participants.copy()
        if email.from_addr.addr.lower() not in new_participants:
            new_participants.append(email.from_addr.addr.lower())
        for addr in email.to_addrs:
            if addr.addr.lower() not in new_participants:
                new_participants.append(addr.addr.lower())
        for addr in email.cc_addrs:
            if addr.addr.lower() not in new_participants:
                new_participants.append(addr.addr.lower())

        # Update labels
        new_labels = thread.labels.copy()
        if email.labels:
            for label in email.labels:
                if label not in new_labels:
                    new_labels.append(label)

        # Update timestamps
        first_message_at = thread.first_message_at
        last_message_at = thread.last_message_at

        if email.received_at < first_message_at:
            first_message_at = email.received_at
        if email.received_at > last_message_at:
            last_message_at = email.received_at

        # Create updated thread
        thread.update_metadata(
            participants=new_participants,
            labels=new_labels,
            message_count=thread.message_count + 1,
            first_message_at=first_message_at,
            last_message_at=last_message_at,
        )

        return thread

    @staticmethod
    def rebuild_thread_from_emails(thread: Thread, emails: list[Email]) -> Thread:
        """Rebuild thread metadata from a list of emails.

        Args:
            thread: Thread entity to rebuild
            emails: List of all emails in the thread

        Returns:
            Updated Thread entity with recalculated metadata
        """
        if not emails:
            return thread

        # Sort emails by received date
        sorted_emails = sorted(emails, key=lambda e: e.received_at)

        # Collect all participants
        participants: list[str] = []
        seen_participants: set[str] = set()

        for email in sorted_emails:
            addr = email.from_addr.addr.lower()
            if addr not in seen_participants:
                seen_participants.add(addr)
                participants.append(addr)

            for to_addr in email.to_addrs:
                addr = to_addr.addr.lower()
                if addr not in seen_participants:
                    seen_participants.add(addr)
                    participants.append(addr)

            for cc_addr in email.cc_addrs:
                addr = cc_addr.addr.lower()
                if addr not in seen_participants:
                    seen_participants.add(addr)
                    participants.append(addr)

        # Collect all labels
        labels: list[str] = []
        seen_labels: set[str] = set()

        for email in sorted_emails:
            if email.labels:
                for label in email.labels:
                    if label not in seen_labels:
                        seen_labels.add(label)
                        labels.append(label)

        # Update thread metadata
        thread.update_metadata(
            participants=participants,
            labels=labels,
            message_count=len(sorted_emails),
            first_message_at=sorted_emails[0].received_at,
            last_message_at=sorted_emails[-1].received_at,
        )

        return thread

    @staticmethod
    def should_merge_threads(thread1: Thread, thread2: Thread) -> bool:
        """Determine if two threads should be merged.

        Threads should be merged if they have:
        - Same normalized subject
        - Overlapping participants
        - Same mailbox

        Args:
            thread1: First thread
            thread2: Second thread

        Returns:
            True if threads should be merged
        """
        # Must be in same mailbox
        if thread1.mailbox_id != thread2.mailbox_id:
            return False

        # Must have same normalized subject
        if thread1.subject != thread2.subject:
            return False

        # Check for overlapping participants (at least 50% overlap)
        participants1 = set(thread1.participants)
        participants2 = set(thread2.participants)
        overlap = len(participants1 & participants2)
        total_unique = len(participants1 | participants2)

        if total_unique == 0:
            return False

        overlap_ratio = overlap / total_unique
        return overlap_ratio >= 0.5

    @staticmethod
    def merge_threads(primary_thread: Thread, secondary_thread: Thread) -> Thread:
        """Merge two threads into one.

        Args:
            primary_thread: Primary thread (will be kept)
            secondary_thread: Secondary thread (will be merged into primary)

        Returns:
            Updated primary Thread entity
        """
        # Merge participants
        participants = primary_thread.participants.copy()
        for p in secondary_thread.participants:
            if p not in participants:
                participants.append(p)

        # Merge labels
        labels = primary_thread.labels.copy()
        for label in secondary_thread.labels:
            if label not in labels:
                labels.append(label)

        # Update timestamps
        first_message_at = min(primary_thread.first_message_at, secondary_thread.first_message_at)
        last_message_at = max(primary_thread.last_message_at, secondary_thread.last_message_at)
        message_count = primary_thread.message_count + secondary_thread.message_count

        # Update primary thread
        primary_thread.update_metadata(
            participants=participants,
            labels=labels,
            message_count=message_count,
            first_message_at=first_message_at,
            last_message_at=last_message_at,
        )

        return primary_thread

    @staticmethod
    def find_matching_thread(
        email: Email,
        candidate_threads: list[Thread],
    ) -> Thread | None:
        """Find a matching thread for an email.

        Uses In-Reply-To, References, and subject matching.

        Args:
            email: Email entity
            candidate_threads: List of candidate threads to match against

        Returns:
            Matching Thread entity or None
        """
        # First priority: In-Reply-To match
        # (Not directly matchable without email lookup, skip for now)

        # Second priority: Subject match with recent thread
        normalized_subject = EmailParserService.normalize_subject(email.subject)

        for thread in candidate_threads:
            if thread.subject == normalized_subject:
                # Check if email is recent relative to thread
                time_diff = abs((email.received_at - thread.last_message_at).total_seconds())
                # Allow matching within 30 days
                if time_diff < 30 * 24 * 3600:
                    return thread

        return None

    @staticmethod
    def create_thread_tree(emails: list[Email]) -> list[ThreadNode]:
        """Create thread tree structure from emails.

        Args:
            emails: List of Email entities

        Returns:
            List of ThreadNode root nodes
        """
        return ThreadingAlgorithm.rebuild_thread_from_emails(emails, prune_dummies=True)

    @staticmethod
    def get_thread_summary(thread: Thread) -> dict:
        """Get a summary of thread metadata.

        Args:
            thread: Thread entity

        Returns:
            Dictionary with thread summary
        """
        return {
            "id": thread.id,
            "subject": thread.subject,
            "message_count": thread.message_count,
            "participants": thread.participants,
            "labels": thread.labels,
            "first_message_at": thread.first_message_at.isoformat(),
            "last_message_at": thread.last_message_at.isoformat(),
            "duration_days": (thread.last_message_at - thread.first_message_at).days,
        }
