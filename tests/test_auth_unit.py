# tests/test_auth_unit.py
import pytest
import sys
import os
from unittest.mock import MagicMock

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Robust import for different project layouts
try:
    import user_model as um
except ModuleNotFoundError:
    try:
        import ePIS.user_model as um  # if in a package folder
    except Exception as exc:
        raise ModuleNotFoundError("Could not import user_model. Place user_model.py in project root.") from exc


def make_mock_conn_fetchone(return_val):
    """Return a mock connection whose cursor() acts as a context manager and fetchone() returns return_val."""
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = return_val

    # context manager wrapper
    cm = MagicMock()
    cm.__enter__.return_value = mock_cur
    cm.__exit__.return_value = False

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = cm
    return mock_conn, mock_cur


def test_get_user_by_email_calls_cursor_correctly():
    expected = {"user_id": 1, "email": "test@example.com", "role": "doctor", "password_hash": "abc"}
    mock_conn, mock_cur = make_mock_conn_fetchone(expected)

    user = um.get_user_by_email(mock_conn, "test@example.com", "doctor")

    mock_conn.cursor.assert_called()
    mock_cur.execute.assert_called()
    assert user == expected


def test_create_user_executes_insert():
    # Use a real connection mock and inspect calls
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    cm = MagicMock()
    cm.__enter__.return_value = mock_cur
    cm.__exit__.return_value = False
    mock_conn.cursor.return_value = cm

    um.create_user(
        mock_conn,
        "Alice",
        "alice@example.com",
        "pass1",
        "patient",
        linked_cid="11111111111",
        linked_emp_id=None
    )

    mock_conn.cursor.assert_called()
    assert mock_cur.execute.called, "Expected cursor.execute to be called during create_user"
    assert mock_conn.commit.called, "Expected connection.commit to be called during create_user"
