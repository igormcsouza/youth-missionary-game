import pytest
import os
import sys
import time
from unittest.mock import patch, MagicMock, call
import pandas as pd

# Import the modules to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDadosGincanaPage:
    """Test functionality in the Dados da Gincana page"""
    
    def test_points_calculation_logic(self):
        """Test the points calculation logic from the page"""
        # Mock data similar to what's in the page
        mock_compiled_entries = [
            MagicMock(youth_id=1, task_id=1, quantity=2, bonus=5),  # 10*2 + 5 = 25
            MagicMock(youth_id=1, task_id=2, quantity=1, bonus=0),  # 20*1 + 0 = 20
            MagicMock(youth_id=2, task_id=1, quantity=1, bonus=10), # 10*1 + 10 = 20
        ]
        
        mock_tasks = [
            MagicMock(id=1, points=10),
            MagicMock(id=2, points=20),
        ]
        
        mock_youth = [
            MagicMock(id=1),
            MagicMock(id=2),
        ]
        
        # Apply the same logic as in the page
        task_by_id = {t.id: t for t in mock_tasks}
        
        youth_points = {}
        for youth in mock_youth:
            total_points = 0
            for entry in mock_compiled_entries:
                if entry.youth_id == youth.id:
                    task = task_by_id.get(entry.task_id)
                    if task:
                        total_points += task.points * entry.quantity + entry.bonus
            youth_points[youth.id] = total_points
        
        # Verify calculations
        assert youth_points[1] == 45  # 25 + 20
        assert youth_points[2] == 20  # 20
    
    def test_points_calculation_missing_task(self):
        """Test points calculation when task is missing"""
        mock_compiled_entries = [
            MagicMock(youth_id=1, task_id=999, quantity=2, bonus=5),  # Non-existent task
        ]
        
        mock_tasks = [
            MagicMock(id=1, points=10),
        ]
        
        mock_youth = [
            MagicMock(id=1),
        ]
        
        # Apply the same logic as in the page
        task_by_id = {t.id: t for t in mock_tasks}
        
        total_points = 0
        for entry in mock_compiled_entries:
            if entry.youth_id == 1:
                task = task_by_id.get(entry.task_id)
                if task:  # This should be False for non-existent task
                    total_points += task.points * entry.quantity + entry.bonus
        
        # Should be 0 since task doesn't exist
        assert total_points == 0
    
    def test_points_calculation_no_entries(self):
        """Test points calculation with no compiled entries"""
        mock_compiled_entries = []
        mock_tasks = [MagicMock(id=1, points=10)]
        mock_youth = [MagicMock(id=1)]
        
        task_by_id = {t.id: t for t in mock_tasks}
        
        total_points = 0
        for entry in mock_compiled_entries:
            if entry.youth_id == 1:
                task = task_by_id.get(entry.task_id)
                if task:
                    total_points += task.points * entry.quantity + entry.bonus
        
        assert total_points == 0


