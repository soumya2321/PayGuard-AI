"""
logging.py - Structured audit logging for login attempts and brute-force rate-limiting.
Never logs plaintext passwords.
"""

from datetime import datetime, timezone
import time
from typing import Dict, List, Tuple
from collections import defaultdict

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_WINDOW_SECONDS = 60

# In-memory store of recent failed login attempts per key (identifier / IP)
# Format: { key: [timestamp1, timestamp2, ...] }
_failed_attempts: Dict[str, List[float]] = defaultdict(list)

# In-memory audit trail of login events
_login_audit_trail: List[Dict[str, any]] = []


def is_rate_limited(identifier: str, client_ip: str) -> Tuple[bool, int]:
    """
    Checks if an account or IP is currently locked out after 5 failed attempts in 60s.
    Returns (is_locked, retry_after_seconds).
    """
    now = time.time()
    cutoff = now - LOCKOUT_WINDOW_SECONDS

    # Check both identifier and IP
    for key in [identifier.lower().strip(), client_ip]:
        recent_failures = [t for t in _failed_attempts[key] if t > cutoff]
        _failed_attempts[key] = recent_failures

        if len(recent_failures) >= MAX_FAILED_ATTEMPTS:
            oldest_relevant = min(recent_failures)
            remaining_lockout = int(LOCKOUT_WINDOW_SECONDS - (now - oldest_relevant))
            return True, max(1, remaining_lockout)

    return False, 0


def log_login_attempt(
    identifier: str,
    client_ip: str,
    success: bool,
    reason: str = "",
    user_id: int = None,
) -> None:
    """
    Logs authentication attempts with security auditing. Never logs passwords.
    """
    now_ts = time.time()
    iso_time = datetime.now(timezone.utc).isoformat()
    clean_id = identifier.lower().strip()

    audit_entry = {
        "timestamp": iso_time,
        "identifier": clean_id,
        "client_ip": client_ip,
        "success": success,
        "reason": reason if not success else "Authenticated successfully",
        "user_id": user_id,
    }

    _login_audit_trail.append(audit_entry)

    # Keep trail bounded to last 500 entries
    if len(_login_audit_trail) > 500:
        _login_audit_trail.pop(0)

    if success:
        # Reset failed attempts upon successful login
        _failed_attempts.pop(clean_id, None)
        _failed_attempts.pop(client_ip, None)
        print(f"[AUTH AUDIT] [SUCCESS] User '{clean_id}' logged in from IP {client_ip} at {iso_time}")
    else:
        _failed_attempts[clean_id].append(now_ts)
        _failed_attempts[client_ip].append(now_ts)
        print(f"[AUTH AUDIT] [FAILURE] Login failed for '{clean_id}' from IP {client_ip}. Reason: {reason} at {iso_time}")


def get_login_audit_trail() -> List[Dict[str, any]]:
    """Retrieve recent login audit entries for inspection."""
    return list(_login_audit_trail)
