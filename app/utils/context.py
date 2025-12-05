"""
Request context management for trace IDs and correlation.
"""
from contextvars import ContextVar
import uuid
from typing import Optional


# Context variable for request ID (thread-safe)
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> str:
    """
    Get the current request ID from context, or generate a new one.

    Returns:
        str: Request/trace ID (UUID format)
    """
    request_id = request_id_var.get()
    if request_id is None:
        request_id = str(uuid.uuid4())
        set_request_id(request_id)
    return request_id


def set_request_id(request_id: str) -> None:
    """
    Set the request ID in the current context.

    Args:
        request_id: The request/trace ID to set
    """
    request_id_var.set(request_id)


def clear_request_id() -> None:
    """
    Clear the request ID from the current context.
    """
    request_id_var.set(None)
