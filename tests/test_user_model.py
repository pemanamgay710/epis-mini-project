# tests/test_user_model_unit.py
import pytest
import sys
import os
# ensure project root is on sys.path (optional but robust)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import user_model as um   # or import auth if file is auth.py (adjust accordingly)


def test_hash_and_check_password():
    pw = "SuperSecret123!"
    hashed = um.hash_password(pw)
    assert isinstance(hashed, str)
    assert um.check_password(pw, hashed)

def test_check_password_negative():
    pw = "Password1"
    hashed = um.hash_password(pw)
    assert not um.check_password("WrongPassword", hashed)
