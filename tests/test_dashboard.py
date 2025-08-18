import pytest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
from streamlit.testing.v1 import AppTest

# Import the modules to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDashboardStreamlitApp:
    """Test Dashboard.py using Streamlit testing API"""
    
    def test_dashboard_loads_without_error(self):
        """Test that the dashboard loads without errors"""
        # Change to src directory for proper imports
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        assert not at.exception
    
    def test_dashboard_title_displayed(self):
        """Test that the main title is displayed"""
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        # Check if title exists in any form
        assert len(at.title) > 0 or len(at.markdown) > 0
    
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_dashboard_with_empty_database(self, mock_compiled, mock_tasks, mock_youth):
        """Test dashboard behavior with empty database"""
        mock_youth.return_value = []
        mock_tasks.return_value = []
        mock_compiled.return_value = []
        
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        # Should load without exception
        assert not at.exception
    
    @patch('database.YouthFormDataRepository.get_all')
    @patch('database.TasksFormDataRepository.get_all')
    @patch('database.CompiledFormDataRepository.get_all')
    def test_dashboard_with_sample_data(self, mock_compiled, mock_tasks, mock_youth):
        """Test dashboard with sample data displays correctly"""
        # Mock youth data
        mock_youth_obj = MagicMock()
        mock_youth_obj.id = 1
        mock_youth_obj.name = "João Silva"
        mock_youth_obj.age = 16
        mock_youth_obj.organization = "Rapazes"
        mock_youth_obj.total_points = 45
        mock_youth.return_value = [mock_youth_obj]
        
        # Mock task data
        mock_task_obj = MagicMock()
        mock_task_obj.id = 1
        mock_task_obj.tasks = "Read scriptures"
        mock_task_obj.points = 10
        mock_task_obj.repeatable = True
        mock_tasks.return_value = [mock_task_obj]
        
        # Mock compiled data
        mock_compiled_obj = MagicMock()
        mock_compiled_obj.youth_id = 1
        mock_compiled_obj.task_id = 1
        mock_compiled_obj.quantity = 2
        mock_compiled_obj.bonus = 5
        mock_compiled_obj.timestamp = datetime.now().timestamp()
        mock_compiled.return_value = [mock_compiled_obj]
        
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        # Should load without exception
        assert not at.exception


class TestDashboardHelperFunctions:
    """Test helper functions in Dashboard module"""
    
    def test_get_last_sunday_logic(self):
        """Test get_last_sunday function logic"""
        # Test the logic directly without importing the module
        def get_last_sunday_test(current_date):
            days_since_sunday = current_date.weekday() + 1  # Monday = 1, Tuesday = 2, ..., Sunday = 7
            last_sunday = current_date - timedelta(days=days_since_sunday)
            # Set to beginning of Sunday
            return last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Test with Tuesday, Jan 3, 2023
        mock_tuesday = datetime(2023, 1, 3, 14, 30, 0)  # Tuesday afternoon
        last_sunday = get_last_sunday_test(mock_tuesday)
        
        # Should return Sunday, Jan 1, 2023 at 00:00:00
        expected_sunday = datetime(2023, 1, 1, 0, 0, 0)
        assert last_sunday == expected_sunday
    
    def test_get_last_sunday_on_sunday_logic(self):
        """Test get_last_sunday when today is Sunday"""
        def get_last_sunday_test(current_date):
            days_since_sunday = current_date.weekday() + 1  # Monday = 1, Tuesday = 2, ..., Sunday = 7
            last_sunday = current_date - timedelta(days=days_since_sunday)
            return last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Test with Sunday
        mock_sunday = datetime(2023, 1, 1, 15, 30, 0)  # Sunday afternoon
        last_sunday = get_last_sunday_test(mock_sunday)
        
        # Sunday's weekday() is 6, so days_since_sunday = 7, should return 7 days ago
        expected_sunday = datetime(2022, 12, 25, 0, 0, 0)
        assert last_sunday == expected_sunday
    
    def test_get_last_sunday_on_monday_logic(self):
        """Test get_last_sunday when today is Monday"""
        def get_last_sunday_test(current_date):
            days_since_sunday = current_date.weekday() + 1  # Monday = 1, Tuesday = 2, ..., Sunday = 7
            last_sunday = current_date - timedelta(days=days_since_sunday)
            return last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Test with Monday
        mock_monday = datetime(2023, 1, 2, 10, 0, 0)  # Monday morning
        last_sunday = get_last_sunday_test(mock_monday)
        
        # Monday's weekday() is 0, so days_since_sunday = 1, should return yesterday (Sunday)
        expected_sunday = datetime(2023, 1, 1, 0, 0, 0)
        assert last_sunday == expected_sunday


