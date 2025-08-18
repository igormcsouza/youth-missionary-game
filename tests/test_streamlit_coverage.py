import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

# Import the modules to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestStreamlitPageCoverage:
    """Test Streamlit pages for coverage - focused on exercising page code paths"""
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_dashboard_with_various_data_scenarios(self, mock_compiled, mock_tasks, mock_youth):
        """Test dashboard with different data scenarios to increase coverage"""
        # Test with empty data
        mock_youth.return_value = []
        mock_tasks.return_value = []
        mock_compiled.return_value = []
        
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        assert not at.exception
        
        # Test with some data
        mock_youth_obj = MagicMock()
        mock_youth_obj.id = 1
        mock_youth_obj.name = "João Silva"
        mock_youth_obj.age = 16
        mock_youth_obj.organization = "Rapazes"
        mock_youth_obj.total_points = 45
        
        mock_youth_obj2 = MagicMock()
        mock_youth_obj2.id = 2
        mock_youth_obj2.name = "Maria Santos"
        mock_youth_obj2.age = 15
        mock_youth_obj2.organization = "Moças"
        mock_youth_obj2.total_points = 60
        
        mock_youth.return_value = [mock_youth_obj, mock_youth_obj2]
        
        # Mock missionary tasks
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.tasks = "Entregar Livro de Mórmon + foto + relato no grupo"
        mock_task1.points = 10
        mock_task1.repeatable = True
        
        mock_task2 = MagicMock()
        mock_task2.id = 2
        mock_task2.tasks = "Levar amigo à sacramental"
        mock_task2.points = 20
        mock_task2.repeatable = True
        
        mock_tasks.return_value = [mock_task1, mock_task2]
        
        # Mock compiled data
        mock_compiled1 = MagicMock()
        mock_compiled1.youth_id = 1
        mock_compiled1.task_id = 1
        mock_compiled1.quantity = 2
        mock_compiled1.bonus = 5
        mock_compiled1.timestamp = 1609459200.0  # Jan 1, 2021
        
        mock_compiled2 = MagicMock()
        mock_compiled2.youth_id = 2
        mock_compiled2.task_id = 2
        mock_compiled2.quantity = 1
        mock_compiled2.bonus = 0
        mock_compiled2.timestamp = 1609459200.0
        
        mock_compiled.return_value = [mock_compiled1, mock_compiled2]
        
        at.run()
        assert not at.exception
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.YouthFormDataRepository.store')
    @patch('database.YouthFormDataRepository.update_total_points')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.store')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_dados_gincana_page_coverage(self, mock_compiled_get, mock_tasks_store, mock_tasks_get, 
                                       mock_youth_update, mock_youth_store, mock_youth_get):
        """Test Dados da Gincana page with different scenarios"""
        with patch('utils.check_password', return_value=True):
            # Mock return values
            mock_youth_get.return_value = []
            mock_tasks_get.return_value = []
            mock_compiled_get.return_value = []
            mock_youth_store.return_value = MagicMock(id=1)
            mock_tasks_store.return_value = MagicMock(id=1)
            
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/1_📁_Dados_da_Gincana.py")
            at.run()
            assert not at.exception
            
            # Test with existing data
            mock_youth1 = MagicMock()
            mock_youth1.id = 1
            mock_youth1.name = "João Silva"
            mock_youth1.age = 16
            mock_youth1.organization = "Rapazes"
            mock_youth1.total_points = 0
            
            mock_task1 = MagicMock()
            mock_task1.id = 1
            mock_task1.tasks = "Test Task"
            mock_task1.points = 10
            mock_task1.repeatable = True
            
            mock_youth_get.return_value = [mock_youth1]
            mock_tasks_get.return_value = [mock_task1]
            
            at.run()
            assert not at.exception
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.store')
    @patch('database.CompiledFormDataRepository.has_entry_today')
    def test_registro_tarefas_page_coverage(self, mock_has_entry, mock_compiled_store, 
                                         mock_compiled_get, mock_tasks_get, mock_youth_get):
        """Test Registro das Tarefas page with different scenarios"""
        with patch('utils.check_password', return_value=True):
            # Setup mock data
            mock_youth1 = MagicMock()
            mock_youth1.id = 1
            mock_youth1.name = "João Silva"
            
            mock_task1 = MagicMock()
            mock_task1.id = 1
            mock_task1.tasks = "Test Task"
            mock_task1.repeatable = True
            
            mock_task2 = MagicMock()
            mock_task2.id = 2
            mock_task2.tasks = "Non-Repeatable Task"
            mock_task2.repeatable = False
            
            mock_youth_get.return_value = [mock_youth1]
            mock_tasks_get.return_value = [mock_task1, mock_task2]
            mock_compiled_get.return_value = []
            mock_has_entry.return_value = False
            mock_compiled_store.return_value = MagicMock(id=1)
            
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/2_📝_Registro_das_Tarefas.py")
            at.run()
            assert not at.exception
            
            # Test with empty options
            mock_youth_get.return_value = []
            mock_tasks_get.return_value = []
            
            at.run()
            assert not at.exception
    
    @patch.dict(os.environ, {'AUTH': 'test_password'})
    def test_authentication_scenarios(self):
        """Test authentication scenarios to increase utils coverage"""
        # Test with missing AUTH
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.check_password', return_value=False):
                os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
                at = AppTest.from_file("pages/1_📁_Dados_da_Gincana.py")
                at.run()
                # Page should stop due to authentication failure
                assert not at.exception  # Should handle gracefully
        
        # Test with correct auth
        with patch('utils.check_password', return_value=True):
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("pages/1_📁_Dados_da_Gincana.py")
            at.run()
            assert not at.exception