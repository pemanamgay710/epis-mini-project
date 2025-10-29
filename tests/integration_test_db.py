# tests/integration_test_db.py
import pytest
from auth import user_model as um
import mysql.connector
import os

def test_create_and_fetch_user_in_db(conn):
    # create a test user
    name = "TestUser"
    email = "testuser@example.com"
    password = "TestPass!23"
    role = "lab_tech"  # must match ENUM in schema

    # ensure no user exists with this email/role
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM Users WHERE email=%s AND role=%s", (email, role))
        assert cur.fetchone() is None

    # create the user
    um.create_user(conn, name, email, password, role, linked_cid=None, linked_emp_id=42)

    # now fetch and verify
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM Users WHERE email=%s AND role=%s", (email, role))
        user = cur.fetchone()
    assert user is not None
    assert user["name"] == name
    assert user["email"] == email
    assert user["role"] == role
    assert um.check_password(password, user["password_hash"])

def test_lab_test_to_report_flow(conn):
    """
    Integration test that:
    - inserts a Patient
    - inserts a Lab_Test for that patient
    - inserts a Test_Report for that test_id
    - validates referential integrity works
    """

    # 1) create a patient
    cid = 91111111111  # ensure it matches your CID constraints in schema
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Patient (CID_no, name, DOB, gender, contact, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (cid, "Integration Patient", "1980-01-01", "Male", 17700000, "Thimphu"))

    # 2) create a lab_test
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Lab_Test (test_name, date_ordered, CID_no, doctor_emp_id)
            VALUES (%s, CURDATE(), %s, %s)
        """, ("Integration Blood Test", cid, None))
        # get last inserted test_id
        cur.execute("SELECT LAST_INSERT_ID() as id")
        lid = cur.fetchone()[0]

    # 3) insert a Test_Report for that test_id
    # create a fake path
    fake_path = "reports/integration_report.pdf"
    with conn.cursor() as cur:
        cur.execute("INSERT INTO Test_Report (file_path, date_uploaded, test_id) VALUES (%s, CURDATE(), %s)", (fake_path, lid))

    # validate it exists
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM Test_Report WHERE test_id=%s", (lid,))
        tr = cur.fetchone()
    assert tr is not None
    assert tr["file_path"] == fake_path
