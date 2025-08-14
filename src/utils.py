import os
import secrets

import streamlit as st


def check_password():
    """Returns `True` if the user entered the correct password."""
    auth_password = os.environ.get("AUTH")

    if auth_password is None:
        st.error("Autenticação não configurada. Por favor, defina a variável de ambiente AUTH.")
        return False

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if secrets.compare_digest(st.session_state["password"], auth_password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # First run: ask for password
    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False

    # Wrong password
    elif not st.session_state["password_correct"]:
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        return False

    # Wrong password
    elif not st.session_state["password_correct"]:
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        st.error("Senha incorreta")
        return False

    # Correct password
    else:
        return True
