"""Thread domain module.

Note: Thread entities and repository interfaces are defined in the emails
domain to avoid circular dependencies. This module provides threading
algorithm and thread-specific services.
"""

from mailhookoss.domain.threads.service import ThreadService
from mailhookoss.domain.threads.threading_algorithm import ThreadingAlgorithm, ThreadNode

__all__ = [
    "ThreadService",
    "ThreadingAlgorithm",
    "ThreadNode",
]
