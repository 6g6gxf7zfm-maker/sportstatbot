"""Integration modules for external services."""
from .google_docs import GoogleDocsIntegration
from .apple_notes import AppleNotesIntegration
from .email_notifier import EmailNotifier

__all__ = ['GoogleDocsIntegration', 'AppleNotesIntegration', 'EmailNotifier']
