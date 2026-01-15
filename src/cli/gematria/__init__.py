"""Gematria CLI commands."""

from .commands import user_commands
from .admin import admin_commands

# All gematria commands to register
gematria_commands = user_commands + admin_commands

__all__ = ["gematria_commands"]
