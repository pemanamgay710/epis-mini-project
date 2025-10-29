# tests/test_user_model_unit.py
import pytest
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    import user_model as um
except ModuleNotFoundError:
    try:
        import ePIS.user_model as um
    except Exception as exc:
        raise ModuleNotFoundError("Could not import user_model. Place user_model.py in project root.") from exc


def test_hash_and_check_password():
    pw = "SuperSecret123!"
    hashed = um.hash_password(pw)
    assert isinstance(hashed, str)
    assert um.check_password(pw, hashed)


def test_check_password_negative():
    pw = "Password1"
    hashed = um.hash_password(pw)
    assert not um.check_password("WrongPassword", hashed)
