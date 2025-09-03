import os

# Import the modules to test
import sys
from unittest.mock import patch

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils import check_password, handle_database_operation


class TestCheckPassword:
    """Test password checking functionality"""

    def setup_method(self):
        """Reset Streamlit session state before each test"""
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

    @patch.dict(os.environ, {}, clear=True)
    @patch("streamlit.error")
    def test_check_password_no_auth_env(self, mock_error):
        """Test check_password when AUTH environment variable is not set"""
        result = check_password()

        assert result is False
        mock_error.assert_called_once_with(
            "Autenticação não configurada. Por favor, defina a variável de ambiente AUTH."
        )

    @patch.dict(os.environ, {"AUTH": "test_password"})
    @patch("streamlit.text_input")
    def test_check_password_first_run(self, mock_text_input):
        """Test check_password on first run (no session state)"""
        result = check_password()

        assert result is False
        mock_text_input.assert_called_once_with(
            "Senha",
            type="password",
            on_change=mock_text_input.call_args[1]["on_change"],
            key="password",
        )

    @patch.dict(os.environ, {"AUTH": "test_password"})
    @patch("streamlit.text_input")
    @patch("streamlit.error")
    def test_check_password_wrong_password(self, mock_error, mock_text_input):
        """Test check_password with wrong password"""
        # Set up session state for wrong password
        st.session_state["password_correct"] = False

        result = check_password()

        assert result is False
        mock_text_input.assert_called_once()
        mock_error.assert_called_once_with(
            "❌ Senha incorreta. Entre em contato para obter uma nova senha!"
        )

    @patch.dict(os.environ, {"AUTH": "test_password"})
    def test_check_password_correct_password(self):
        """Test check_password with correct password"""
        # Set up session state for correct password
        st.session_state["password_correct"] = True

        result = check_password()

        assert result is True

    @patch.dict(os.environ, {"AUTH": "test_password"})
    def test_password_entered_correct(self):
        """Test password_entered function with correct password"""
        # Set up session state with correct password
        st.session_state["password"] = "test_password"

        # Get the password_entered function by calling check_password
        with patch("streamlit.text_input") as mock_text_input:
            check_password()

            # Extract the on_change function
            password_entered = mock_text_input.call_args[1]["on_change"]

            # Call the password_entered function
            password_entered()

            # Check that session state is updated correctly
            assert st.session_state["password_correct"] is True
            assert "password" not in st.session_state

    @patch.dict(os.environ, {"AUTH": "test_password"})
    def test_password_entered_incorrect(self):
        """Test password_entered function with incorrect password"""
        # Set up session state with incorrect password
        st.session_state["password"] = "wrong_password"

        # Get the password_entered function by calling check_password
        with patch("streamlit.text_input") as mock_text_input:
            check_password()

            # Extract the on_change function
            password_entered = mock_text_input.call_args[1]["on_change"]

            # Call the password_entered function
            password_entered()

            # Check that session state is updated correctly
            assert st.session_state["password_correct"] is False
            # Password should remain in session state for incorrect attempts