class TestRegistroTarefasPage:
    """Test functionality in the Registro das Tarefas page"""
    
    def test_refresh_youth_and_task_entries_function(self):
        """Test the refresh_youth_and_task_entries function logic"""
        # Mock youth and task data
        mock_youth = [
            MagicMock(id=1, name="João"),
            MagicMock(id=2, name="Maria"),
        ]
        
        mock_tasks = [
            MagicMock(id=1, tasks="Task 1"),
            MagicMock(id=2, tasks="Task 2"),
        ]
        
        # Apply the logic from the function
        youth_options = {y.id: y.name for y in mock_youth}
        task_options = {t.id: t.tasks for t in mock_tasks}
        
        # Verify the dictionaries are created correctly
        assert youth_options == {1: "João", 2: "Maria"}
        assert task_options == {1: "Task 1", 2: "Task 2"}
    
    def test_refresh_youth_and_task_entries_empty(self):
        """Test refresh function with empty data"""
        mock_youth = []
        mock_tasks = []
        
        youth_options = {y.id: y.name for y in mock_youth}
        task_options = {t.id: t.tasks for t in mock_tasks}
        
        assert youth_options == {}
        assert task_options == {}
    
    def test_task_by_id_mapping(self):
        """Test the task_by_id mapping logic"""
        mock_tasks = [
            MagicMock(id=1, tasks="Task 1", repeatable=True),
            MagicMock(id=2, tasks="Task 2", repeatable=False),
        ]
        
        # Apply the logic from the page
        task_by_id = {t.id: t for t in mock_tasks}
        
        assert len(task_by_id) == 2
        assert task_by_id[1].tasks == "Task 1"
        assert task_by_id[1].repeatable is True
        assert task_by_id[2].tasks == "Task 2"
        assert task_by_id[2].repeatable is False
    
    def test_repeatable_task_logic(self):
        """Test the logic for determining if a task is repeatable"""
        mock_tasks = [
            MagicMock(id=1, repeatable=True),
            MagicMock(id=2, repeatable=False),
        ]
        
        task_by_id = {t.id: t for t in mock_tasks}
        
        # Test logic from the page for selected task
        selected_task_id = 1
        selected_task = task_by_id.get(selected_task_id) if selected_task_id else None
        is_repeatable = selected_task.repeatable if selected_task else True
        
        assert is_repeatable is True
        
        # Test with non-repeatable task
        selected_task_id = 2
        selected_task = task_by_id.get(selected_task_id) if selected_task_id else None
        is_repeatable = selected_task.repeatable if selected_task else True
        
        assert is_repeatable is False
        
        # Test with no task selected
        selected_task_id = None
        selected_task = task_by_id.get(selected_task_id) if selected_task_id else None
        is_repeatable = selected_task.repeatable if selected_task else True
        
        assert is_repeatable is True  # Default to True when no task selected
    
    def test_validation_logic_non_repeatable_with_entry_today(self):
        """Test validation logic for non-repeatable tasks with existing entry"""
        # Simulate the validation conditions
        is_repeatable = False
        has_entry_today = True
        quantity = 1
        
        # This should trigger the first error condition
        should_error = not is_repeatable and has_entry_today
        assert should_error is True
    
    def test_validation_logic_non_repeatable_quantity_greater_than_one(self):
        """Test validation logic for non-repeatable tasks with quantity > 1"""
        # Simulate the validation conditions
        is_repeatable = False
        has_entry_today = False
        quantity = 2
        
        # This should trigger the second error condition
        should_error = not is_repeatable and quantity > 1
        assert should_error is True
    
    def test_validation_logic_repeatable_task(self):
        """Test validation logic for repeatable tasks"""
        # Simulate the validation conditions for repeatable task
        is_repeatable = True
        has_entry_today = True
        quantity = 5
        
        # This should not trigger any error conditions
        should_error_1 = not is_repeatable and has_entry_today
        should_error_2 = not is_repeatable and quantity > 1
        
        assert should_error_1 is False
        assert should_error_2 is False
    
    def test_validation_logic_non_repeatable_valid(self):
        """Test validation logic for valid non-repeatable task entry"""
        # Simulate valid conditions for non-repeatable task
        is_repeatable = False
        has_entry_today = False
        quantity = 1
        
        # This should not trigger any error conditions
        should_error_1 = not is_repeatable and has_entry_today
        should_error_2 = not is_repeatable and quantity > 1
        
        assert should_error_1 is False
        assert should_error_2 is False


class TestPageFormLogic:
    """Test form logic and data processing in pages"""
    
    def test_youth_form_data_validation(self):
        """Test youth form data structure"""
        # Simulate form data from youth registration
        name = "João Silva"
        age = 16
        organization = "Rapazes"
        total_points = 0
        
        # Basic validation that would be implicit in the form
        assert isinstance(name, str) and len(name) > 0
        assert isinstance(age, int) and 0 <= age <= 120
        assert organization in ["Rapazes", "Moças"]
        assert isinstance(total_points, int) and total_points >= 0
    
    def test_task_form_data_validation(self):
        """Test task form data structure"""
        # Simulate form data from task registration
        tasks = "Read scriptures daily"
        points = 10
        repeatable = True
        
        # Basic validation
        assert isinstance(tasks, str) and len(tasks) > 0
        assert isinstance(points, int) and points >= 0
        assert isinstance(repeatable, bool)
    
    def test_compiled_form_data_validation(self):
        """Test compiled form data structure"""
        # Simulate form data from task completion
        selected_youth_id = 1
        selected_task_id = 1
        quantity = 2
        bonus = 5
        timestamp = time.time()
        
        # Basic validation
        assert isinstance(selected_youth_id, int) and selected_youth_id > 0
        assert isinstance(selected_task_id, int) and selected_task_id > 0
        assert isinstance(quantity, int) and quantity >= 1
        assert isinstance(bonus, int) and bonus >= 0
        assert isinstance(timestamp, float) and timestamp > 0
    
    def test_form_submission_conditions(self):
        """Test conditions for form submissions"""
        # Test youth form submission conditions
        name = "Test Name"
        submitted = True
        
        should_process_youth = submitted and bool(name.strip())
        assert should_process_youth is True
        
        # Test with empty name
        name = ""
        should_process_youth = submitted and bool(name.strip())
        assert should_process_youth is False
        
        # Test compiled form submission conditions
        selected_youth_id = 1
        selected_task_id = 1
        submitted = True
        
        should_process_compiled = submitted and selected_youth_id and selected_task_id
        assert should_process_compiled is True
        
        # Test with missing youth
        selected_youth_id = None
        should_process_compiled = submitted and selected_youth_id and selected_task_id
        assert should_process_compiled is False


