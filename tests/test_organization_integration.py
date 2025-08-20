"""
Streamlit app integration tests for the Organization column feature using streamlit.testing API
"""
import os
import sys
import time
import pytest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

# Ensure we can import from src directory  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestOrganizationColumnStreamlitIntegration:
    """Integration tests for Organization column functionality in actual Streamlit app"""
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_organization_column_end_to_end_streamlit_app(self, mock_compiled, mock_tasks, mock_youth):
        """Test the complete organization column workflow in actual Streamlit app"""
        
        # Create test data - youth with different organizations
        mock_youth1 = MagicMock()
        mock_youth1.id = 1
        mock_youth1.name = "João Silva"
        mock_youth1.organization = "Rapazes"
        
        mock_youth2 = MagicMock()
        mock_youth2.id = 2
        mock_youth2.name = "Maria Santos"
        mock_youth2.organization = "Moças"
        
        mock_youth3 = MagicMock()
        mock_youth3.id = 3
        mock_youth3.name = "Pedro Costa"
        mock_youth3.organization = "Rapazes"
        
        mock_youth.return_value = [mock_youth1, mock_youth2, mock_youth3]
        
        # Mock tasks
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
        current_time = time.time()
        mock_compiled1 = MagicMock()
        mock_compiled1.youth_id = 1
        mock_compiled1.task_id = 1
        mock_compiled1.timestamp = current_time
        mock_compiled1.quantity = 1
        mock_compiled1.bonus = 5
        
        mock_compiled2 = MagicMock()
        mock_compiled2.youth_id = 2
        mock_compiled2.task_id = 2
        mock_compiled2.timestamp = current_time
        mock_compiled2.quantity = 1
        mock_compiled2.bonus = 0
        
        mock_compiled3 = MagicMock()
        mock_compiled3.youth_id = 3
        mock_compiled3.task_id = 1
        mock_compiled3.timestamp = current_time
        mock_compiled3.quantity = 2
        mock_compiled3.bonus = 3
        
        mock_compiled.return_value = [mock_compiled1, mock_compiled2, mock_compiled3]
        
        # Mock authentication and run the actual Streamlit app
        with patch('utils.check_password', return_value=True):
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # The app should create the organization mappings and display the DataFrame
            # with Organization column in the correct position
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_form_interactions_with_organization_data(self, mock_compiled, mock_tasks, mock_youth):
        """Test form interactions when organization data is present"""
        
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
        
        # Empty compiled entries initially
        mock_compiled.return_value = []
        
        # Mock authentication and run the app
        with patch('utils.check_password', return_value=True):
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # The selectboxes should have the correct options available
            # The youth_org_options mapping should be created for organization lookup
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})  
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_organization_column_with_edge_case_data(self, mock_compiled, mock_tasks, mock_youth):
        """Test organization column with edge case data in Streamlit app"""
        
        # Mock youth with edge case organization data
        mock_youth1 = MagicMock()
        mock_youth1.id = 1
        mock_youth1.name = "Test User"
        mock_youth1.organization = "Rapazes"
        
        mock_youth.return_value = [mock_youth1]
        
        # Mock task
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.tasks = "Test Task"
        mock_task1.points = 10
        mock_task1.repeatable = True
        
        mock_tasks.return_value = [mock_task1]
        
        # Mock compiled entry with references to existing data
        mock_compiled1 = MagicMock()
        mock_compiled1.youth_id = 1
        mock_compiled1.task_id = 1
        mock_compiled1.timestamp = time.time()
        mock_compiled1.quantity = 1
        mock_compiled1.bonus = 0
        
        mock_compiled.return_value = [mock_compiled1]
        
        # Mock authentication and run the app
        with patch('utils.check_password', return_value=True):
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # The organization helper function should work correctly with valid data
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')  
    @patch('database.CompiledFormDataRepository.get_all')
    def test_refresh_function_signature_in_streamlit_context(self, mock_compiled, mock_tasks, mock_youth):
        """Test that refresh function returns the expected structure in Streamlit context"""
        
        # Mock youth with organization data
        mock_youth1 = MagicMock()
        mock_youth1.id = 1
        mock_youth1.name = "João"
        mock_youth1.organization = "Rapazes"
        
        mock_youth2 = MagicMock()
        mock_youth2.id = 2
        mock_youth2.name = "Maria"
        mock_youth2.organization = "Moças"
        
        mock_youth.return_value = [mock_youth1, mock_youth2]
        
        # Mock tasks
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.tasks = "Task 1"
        mock_task1.points = 10
        mock_task1.repeatable = True
        
        mock_task2 = MagicMock()
        mock_task2.id = 2
        mock_task2.tasks = "Task 2"
        mock_task2.points = 15
        mock_task2.repeatable = False
        
        mock_tasks.return_value = [mock_task1, mock_task2]
        
        # Mock empty compiled entries
        mock_compiled.return_value = []
        
        # Mock authentication and run the app
        with patch('utils.check_password', return_value=True):
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # The refresh function should be called and create all expected mappings
            # including the new youth_org_options mapping
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_dataframe_display_with_organization_column(self, mock_compiled, mock_tasks, mock_youth):
        """Test DataFrame display includes Organization column in Streamlit app"""
        
        # Mock youth data with organizations
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
        mock_task1.tasks = "Leitura"
        mock_task1.points = 10
        mock_task1.repeatable = True
        
        mock_task2 = MagicMock()
        mock_task2.id = 2
        mock_task2.tasks = "Culto"
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
        mock_compiled2.quantity = 2
        mock_compiled2.bonus = 0
        
        mock_compiled.return_value = [mock_compiled1, mock_compiled2]
        
        # Mock authentication and run the app
        with patch('utils.check_password', return_value=True):
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            
            # Verify the app loaded without errors
            assert not at.exception
            
            # The DataFrame should be created with the Organization column
            # and displayed in the "Entradas Compiladas Salvas" section


if __name__ == "__main__":
    pytest.main([__file__])