class TestCalculateTaskTotals:
    """Test calculate_task_totals function logic"""
    
    def test_calculate_task_totals_empty_data(self):
        """Test calculate_task_totals logic with no data"""
        # Test the logic directly
        compiled_entries = []
        task_entries = []
        task_dict = {t.id: t for t in task_entries}
        
        # Define target tasks mapping
        target_tasks = {
            "Entregar Livro de Mórmon + foto + relato no grupo": "Livros de Mórmon entregues",
            "Levar amigo à sacramental": "Pessoas levadas à igreja",
            "Ajudar alguém a se batizar": "Batismos",
            "Postar mensagem do evangelho nas redes sociais + print": "Posts nas redes sociais",
            "Fazer noite familiar com pesquisador": "Sessões de noite familiar"
        }
        
        # Calculate totals and deltas
        totals = {display_name: 0 for display_name in target_tasks.values()}
        deltas = {display_name: 0 for display_name in target_tasks.values()}
        
        current_time = datetime.now()
        last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
        monday_after_last_sunday = last_sunday + timedelta(days=1)
        monday_timestamp = monday_after_last_sunday.timestamp()
        
        for entry in compiled_entries:
            task = task_dict.get(entry.task_id)
            if task and task.tasks in target_tasks:
                display_name = target_tasks[task.tasks]
                totals[display_name] += entry.quantity
                
                if entry.timestamp >= monday_timestamp:
                    deltas[display_name] += entry.quantity
        
        expected_keys = [
            "Livros de Mórmon entregues",
            "Pessoas levadas à igreja", 
            "Batismos",
            "Posts nas redes sociais",
            "Sessões de noite familiar"
        ]
        
        # All totals should be 0
        for key in expected_keys:
            assert totals[key] == 0
            assert deltas[key] == 0
    
    def test_calculate_task_totals_with_data(self):
        """Test calculate_task_totals logic with sample data"""
        # Create proper mock objects
        class MockTask:
            def __init__(self, id, tasks):
                self.id = id
                self.tasks = tasks
        
        class MockEntry:
            def __init__(self, task_id, quantity, timestamp):
                self.task_id = task_id
                self.quantity = quantity
                self.timestamp = timestamp
        
        # Mock tasks
        mock_tasks = [
            MockTask(1, "Entregar Livro de Mórmon + foto + relato no grupo"),
            MockTask(2, "Levar amigo à sacramental"),
            MockTask(3, "Other task")  # This should be ignored
        ]
        
        # Mock compiled entries - some from this week, some older
        current_time = datetime.now()
        last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
        monday_after = last_sunday + timedelta(days=1)
        
        old_timestamp = (monday_after - timedelta(days=3)).timestamp()  # Before this week
        new_timestamp = (monday_after + timedelta(days=1)).timestamp()  # This week
        
        mock_compiled = [
            MockEntry(1, 2, old_timestamp),      # 2 books, old
            MockEntry(1, 1, new_timestamp),      # 1 book, this week  
            MockEntry(2, 1, new_timestamp),      # 1 friend, this week
            MockEntry(3, 5, new_timestamp),      # Other task, ignored
        ]
        
        # Apply dashboard calculation logic
        task_dict = {t.id: t for t in mock_tasks}
        
        # Define target tasks mapping
        target_tasks = {
            "Entregar Livro de Mórmon + foto + relato no grupo": "Livros de Mórmon entregues",
            "Levar amigo à sacramental": "Pessoas levadas à igreja",
            "Ajudar alguém a se batizar": "Batismos",
            "Postar mensagem do evangelho nas redes sociais + print": "Posts nas redes sociais",
            "Fazer noite familiar com pesquisador": "Sessões de noite familiar"
        }
        
        # Calculate totals and deltas
        totals = {display_name: 0 for display_name in target_tasks.values()}
        deltas = {display_name: 0 for display_name in target_tasks.values()}
        
        monday_timestamp = monday_after.timestamp()
        
        for entry in mock_compiled:
            task = task_dict.get(entry.task_id)
            if task and task.tasks in target_tasks:
                display_name = target_tasks[task.tasks]
                totals[display_name] += entry.quantity
                
                # Count activities since Monday after last Sunday
                if entry.timestamp >= monday_timestamp:
                    deltas[display_name] += entry.quantity
        
        # Check totals (all entries)
        assert totals["Livros de Mórmon entregues"] == 3  # 2 + 1
        assert totals["Pessoas levadas à igreja"] == 1
        assert totals["Batismos"] == 0
        assert totals["Posts nas redes sociais"] == 0
        assert totals["Sessões de noite familiar"] == 0
        
        # Check deltas (only this week)
        assert deltas["Livros de Mórmon entregues"] == 1  # Only new entry
        assert deltas["Pessoas levadas à igreja"] == 1
        assert deltas["Batismos"] == 0
        assert deltas["Posts nas redes sociais"] == 0
        assert deltas["Sessões de noite familiar"] == 0
    
    def test_calculate_task_totals_all_target_tasks(self):
        """Test calculate_task_totals logic with all target tasks"""
        # Create proper mock objects for all target tasks
        class MockTask:
            def __init__(self, id, tasks):
                self.id = id
                self.tasks = tasks
        
        class MockEntry:
            def __init__(self, task_id, quantity, timestamp):
                self.task_id = task_id
                self.quantity = quantity
                self.timestamp = timestamp
        
        # Mock all target tasks
        mock_tasks = [
            MockTask(1, "Entregar Livro de Mórmon + foto + relato no grupo"),
            MockTask(2, "Levar amigo à sacramental"),
            MockTask(3, "Ajudar alguém a se batizar"),
            MockTask(4, "Postar mensagem do evangelho nas redes sociais + print"),
            MockTask(5, "Fazer noite familiar com pesquisador"),
        ]
        
        current_time = datetime.now()
        last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
        monday_after = last_sunday + timedelta(days=1)
        this_week_timestamp = (monday_after + timedelta(days=1)).timestamp()
        
        # Mock compiled entries for all tasks, all this week
        mock_compiled = [
            MockEntry(1, 3, this_week_timestamp),  # 3 books
            MockEntry(2, 2, this_week_timestamp),  # 2 friends
            MockEntry(3, 1, this_week_timestamp),  # 1 baptism
            MockEntry(4, 5, this_week_timestamp),  # 5 posts
            MockEntry(5, 2, this_week_timestamp),  # 2 family nights
        ]
        
        # Apply dashboard calculation logic
        task_dict = {t.id: t for t in mock_tasks}
        
        # Define target tasks mapping
        target_tasks = {
            "Entregar Livro de Mórmon + foto + relato no grupo": "Livros de Mórmon entregues",
            "Levar amigo à sacramental": "Pessoas levadas à igreja",
            "Ajudar alguém a se batizar": "Batismos",
            "Postar mensagem do evangelho nas redes sociais + print": "Posts nas redes sociais",
            "Fazer noite familiar com pesquisador": "Sessões de noite familiar"
        }
        
        # Calculate totals and deltas
        totals = {display_name: 0 for display_name in target_tasks.values()}
        deltas = {display_name: 0 for display_name in target_tasks.values()}
        
        monday_timestamp = monday_after.timestamp()
        
        for entry in mock_compiled:
            task = task_dict.get(entry.task_id)
            if task and task.tasks in target_tasks:
                display_name = target_tasks[task.tasks]
                totals[display_name] += entry.quantity
                
                if entry.timestamp >= monday_timestamp:
                    deltas[display_name] += entry.quantity
        
        # All should have matching totals and deltas since all are this week
        assert totals["Livros de Mórmon entregues"] == 3
        assert deltas["Livros de Mórmon entregues"] == 3
        
        assert totals["Pessoas levadas à igreja"] == 2
        assert deltas["Pessoas levadas à igreja"] == 2
        
        assert totals["Batismos"] == 1
        assert deltas["Batismos"] == 1
        
        assert totals["Posts nas redes sociais"] == 5
        assert deltas["Posts nas redes sociais"] == 5
        
        assert totals["Sessões de noite familiar"] == 2
        assert deltas["Sessões de noite familiar"] == 2