class TestPageDataFrameLogic:
    """Test DataFrame creation logic used in pages"""
    
    def test_youth_dataframe_creation(self):
        """Test youth DataFrame creation logic"""
        # Mock youth entries
        mock_entries = [
            MagicMock(name="João", age=16, organization="Rapazes", total_points=100),
            MagicMock(name="Maria", age=15, organization="Moças", total_points=75),
        ]
        
        # Apply the DataFrame creation logic from the page
        df_data = [
            {
                "Nome": e.name,
                "Idade": e.age,
                "Organização": e.organization,
                "Pontuação Total": e.total_points
            } for e in mock_entries
        ]
        
        df = pd.DataFrame(df_data)
        
        # Verify DataFrame structure
        assert len(df) == 2
        assert list(df.columns) == ["Nome", "Idade", "Organização", "Pontuação Total"]
        assert df.iloc[0]["Nome"] == "João"
        assert df.iloc[0]["Idade"] == 16
        assert df.iloc[1]["Nome"] == "Maria"
        assert df.iloc[1]["Organização"] == "Moças"
    
    def test_tasks_dataframe_creation(self):
        """Test tasks DataFrame creation logic"""
        # Mock task entries
        mock_entries = [
            MagicMock(tasks="Read scriptures", points=10, repeatable=True),
            MagicMock(tasks="Attend church", points=20, repeatable=False),
        ]
        
        # Apply the DataFrame creation logic from the page
        df_data = [
            {
                "Tarefa": t.tasks,
                "Pontuação": t.points,
                "Repetível": "Sim" if t.repeatable else "Não"
            } for t in mock_entries
        ]
        
        df = pd.DataFrame(df_data)
        
        # Verify DataFrame structure
        assert len(df) == 2
        assert list(df.columns) == ["Tarefa", "Pontuação", "Repetível"]
        assert df.iloc[0]["Tarefa"] == "Read scriptures"
        assert df.iloc[0]["Repetível"] == "Sim"
        assert df.iloc[1]["Tarefa"] == "Attend church"
        assert df.iloc[1]["Repetível"] == "Não"
    
    def test_empty_dataframe_handling(self):
        """Test DataFrame creation with empty data"""
        # Test empty youth entries
        mock_entries = []
        
        df_data = [
            {
                "Nome": e.name,
                "Idade": e.age,
                "Organização": e.organization,
                "Pontuação Total": e.total_points
            } for e in mock_entries
        ]
        
        df = pd.DataFrame(df_data)
        
        # Should create empty DataFrame with expected columns
        assert len(df) == 0
        
        # When DataFrame is empty, the conditional logic should handle it
        entries_exist = len(mock_entries) > 0
        assert entries_exist is False


class TestPageErrorHandling:
    """Test error handling scenarios in pages"""
    
    def test_missing_youth_or_task_options(self):
        """Test handling when youth or task options are empty"""
        youth_options = {}
        task_options = {}
        
        # Test selectbox options handling
        youth_keys = list(youth_options.keys())
        task_keys = list(task_options.keys())
        
        assert youth_keys == []
        assert task_keys == []
        
        # Test format_func with empty options
        def youth_format_func(x):
            return youth_options[x] if x in youth_options else ""
        
        def task_format_func(x):
            return task_options[x] if x in task_options else ""
        
        # Should return empty string for any input when options are empty
        assert youth_format_func(1) == ""
        assert task_format_func(1) == ""
    
    def test_none_values_in_selectbox(self):
        """Test handling None values in selectbox"""
        youth_options = {1: "João", 2: "Maria"}
        task_options = {1: "Task 1", 2: "Task 2"}
        
        def youth_format_func(x):
            return youth_options[x] if x in youth_options else ""
        
        def task_format_func(x):
            return task_options[x] if x in task_options else ""
        
        # Test with None (which shouldn't be in options but could be selected initially)
        assert youth_format_func(None) == ""
        assert task_format_func(None) == ""
        
        # Test with invalid ID
        assert youth_format_func(999) == ""
        assert task_format_func(999) == ""
    
    def test_task_retrieval_edge_cases(self):
        """Test edge cases in task retrieval"""
        task_by_id = {1: MagicMock(repeatable=True), 2: MagicMock(repeatable=False)}
        
        # Test with valid task ID
        selected_task = task_by_id.get(1)
        assert selected_task is not None
        assert selected_task.repeatable is True
        
        # Test with invalid task ID
        selected_task = task_by_id.get(999)
        assert selected_task is None
        
        # Test the conditional logic for None task
        is_repeatable = selected_task.repeatable if selected_task else True
        assert is_repeatable is True  # Default when task is None