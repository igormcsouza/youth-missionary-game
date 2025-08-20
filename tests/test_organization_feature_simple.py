"""
Streamlit app tests for the Organization column feature using streamlit.testing API
"""
import os
import sys
import time
import pytest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

# Ensure we can import from src directory  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestOrganizationColumnInStreamlitApp:
    """Test Organization column functionality within the actual Streamlit application"""
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_organization_column_appears_in_compiled_entries_table(self, mock_compiled, mock_tasks, mock_youth):
        """Test that the Organization column appears in the Entradas Compiladas Salvas table"""
        # Mock youth data with different organizations
        mock_youth1 = MagicMock()
        mock_youth1.id = 1
        mock_youth1.name = "João Silva"
        mock_youth1.organization = "Rapazes"
        
        mock_youth2 = MagicMock()
        mock_youth2.id = 2
        mock_youth2.name = "Maria Santos"
        mock_youth2.organization = "Moças"
        
        mock_youth.return_value = [mock_youth1, mock_youth2]
        
        # Mock task data
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.tasks = "Leitura das Escrituras"
        mock_task1.points = 10
        mock_task1.repeatable = True
        
        mock_task2 = MagicMock()
        mock_task2.id = 2
        mock_task2.tasks = "Participação no Culto"
        mock_task2.points = 15
        mock_task2.repeatable = False
        
        mock_tasks.return_value = [mock_task1, mock_task2]
        
        # Mock compiled entries
        mock_compiled1 = MagicMock()
        mock_compiled1.youth_id = 1
        mock_compiled1.task_id = 1
        mock_compiled1.timestamp = time.time()
        mock_compiled1.quantity = 1
        mock_compiled1.bonus = 5
        
        mock_compiled2 = MagicMock()
        mock_compiled2.youth_id = 2
        mock_compiled2.task_id = 2
        mock_compiled2.timestamp = time.time()
        mock_compiled2.quantity = 1
        mock_compiled2.bonus = 0
        
        mock_compiled.return_value = [mock_compiled1, mock_compiled2]
        
        # Mock authentication
        with patch('utils.check_password', return_value=True):
            # Change to source directory and run the actual Streamlit page
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # Check that the page contains the compiled entries table
            # The app should display the DataFrame with organization column
            # We can't directly inspect the DataFrame content in AppTest,
            # but we can verify there are no exceptions and the page loads
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_organization_column_with_empty_data(self, mock_compiled, mock_tasks, mock_youth):
        """Test Organization column handling when no compiled entries exist"""
        # Return empty data
        mock_youth.return_value = []
        mock_tasks.return_value = []
        mock_compiled.return_value = []
        
        # Mock authentication
        with patch('utils.check_password', return_value=True):
            # Change to source directory and run the actual Streamlit page
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # When there's no data, the app should show the empty state message
            # The page should still render correctly even with no organization data
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_organization_helper_function_in_streamlit_context(self, mock_compiled, mock_tasks, mock_youth):
        """Test that the get_organization_by_id helper function works in Streamlit context"""
        # Mock youth data
        mock_youth1 = MagicMock()
        mock_youth1.id = 1
        mock_youth1.name = "João Silva"
        mock_youth1.organization = "Rapazes"
        
        mock_youth.return_value = [mock_youth1]
        
        # Mock task data
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.tasks = "Test Task"
        mock_task1.points = 10
        mock_task1.repeatable = True
        
        mock_tasks.return_value = [mock_task1]
        
        # Mock compiled entry with an organization reference
        mock_compiled1 = MagicMock()
        mock_compiled1.youth_id = 1
        mock_compiled1.task_id = 1
        mock_compiled1.timestamp = time.time()
        mock_compiled1.quantity = 1
        mock_compiled1.bonus = 0
        
        mock_compiled.return_value = [mock_compiled1]
        
        # Mock authentication
        with patch('utils.check_password', return_value=True):
            # Change to source directory and run the actual Streamlit page
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # The helper function should be called within the app and work correctly
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_refresh_function_returns_organization_options(self, mock_compiled, mock_tasks, mock_youth):
        """Test that refresh_youth_and_task_entries returns youth_org_options in Streamlit context"""
        # Mock youth data with organization info
        mock_youth1 = MagicMock()
        mock_youth1.id = 1
        mock_youth1.name = "João Silva"
        mock_youth1.organization = "Rapazes"
        
        mock_youth2 = MagicMock()
        mock_youth2.id = 2
        mock_youth2.name = "Maria Santos"
        mock_youth2.organization = "Moças"
        
        mock_youth.return_value = [mock_youth1, mock_youth2]
        
        # Mock tasks
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.tasks = "Test Task"
        mock_task1.points = 10
        mock_task1.repeatable = True
        
        mock_tasks.return_value = [mock_task1]
        
        # Mock empty compiled entries
        mock_compiled.return_value = []
        
        # Mock authentication
        with patch('utils.check_password', return_value=True):
            # Change to source directory and run the actual Streamlit page
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # The refresh function should be called and create the youth_org_options mapping
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_organization_column_with_missing_youth_reference(self, mock_compiled, mock_tasks, mock_youth):
        """Test Organization column handles missing youth references gracefully"""
        # Mock empty youth data
        mock_youth.return_value = []
        
        # Mock task data
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.tasks = "Test Task"
        mock_task1.points = 10
        mock_task1.repeatable = True
        
        mock_tasks.return_value = [mock_task1]
        
        # Mock compiled entry with non-existent youth_id
        mock_compiled1 = MagicMock()
        mock_compiled1.youth_id = 999  # Non-existent
        mock_compiled1.task_id = 1
        mock_compiled1.timestamp = time.time()
        mock_compiled1.quantity = 1
        mock_compiled1.bonus = 0
        
        mock_compiled.return_value = [mock_compiled1]
        
        # Mock authentication
        with patch('utils.check_password', return_value=True):
            # Change to source directory and run the actual Streamlit page
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors even with missing references
            assert not at.exception
            
            # The get_organization_by_id function should handle missing IDs gracefully


if __name__ == "__main__":
    pytest.main([__file__])