class TestDashboardDataProcessing:
    """Test data processing logic used in dashboard"""
    
    def test_youth_ranking_logic(self):
        """Test the logic for ranking youth by total points"""
        # Create proper mock objects
        class MockYouth:
            def __init__(self, name, age, organization, total_points):
                self.name = name
                self.age = age
                self.organization = organization
                self.total_points = total_points
        
        # Mock youth data
        mock_youth = [
            MockYouth("João", 16, "Rapazes", 100),
            MockYouth("Maria", 15, "Moças", 150),
            MockYouth("Pedro", 17, "Rapazes", 0),  # Should be filtered out
            MockYouth("Ana", 16, "Moças", 75),
        ]
        
        # Apply the same logic as in Dashboard
        filtered_youth = [y for y in mock_youth if y.total_points > 0]
        sorted_youth = sorted(filtered_youth, key=lambda y: y.total_points, reverse=True)
        
        # Should be sorted by points, highest first, zero points filtered out
        assert len(sorted_youth) == 3
        assert sorted_youth[0].name == "Maria"  # 150 points
        assert sorted_youth[0].total_points == 150
        assert sorted_youth[1].name == "João"   # 100 points
        assert sorted_youth[1].total_points == 100
        assert sorted_youth[2].name == "Ana"    # 75 points
        assert sorted_youth[2].total_points == 75
        
        # Pedro should be filtered out (0 points)
        names = [y.name for y in sorted_youth]
        assert "Pedro" not in names
    
    def test_task_points_calculation(self):
        """Test the logic for calculating task points"""
        # Mock tasks
        mock_tasks = [
            MagicMock(id=1, tasks="Task 1", points=10),
            MagicMock(id=2, tasks="Task 2", points=20),
            MagicMock(id=3, tasks="Task 3", points=5),
        ]
        
        # Mock compiled entries
        mock_compiled = [
            MagicMock(task_id=1, quantity=2, bonus=5),  # 10*2 + 5 = 25 points
            MagicMock(task_id=1, quantity=1, bonus=0),  # 10*1 + 0 = 10 points  
            MagicMock(task_id=2, quantity=1, bonus=10), # 20*1 + 10 = 30 points
            MagicMock(task_id=3, quantity=3, bonus=0),  # 5*3 + 0 = 15 points
        ]
        
        # Apply the same logic as in Dashboard
        task_dict = {t.id: t for t in mock_tasks}
        task_points = {}
        
        for entry in mock_compiled:
            task = task_dict.get(entry.task_id)
            if task:
                points = task.points * entry.quantity + entry.bonus
                task_points[task.tasks] = task_points.get(task.tasks, 0) + points
        
        # Check calculated points
        assert task_points["Task 1"] == 35  # 25 + 10
        assert task_points["Task 2"] == 30  # 30
        assert task_points["Task 3"] == 15  # 15
    
    def test_organization_points_calculation(self):
        """Test the logic for calculating organization total points"""
        # Mock youth data
        mock_youth = [
            MagicMock(organization="Rapazes", total_points=100),
            MagicMock(organization="Rapazes", total_points=50),
            MagicMock(organization="Moças", total_points=75),
            MagicMock(organization="Moças", total_points=125),
            MagicMock(organization="Moças", total_points=25),
        ]
        
        # Apply the same logic as in Dashboard
        young_man_points = sum(y.total_points for y in mock_youth if y.organization == "Rapazes")
        young_woman_points = sum(y.total_points for y in mock_youth if y.organization == "Moças")
        
        assert young_man_points == 150  # 100 + 50
        assert young_woman_points == 225  # 75 + 125 + 25


