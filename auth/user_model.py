# auth/user_model.py
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_user_by_email(conn, email, role):
    with conn.cursor(dictionary=True) as cur:
        cur.execute(
            "SELECT * FROM Users WHERE email=%s AND role=%s",
            (email, role)
        )
        return cur.fetchone()

def create_user(conn, name, email, password, role, linked_cid=None, linked_emp_id=None):
    hashed = hash_password(password)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Users (name, email, password_hash, role, linked_cid, linked_emp_id)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (name, email, hashed, role, linked_cid, linked_emp_id))
        conn.commit()
 