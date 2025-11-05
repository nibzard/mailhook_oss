"""Email threading algorithm implementation.

This implements a simplified version of the JWZMESSAGING email threading algorithm
(https://www.jwz.org/doc/threading.html) with adaptations for mailbox-scoped threading.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from mailhookoss.domain.emails.entities import Email
from mailhookoss.domain.emails.parser import EmailParserService


@dataclass
class ThreadNode:
    """Node in the thread tree."""

    message_id: str
    email: Email | None = None
    parent: "ThreadNode | None" = None
    children: list["ThreadNode"] = field(default_factory=list)

    def add_child(self, child: "ThreadNode") -> None:
        """Add a child node."""
        if child not in self.children:
            self.children.append(child)
            child.parent = self

    def is_dummy(self) -> bool:
        """Check if this is a dummy node (no email)."""
        return self.email is None


class ThreadingAlgorithm:
    """Email threading algorithm service."""

    @staticmethod
    def build_threads(emails: Sequence[Email]) -> list[ThreadNode]:
        """Build thread trees from a list of emails.

        Args:
            emails: List of Email entities

        Returns:
            List of root ThreadNode objects (one per thread)
        """
        # Step 1: Create a message ID to node mapping
        id_table: dict[str, ThreadNode] = {}

        # Step 2: Process each email
        for email in emails:
            # Get or create node for this email
            if email.message_id in id_table:
                node = id_table[email.message_id]
                node.email = email
            else:
                node = ThreadNode(message_id=email.message_id, email=email)
                id_table[email.message_id] = node

            # Process References header (threading by References)
            references = email.references if email.references else []

            # Add In-Reply-To if not in references
            if email.in_reply_to and email.in_reply_to not in references:
                references = references + [email.in_reply_to]

            # Build parent chain
            parent_node = None
            for ref_id in references:
                # Get or create node for this reference
                if ref_id not in id_table:
                    ref_node = ThreadNode(message_id=ref_id, email=None)
                    id_table[ref_id] = ref_node
                else:
                    ref_node = id_table[ref_id]

                # Link to parent
                if parent_node is not None and ref_node.parent is None:
                    parent_node.add_child(ref_node)

                parent_node = ref_node

            # Link current email to the last reference
            if parent_node is not None and node.parent is None:
                parent_node.add_child(node)

        # Step 3: Find root nodes (nodes with no parent)
        root_nodes = [node for node in id_table.values() if node.parent is None]

        # Step 4: Group by subject for orphaned messages
        root_nodes = ThreadingAlgorithm._group_by_subject(root_nodes)

        # Step 5: Sort threads by most recent message
        root_nodes.sort(
            key=lambda n: ThreadingAlgorithm._get_latest_date(n),
            reverse=True,
        )

        return root_nodes

    @staticmethod
    def _group_by_subject(root_nodes: list[ThreadNode]) -> list[ThreadNode]:
        """Group orphaned messages by subject.

        Args:
            root_nodes: List of root nodes

        Returns:
            List of root nodes with subject grouping applied
        """
        # Map normalized subjects to root nodes
        subject_table: dict[str, ThreadNode] = {}

        for node in root_nodes:
            if node.email is None:
                continue

            # Normalize subject
            subject = EmailParserService.normalize_subject(node.email.subject)
            if not subject:
                continue

            # If we've seen this subject before, merge threads
            if subject in subject_table:
                existing_node = subject_table[subject]

                # Compare dates to determine which should be parent
                existing_date = ThreadingAlgorithm._get_latest_date(existing_node)
                new_date = ThreadingAlgorithm._get_latest_date(node)

                if new_date < existing_date:
                    # New message is older, it becomes parent
                    if node.parent is None:
                        node.add_child(existing_node)
                        subject_table[subject] = node
                else:
                    # Existing message is older, it remains parent
                    if existing_node.parent is None:
                        existing_node.add_child(node)
            else:
                subject_table[subject] = node

        # Return only root nodes (nodes with no parent)
        return [node for node in root_nodes if node.parent is None]

    @staticmethod
    def _get_latest_date(node: ThreadNode) -> float:
        """Get the latest date from a thread tree.

        Args:
            node: Root node of thread

        Returns:
            Latest timestamp in the thread
        """
        latest = 0.0

        def traverse(n: ThreadNode) -> None:
            nonlocal latest
            if n.email:
                timestamp = n.email.received_at.timestamp()
                if timestamp > latest:
                    latest = timestamp
            for child in n.children:
                traverse(child)

        traverse(node)
        return latest

    @staticmethod
    def flatten_thread(root: ThreadNode) -> list[Email]:
        """Flatten a thread tree into a list of emails.

        Args:
            root: Root node of thread

        Returns:
            List of Email entities in chronological order
        """
        emails: list[Email] = []

        def traverse(node: ThreadNode) -> None:
            if node.email:
                emails.append(node.email)
            for child in node.children:
                traverse(child)

        traverse(root)

        # Sort by received date
        emails.sort(key=lambda e: e.received_at)
        return emails

    @staticmethod
    def get_thread_participants(root: ThreadNode) -> list[str]:
        """Get all unique participants in a thread.

        Args:
            root: Root node of thread

        Returns:
            List of unique email addresses
        """
        participants: set[str] = set()

        def traverse(node: ThreadNode) -> None:
            if node.email:
                # Add sender
                participants.add(node.email.from_addr.addr.lower())

                # Add recipients
                for addr in node.email.to_addrs:
                    participants.add(addr.addr.lower())

                # Add CC
                for addr in node.email.cc_addrs:
                    participants.add(addr.addr.lower())

            for child in node.children:
                traverse(child)

        traverse(root)
        return list(participants)

    @staticmethod
    def get_thread_labels(root: ThreadNode) -> list[str]:
        """Get all unique labels from emails in a thread.

        Args:
            root: Root node of thread

        Returns:
            List of unique labels
        """
        labels: set[str] = set()

        def traverse(node: ThreadNode) -> None:
            if node.email and node.email.labels:
                labels.update(node.email.labels)
            for child in node.children:
                traverse(child)

        traverse(root)
        return list(labels)

    @staticmethod
    def find_email_in_thread(root: ThreadNode, email_id: str) -> ThreadNode | None:
        """Find a specific email in a thread tree.

        Args:
            root: Root node of thread
            email_id: Email ID to find

        Returns:
            ThreadNode containing the email or None
        """

        def traverse(node: ThreadNode) -> ThreadNode | None:
            if node.email and node.email.id == email_id:
                return node
            for child in node.children:
                result = traverse(child)
                if result:
                    return result
            return None

        return traverse(root)

    @staticmethod
    def get_thread_depth(node: ThreadNode) -> int:
        """Get the depth of a thread tree.

        Args:
            node: Root node of thread

        Returns:
            Maximum depth of the tree
        """
        if not node.children:
            return 1

        max_child_depth = max(ThreadingAlgorithm.get_thread_depth(child) for child in node.children)
        return 1 + max_child_depth

    @staticmethod
    def prune_dummy_nodes(root: ThreadNode) -> ThreadNode | None:
        """Remove dummy nodes (nodes without emails) that have only one child.

        Args:
            root: Root node of thread

        Returns:
            New root node (may be different if root was dummy)
        """
        # Prune children first
        new_children = []
        for child in root.children:
            pruned_child = ThreadingAlgorithm.prune_dummy_nodes(child)
            if pruned_child:
                new_children.append(pruned_child)
        root.children = new_children

        # If this is a dummy node with only one child, promote the child
        if root.is_dummy() and len(root.children) == 1:
            promoted = root.children[0]
            promoted.parent = root.parent
            return promoted

        # If this is a dummy node with no children, remove it
        if root.is_dummy() and len(root.children) == 0:
            return None

        return root

    @staticmethod
    def rebuild_thread_from_emails(
        emails: Sequence[Email],
        prune_dummies: bool = True,
    ) -> list[ThreadNode]:
        """Rebuild thread structure from a list of emails.

        This is a convenience method that builds threads and optionally prunes dummy nodes.

        Args:
            emails: List of Email entities
            prune_dummies: Whether to prune dummy nodes

        Returns:
            List of root ThreadNode objects
        """
        roots = ThreadingAlgorithm.build_threads(emails)

        if prune_dummies:
            pruned_roots = []
            for root in roots:
                pruned = ThreadingAlgorithm.prune_dummy_nodes(root)
                if pruned:
                    pruned_roots.append(pruned)
            return pruned_roots

        return roots
