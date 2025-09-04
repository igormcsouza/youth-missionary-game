import logging
import os
import secrets
from collections.abc import Callable
from typing import TypeVar

import streamlit as st

T = TypeVar("T")


def check_password():
    """Returns `True` if the user entered the correct password."""
    auth_password = os.environ.get("AUTH")

    if auth_password is None:
        st.error(
            "Autenticação não configurada. Por favor, defina a "
            "variável de ambiente AUTH."
        )
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
        st.text_input(
            "Senha",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False

    # Wrong password
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Senha",
            type="password",
            on_change=password_entered,
            key="password",
        )
        st.error(
            "❌ Senha incorreta. Entre em contato para obter uma nova senha!"
        )
        return False

    # Correct password
    else:
        return True


def handle_database_operation[T](
    operation: Callable[[], T],
    operation_name: str = "operação do banco de dados",
) -> T | None:
    """
    Handles database operations with user-friendly error messages.

    Args:
        operation: The database operation function to execute
        operation_name: Description of the operation for error messages

    Returns:
        The result of the operation, or None if an error occurred
    """
    try:
        return operation()
    except Exception as e:
        # Log the actual error for debugging
        logging.error(
            f"Database operation '{operation_name}' failed: {str(e)}"
        )

        # Show user-friendly message
        st.info(f"""
        🔄 **Problema temporário com o banco de dados**

        Houve uma dificuldade ao executar a {operation_name}. Isso pode
        acontecer ocasionalmente devido a:
        - Tempo limite de conexão
        - Sobrecarga temporária do banco
        - Problemas de rede

        **💡 Solução simples:** Atualize a página (F5) para tentar novamente.
        """)
        return None
