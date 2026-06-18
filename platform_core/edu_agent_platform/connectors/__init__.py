"""Connector framework — fixture/live adapters for EDU systems of record."""
from .base import Connector, GenericConnector  # noqa: F401
from .factory import get_connector  # noqa: F401

__all__ = ["Connector", "GenericConnector", "get_connector"]
