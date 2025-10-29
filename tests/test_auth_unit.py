# tests/test_auth_unit.py
import pytest
import sys
import os
# ensure project root is on sys.path (optional but robust)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import user_model as um   # or import auth if file is auth.py (adjust accordingly)
from unittest.mock import MagicMock

def make_mock_conn_fetchone(return_val):
    """Helper: return a connection whose cursor().fetchone() returns return_val"""
    mock_cur = MagicMock()
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.fetchone.return_value = return_val

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    return mock_conn, mock_cur

def test_get_user_by_email_calls_cursor_correctly():
    expected = {"user_id": 1, "email": "test@example.com", "role": "doctor", "password_hash": "abc"}
    mock_conn, mock_cur = make_mock_conn_fetchone(expected)

    # patch cursor to behave like context manager that returns dictionary rows
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.fetchone.return_value = expected

    user = um.get_user_by_email(mock_conn, "test@example.com", "doctor")
    # The function uses cursor(dictionary=True) so we check fetchone was called
    mock_conn.cursor.assert_called()
    mock_cur.execute.assert_called()
    assert user == expected

def test_create_user_executes_insert(mocker):
    # Use a real connection mock and inspect calls
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur

    # call create_user (it will call hash_password internally)
    um.create_user(mock_conn, "Alice", "alice@example.com", "pass1", "patient", linked_cid="11111111111", linked_emp_id=None)

    # ensure SQL execution was attempted
    mock_conn.cursor.assert_called()
    assert mock_cur.execute.called
    assert mock_conn.commit.called
