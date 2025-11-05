"""Email search service with query language support."""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SearchOperator(str, Enum):
    """Search operators for email queries."""

    FROM = "from"
    TO = "to"
    CC = "cc"
    SUBJECT = "subject"
    BODY = "body"
    HAS = "has"
    LABEL = "label"
    BEFORE = "before"
    AFTER = "after"
    IS = "is"


class SearchModifier(str, Enum):
    """Search modifiers."""

    ATTACHMENT = "attachment"
    READ = "read"
    UNREAD = "unread"
    STARRED = "starred"


@dataclass
class SearchTerm:
    """Represents a single search term."""

    operator: SearchOperator | None
    value: str
    negated: bool = False


@dataclass
class SearchQuery:
    """Represents a parsed search query."""

    terms: list[SearchTerm]


class EmailSearchService:
    """Service for parsing and executing email search queries.

    Supported query syntax:
    - from:user@example.com - Search by sender
    - to:user@example.com - Search by recipient
    - cc:user@example.com - Search by CC
    - subject:"some text" - Search in subject (quoted for phrases)
    - body:"some text" - Search in body
    - has:attachment - Has attachments
    - label:important - Has specific label
    - before:2024-06-01 - Before date
    - after:2024-01-01 - After date
    - is:read - Read status
    - is:unread - Unread status
    - is:starred - Starred status
    - -operator:value - Negation (exclude)
    - "phrase search" - Search for exact phrase in subject/body
    """

    @staticmethod
    def parse_query(query: str) -> SearchQuery:
        """Parse search query string into SearchQuery object.

        Args:
            query: Search query string

        Returns:
            SearchQuery object with parsed terms
        """
        terms: list[SearchTerm] = []

        # Regular expression to match search terms
        # Matches: operator:value, operator:"quoted value", -operator:value, or standalone words
        pattern = r'(-)?(\w+):("(?:[^"\\]|\\.)*"|[^\s]+)|("(?:[^"\\]|\\.)*"|[^\s]+)'

        for match in re.finditer(pattern, query):
            negation = match.group(1) == "-"
            operator_str = match.group(2)
            operator_value = match.group(3)
            standalone = match.group(4)

            if operator_str and operator_value:
                # Term with operator (e.g., from:user@example.com)
                operator = EmailSearchService._parse_operator(operator_str)
                value = EmailSearchService._unquote(operator_value)
                terms.append(SearchTerm(operator=operator, value=value, negated=negation))
            elif standalone:
                # Standalone term (search in subject/body)
                value = EmailSearchService._unquote(standalone)
                terms.append(SearchTerm(operator=None, value=value, negated=negation))

        return SearchQuery(terms=terms)

    @staticmethod
    def _parse_operator(operator_str: str) -> SearchOperator | None:
        """Parse operator string to SearchOperator enum.

        Args:
            operator_str: Operator string

        Returns:
            SearchOperator or None if invalid
        """
        try:
            return SearchOperator(operator_str.lower())
        except ValueError:
            return None

    @staticmethod
    def _unquote(value: str) -> str:
        """Remove quotes from quoted string.

        Args:
            value: Potentially quoted string

        Returns:
            Unquoted string
        """
        if value.startswith('"') and value.endswith('"'):
            # Remove outer quotes and unescape inner quotes
            return value[1:-1].replace('\\"', '"')
        return value

    @staticmethod
    def _parse_date(date_str: str) -> datetime | None:
        """Parse date string to datetime.

        Supports formats: YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD

        Args:
            date_str: Date string

        Returns:
            datetime object or None if invalid
        """
        # Try different date formats
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y.%m.%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    @staticmethod
    def build_sql_filters(query: SearchQuery) -> dict:
        """Build SQL filter conditions from SearchQuery.

        Args:
            query: Parsed search query

        Returns:
            Dictionary with filter conditions for SQLAlchemy
        """
        filters = {
            "from_addrs": [],
            "to_addrs": [],
            "cc_addrs": [],
            "subjects": [],
            "body_text": [],
            "labels": [],
            "has_attachment": None,
            "before_date": None,
            "after_date": None,
            "is_read": None,
            "is_starred": None,
            "negated_from": [],
            "negated_to": [],
            "negated_labels": [],
            "negated_subjects": [],
            "negated_body": [],
        }

        for term in query.terms:
            if term.operator == SearchOperator.FROM:
                if term.negated:
                    filters["negated_from"].append(term.value.lower())
                else:
                    filters["from_addrs"].append(term.value.lower())

            elif term.operator == SearchOperator.TO:
                if term.negated:
                    filters["negated_to"].append(term.value.lower())
                else:
                    filters["to_addrs"].append(term.value.lower())

            elif term.operator == SearchOperator.CC:
                filters["cc_addrs"].append(term.value.lower())

            elif term.operator == SearchOperator.SUBJECT:
                if term.negated:
                    filters["negated_subjects"].append(term.value)
                else:
                    filters["subjects"].append(term.value)

            elif term.operator == SearchOperator.BODY:
                if term.negated:
                    filters["negated_body"].append(term.value)
                else:
                    filters["body_text"].append(term.value)

            elif term.operator == SearchOperator.HAS:
                if term.value.lower() == "attachment":
                    filters["has_attachment"] = not term.negated

            elif term.operator == SearchOperator.LABEL:
                if term.negated:
                    filters["negated_labels"].append(term.value)
                else:
                    filters["labels"].append(term.value)

            elif term.operator == SearchOperator.BEFORE:
                date = EmailSearchService._parse_date(term.value)
                if date:
                    filters["before_date"] = date

            elif term.operator == SearchOperator.AFTER:
                date = EmailSearchService._parse_date(term.value)
                if date:
                    filters["after_date"] = date

            elif term.operator == SearchOperator.IS:
                if term.value.lower() == "read":
                    filters["is_read"] = not term.negated
                elif term.value.lower() == "unread":
                    filters["is_read"] = term.negated  # unread = not read
                elif term.value.lower() == "starred":
                    filters["is_starred"] = not term.negated

            elif term.operator is None:
                # Standalone term - search in subject and body
                if term.negated:
                    filters["negated_subjects"].append(term.value)
                    filters["negated_body"].append(term.value)
                else:
                    filters["subjects"].append(term.value)
                    filters["body_text"].append(term.value)

        return filters

    @staticmethod
    def highlight_matches(text: str, search_terms: list[str]) -> str:
        """Highlight search terms in text (for display).

        Args:
            text: Text to highlight
            search_terms: List of search terms

        Returns:
            Text with matches highlighted (using **term** markdown)
        """
        highlighted = text
        for term in search_terms:
            # Case-insensitive highlighting
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted = pattern.sub(lambda m: f"**{m.group(0)}**", highlighted)
        return highlighted

    @staticmethod
    def extract_snippet(text: str, search_terms: list[str], context_chars: int = 150) -> str:
        """Extract a snippet around the first search term match.

        Args:
            text: Text to extract snippet from
            search_terms: List of search terms
            context_chars: Number of characters of context on each side

        Returns:
            Text snippet with context
        """
        if not text or not search_terms:
            return text[:300] if text else ""

        # Find first match
        for term in search_terms:
            match = re.search(re.escape(term), text, re.IGNORECASE)
            if match:
                start_pos = max(0, match.start() - context_chars)
                end_pos = min(len(text), match.end() + context_chars)

                snippet = text[start_pos:end_pos]

                # Add ellipsis if truncated
                if start_pos > 0:
                    snippet = "..." + snippet
                if end_pos < len(text):
                    snippet = snippet + "..."

                return snippet

        # No match found, return beginning
        return text[:300] if text else ""

    @staticmethod
    def validate_query(query: str) -> tuple[bool, str | None]:
        """Validate search query syntax.

        Args:
            query: Search query string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Query cannot be empty"

        if len(query) > 1000:
            return False, "Query too long (max 1000 characters)"

        # Try parsing
        try:
            parsed = EmailSearchService.parse_query(query)
            if not parsed.terms:
                return False, "No valid search terms found"
            return True, None
        except Exception as e:
            return False, f"Invalid query syntax: {e!s}"
