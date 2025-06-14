"""
Package initialization for the config module.
"""
from .tenant_utils import tenant_limit_callback

__all__ = ['tenant_limit_callback']