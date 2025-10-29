# user_model.py
"""
Minimal user_model implementation to satisfy unit tests.
Replace with your real DB logic when ready.
"""

import hashlib
import os
import binascii
from typing import Optional, Dict, Any

# --- Password utilities (PBKDF2) ---
def hash_password(password: str, iterations: int = 100_000) -> str:
    """Return a hex string containing salt + derived key (format: salt$dk)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

def check_password(password: str, stored: str, iterations: int = 100_000) -> bool:
    try:
        salt_hex, dk_hex = stored.split("$", 1)
    except Exception:
        return False
    salt = binascii.unhexlify(salt_hex)
    expected = binascii.unhexlify(dk_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return dk == expected

# --- DB helper functions (very small, test-friendly) ---
def get_user_by_email(conn, email: str, role: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Example: conn is expected to provide cursor() usable as a context manager:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
    Returns whatever fetchone() returns (tests expect a dict).
    """
    sql = "SELECT user_id, email, role, password_hash FROM users WHERE email = %s"
    params = (email,)
    if role:
        sql += " AND role = %s"
        params = (email, role)
    cur = conn.cursor()
    # support either context-manager style or plain cursor
    try:
        with cur as c:
            c.execute(sql, params)
            return c.fetchone()
    except Exception:
        # fallback if cursor() returns a non-context manager (older patterns)
        cur.execute(sql, params)
        return cur.fetchone()

def create_user(
    conn,
    name: str,
    email: str,
    password: str,
    role: str,
    linked_cid: Optional[str] = None,
    linked_emp_id: Optional[str] = None,
):
    """Insert a user into DB. This function uses conn.cursor() and conn.commit()."""
    pw_hash = hash_password(password)
    sql = (
        "INSERT INTO users (name, email, password_hash, role, linked_cid, linked_emp_id) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    params = (name, email, pw_hash, role, linked_cid, linked_emp_id)

    cur = conn.cursor()
    try:
        with cur as c:
            c.execute(sql, params)
    except Exception:
        cur.execute(sql, params)

    # commit (connection mock should record this)
    try:
        conn.commit()
    except Exception:
        pass

    # return a simple success marker (not used by tests)
    return {"email": email, "role": role}