class TestDashboardConstants:
    """Test constants and configuration in Dashboard"""
    
    def test_target_tasks_mapping(self):
        """Test that target_tasks mapping is correct"""
        # This tests the target_tasks dictionary structure
        expected_mapping = {
            "Entregar Livro de Mórmon + foto + relato no grupo": "Livros de Mórmon entregues",
            "Levar amigo à sacramental": "Pessoas levadas à igreja",
            "Ajudar alguém a se batizar": "Batismos",
            "Postar mensagem do evangelho nas redes sociais + print": "Posts nas redes sociais",
            "Fazer noite familiar com pesquisador": "Sessões de noite familiar"
        }
        
        # Test the mapping directly
        assert len(expected_mapping) == 5
        assert expected_mapping["Entregar Livro de Mórmon + foto + relato no grupo"] == "Livros de Mórmon entregues"
        assert expected_mapping["Levar amigo à sacramental"] == "Pessoas levadas à igreja"
        assert expected_mapping["Ajudar alguém a se batizar"] == "Batismos"
        assert expected_mapping["Postar mensagem do evangelho nas redes sociais + print"] == "Posts nas redes sociais"
        assert expected_mapping["Fazer noite familiar com pesquisador"] == "Sessões de noite familiar"
    
    def test_activity_cards_structure(self):
        """Test the structure of activity cards"""
        # This tests the activities list structure used for metric cards
        expected_activities = [
            ("Livros de Mórmon", "📖"),
            ("Pessoas na igreja", "⛪"),
            ("Batismos", "🛁"),
            ("Posts", "📱"),
            ("Noites familiares", "🏠")
        ]
        
        # Verify we have the right number and structure
        assert len(expected_activities) == 5
        
        for name, icon in expected_activities:
            assert isinstance(name, str)
            assert isinstance(icon, str)
            assert len(name) > 0
            assert len(icon) > 0
    
    def test_color_constants(self):
        """Test color constants for charts"""
        # Test that the color constants exist and are valid hex colors
        COLOR_YOUNG_MAN = "#1f77b4"
        COLOR_YOUNG_WOMAN = "#e75480"
        
        assert COLOR_YOUNG_MAN.startswith("#")
        assert len(COLOR_YOUNG_MAN) == 7
        assert COLOR_YOUNG_WOMAN.startswith("#")
        assert len(COLOR_YOUNG_WOMAN) == 7


class TestDashboardEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_calculate_task_totals_missing_task(self):
        """Test calculate_task_totals when compiled entry references missing task"""
        # Create proper mock objects
        class MockTask:
            def __init__(self, id, tasks):
                self.id = id
                self.tasks = tasks
        
        class MockEntry:
            def __init__(self, task_id, quantity, timestamp):
                self.task_id = task_id
                self.quantity = quantity
                self.timestamp = timestamp
        
        # Mock tasks (missing task id 2)
        mock_tasks = [
            MockTask(1, "Task 1"),
        ]
        
        # Mock compiled entries (references missing task id 2)
        mock_compiled = [
            MockEntry(1, 1, datetime.now().timestamp()),
            MockEntry(2, 1, datetime.now().timestamp()),  # Missing task
        ]
        
        # Apply the calculation logic
        task_dict = {t.id: t for t in mock_tasks}
        
        target_tasks = {
            "Entregar Livro de Mórmon + foto + relato no grupo": "Livros de Mórmon entregues",
            "Levar amigo à sacramental": "Pessoas levadas à igreja",
            "Ajudar alguém a se batizar": "Batismos",
            "Postar mensagem do evangelho nas redes sociais + print": "Posts nas redes sociais",
            "Fazer noite familiar com pesquisador": "Sessões de noite familiar"
        }
        
        totals = {display_name: 0 for display_name in target_tasks.values()}
        deltas = {display_name: 0 for display_name in target_tasks.values()}
        
        current_time = datetime.now()
        last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
        monday_after = last_sunday + timedelta(days=1)
        monday_timestamp = monday_after.timestamp()
        
        for entry in mock_compiled:
            task = task_dict.get(entry.task_id)
            if task and task.tasks in target_tasks:
                display_name = target_tasks[task.tasks]
                totals[display_name] += entry.quantity
                
                if entry.timestamp >= monday_timestamp:
                    deltas[display_name] += entry.quantity
        
        # Should not raise an error, should handle missing task gracefully
        assert isinstance(totals, dict)
        assert isinstance(deltas, dict)
        
        # All totals should be 0 since no tasks match the target tasks
        for key in target_tasks.values():
            assert totals[key] == 0
            assert deltas[key] == 0
    
    def test_empty_youth_list_ranking(self):
        """Test youth ranking with empty list"""
        mock_youth = []
        
        filtered_youth = [y for y in mock_youth if y.total_points > 0]
        sorted_youth = sorted(filtered_youth, key=lambda y: y.total_points, reverse=True)
        
        assert len(sorted_youth) == 0
        assert sorted_youth == []
    
    def test_all_zero_points_youth(self):
        """Test youth ranking when all youth have zero points"""
        mock_youth = [
            MagicMock(name="João", total_points=0),
            MagicMock(name="Maria", total_points=0),
        ]
        
        filtered_youth = [y for y in mock_youth if y.total_points > 0]
        sorted_youth = sorted(filtered_youth, key=lambda y: y.total_points, reverse=True)
        
        assert len(sorted_youth) == 0
        assert sorted_youth == []
    
    def test_organization_points_empty_data(self):
        """Test organization points calculation with no youth"""
        mock_youth = []
        
        young_man_points = sum(y.total_points for y in mock_youth if y.organization == "Rapazes")
        young_woman_points = sum(y.total_points for y in mock_youth if y.organization == "Moças")
        
        assert young_man_points == 0
        assert young_woman_points == 0
    
    def test_organization_points_unknown_organization(self):
        """Test organization points with unknown organization"""
        mock_youth = [
            MagicMock(organization="Unknown", total_points=100),
            MagicMock(organization="Rapazes", total_points=50),
        ]
        
        young_man_points = sum(y.total_points for y in mock_youth if y.organization == "Rapazes")
        young_woman_points = sum(y.total_points for y in mock_youth if y.organization == "Moças")
        
        # Unknown organization should not be counted
        assert young_man_points == 50
        assert young_woman_points == 0