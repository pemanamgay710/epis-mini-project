# auth/auth.py
import streamlit as st
from auth.user_model import get_user_by_email, create_user, check_password

def login_form(conn, role):
    st.subheader(f"{role.capitalize()} Login")
    email = st.text_input("Email", key=f"{role}_login_email")
    password = st.text_input("Password", type="password", key=f"{role}_login_pwd")
    if st.button("Login", key=f"{role}_login_btn"):
        user = get_user_by_email(conn, email, role)
        if user and check_password(password, user['password_hash']):
            st.session_state['user'] = user
            st.session_state['page'] = "dashboard"  #  Route to dashboard page
            st.success(f"Welcome {user['name']}!")
            st.rerun()  #  Force reload so it switches immediately

        else:
            st.error("Invalid credentials")

def signup_form(conn, role):
    st.subheader(f"{role.capitalize()} Sign-Up")
    with st.form(f"signup_{role}"):
        name = st.text_input("Full Name", key=f"{role}_signup_name")
        email = st.text_input("Email", key=f"{role}_signup_email")
        password = st.text_input("Password", type="password", key=f"{role}_signup_pwd")
        linked_cid = None
        linked_emp_id = None

        if role == "patient":
            linked_cid = st.text_input("Enter your CID", key=f"{role}_cid")
        else:
            linked_emp_id = st.number_input("Enter your Employee ID", min_value=1, step=1, key=f"{role}_emp_id")

        submitted = st.form_submit_button("Sign Up", key=f"{role}_signup_btn")
        if submitted:
            existing = get_user_by_email(conn, email, role)
            if existing:
                st.error("User already exists for this role.")
            else:
                create_user(conn, name, email, password, role, linked_cid, linked_emp_id)
                st.success("Account created! You can now log in.")
