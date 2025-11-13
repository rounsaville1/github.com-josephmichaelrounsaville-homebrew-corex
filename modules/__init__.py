"""
R-COREX Bitcoin Mainnet System
Core Modules Package

Author: Joseph Michael Rounsaville
System: Unified Bitcoin Infrastructure
"""

__version__ = "1.0.0"
__author__ = "Joseph Michael Rounsaville"
__system__ = "R-COREX Bitcoin Mainnet"

# Module exports
from . import bitcoin_core
from . import crypto
from . import api
from . import database
from . import security

__all__ = [
    "bitcoin_core",
    "crypto",
    "api",
    "database",
    "security",
]
