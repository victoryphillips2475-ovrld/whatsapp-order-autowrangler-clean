"""Shared rate limiter for OrderStream API."""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance — used across all routers.
# Default limit is 200/min per IP; specific routes override this.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
)