class TestHandleDatabaseOperation:
    """Test database operation error handling"""

    def test_handle_database_operation_success(self):
        """Test successful database operation"""

        def successful_operation():
            return "success"

        result = handle_database_operation(successful_operation, "test operation")

        assert result == "success"

    @patch("streamlit.info")
    @patch("logging.error")
    def test_handle_database_operation_failure(self, mock_log_error, mock_st_info):
        """Test failed database operation"""

        def failing_operation():
            raise Exception("Database error")

        result = handle_database_operation(failing_operation, "test operation")

        assert result is None
        mock_log_error.assert_called_once_with(
            "Database operation 'test operation' failed: Database error"
        )
        mock_st_info.assert_called_once()

        # Check that the info message contains expected content
        info_call_args = mock_st_info.call_args[0][0]
        assert "Problema temporário com o banco de dados" in info_call_args
        assert "test operation" in info_call_args

    @patch("streamlit.info")
    @patch("logging.error")
    def test_handle_database_operation_default_name(self, mock_log_error, mock_st_info):
        """Test database operation with default operation name"""

        def failing_operation():
            raise Exception("Database error")

        result = handle_database_operation(failing_operation)

        assert result is None
        mock_log_error.assert_called_once_with(
            "Database operation 'operação do banco de dados' failed: Database error"
        )
        mock_st_info.assert_called_once()

    def test_handle_database_operation_with_return_value(self):
        """Test database operation that returns a complex object"""

        def operation_with_object():
            return {"id": 1, "name": "test", "data": [1, 2, 3]}

        result = handle_database_operation(operation_with_object, "complex operation")

        assert result == {"id": 1, "name": "test", "data": [1, 2, 3]}

    def test_handle_database_operation_with_none_return(self):
        """Test database operation that returns None"""

        def operation_returning_none():
            return None

        result = handle_database_operation(operation_returning_none, "none operation")

        assert result is None

    @patch("streamlit.info")
    @patch("logging.error")
    def test_handle_database_operation_different_exceptions(
        self, mock_log_error, mock_st_info
    ):
        """Test database operation with different types of exceptions"""
        exceptions_to_test = [
            ValueError("Invalid value"),
            ConnectionError("Connection failed"),
            RuntimeError("Runtime error"),
            KeyError("Key not found"),
        ]

        for exception in exceptions_to_test:

            def failing_operation():
                raise exception

            result = handle_database_operation(failing_operation, "exception test")

            assert result is None

        # Check that logging was called for each exception
        assert mock_log_error.call_count == len(exceptions_to_test)
        assert mock_st_info.call_count == len(exceptions_to_test)

    @patch("streamlit.info")
    @patch("logging.error")
    def test_handle_database_operation_long_operation_name(
        self, mock_log_error, mock_st_info
    ):
        """Test database operation with a long operation name"""
        long_operation_name = "a very long operation name that describes exactly what this operation does in great detail"

        def failing_operation():
            raise Exception("Test error")

        result = handle_database_operation(failing_operation, long_operation_name)

        assert result is None
        mock_log_error.assert_called_once()

        # Check that the long operation name is included in both log and user message
        log_call_args = mock_log_error.call_args[0][0]
        assert long_operation_name in log_call_args

        info_call_args = mock_st_info.call_args[0][0]
        assert long_operation_name in info_call_args


class TestUtilsModuleIntegration:
    """Integration tests for utils module functionality"""

    @patch.dict(os.environ, {"AUTH": "integration_test_password"})
    def test_password_workflow_complete(self):
        """Test complete password workflow from start to authentication"""
        # Start with clean session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # First call - should ask for password
        with patch("streamlit.text_input") as mock_text_input:
            result1 = check_password()
            assert result1 is False
            mock_text_input.assert_called_once()

        # Simulate user entering correct password
        st.session_state["password"] = "integration_test_password"

        # Get and call the password_entered function
        with patch("streamlit.text_input") as mock_text_input:
            check_password()
            password_entered = mock_text_input.call_args[1]["on_change"]
            password_entered()

        # Third call - should now return True
        result2 = check_password()
        assert result2 is True

    def test_database_operation_with_real_function(self):
        """Test handle_database_operation with a real function"""

        def database_operation():
            # Simulate a real database operation
            data = {"users": [], "tasks": []}
            data["users"].append({"id": 1, "name": "Test User"})
            return data

        result = handle_database_operation(database_operation, "user creation")

        expected = {"users": [{"id": 1, "name": "Test User"}], "tasks": []}
        assert result == expected

    @patch("streamlit.info")
    @patch("logging.error")
    def test_nested_database_operations(self, mock_log_error, mock_st_info):
        """Test nested database operations with error handling"""

        def outer_operation():
            def inner_operation():
                raise Exception("Inner operation failed")

            return handle_database_operation(inner_operation, "inner operation")

        result = handle_database_operation(outer_operation, "outer operation")

        # The inner operation should fail and return None
        # The outer operation should complete successfully but return None
        assert result is None

        # Only the inner operation should log an error
        mock_log_error.assert_called_once()
        mock_st_info.assert_called_once()


class TestTypeAnnotations:
    """Test that type annotations work correctly"""

    def test_handle_database_operation_type_preservation(self):
        """Test that handle_database_operation preserves return types"""

        def string_operation():
            return "string result"

        def int_operation():
            return 42

        def list_operation():
            return [1, 2, 3]

        def dict_operation():
            return {"key": "value"}

        # Test different return types
        assert handle_database_operation(string_operation) == "string result"
        assert handle_database_operation(int_operation) == 42
        assert handle_database_operation(list_operation) == [1, 2, 3]
        assert handle_database_operation(dict_operation) == {"key": "value"}

    def test_check_password_return_type(self):
        """Test that check_password returns boolean"""
        with patch.dict(os.environ, {"AUTH": "test"}):
            st.session_state["password_correct"] = True
            result = check_password()
            assert isinstance(result, bool)
            assert result is True

            st.session_state["password_correct"] = False
            with patch("streamlit.text_input"), patch("streamlit.error"):
                result = check_password()
                assert isinstance(result, bool)
                assert result is False
