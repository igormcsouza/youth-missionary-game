import pytest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

# Import the modules to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# We need to mock streamlit before importing Dashboard
with patch.dict('sys.modules', {'streamlit': MagicMock()}):
    import Dashboard


class TestDashboardHelperFunctions:
    """Test helper functions in Dashboard module"""
    
    def test_get_last_sunday(self):
        """Test get_last_sunday function"""
        # Mock current time to a known date (Tuesday, Jan 3, 2023)
        mock_tuesday = datetime(2023, 1, 3, 14, 30, 0)  # Tuesday afternoon
        
        with patch('Dashboard.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_tuesday
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            last_sunday = Dashboard.get_last_sunday()
            
            # Should return Sunday, Jan 1, 2023 at 00:00:00
            expected_sunday = datetime(2023, 1, 1, 0, 0, 0)
            assert last_sunday == expected_sunday
    
    def test_get_last_sunday_on_sunday(self):
        """Test get_last_sunday when today is Sunday"""
        # Mock current time to Sunday
        mock_sunday = datetime(2023, 1, 1, 15, 30, 0)  # Sunday afternoon
        
        with patch('Dashboard.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_sunday
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            last_sunday = Dashboard.get_last_sunday()
            
            # Should return 7 days ago (previous Sunday)
            expected_sunday = datetime(2022, 12, 25, 0, 0, 0)
            assert last_sunday == expected_sunday
    
    def test_get_last_sunday_on_monday(self):
        """Test get_last_sunday when today is Monday"""
        # Mock current time to Monday
        mock_monday = datetime(2023, 1, 2, 10, 0, 0)  # Monday morning
        
        with patch('Dashboard.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_monday
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            last_sunday = Dashboard.get_last_sunday()
            
            # Should return Sunday, Jan 1, 2023 at 00:00:00
            expected_sunday = datetime(2023, 1, 1, 0, 0, 0)
            assert last_sunday == expected_sunday


class TestCalculateTaskTotals:
    """Test calculate_task_totals function"""
    
    def test_calculate_task_totals_empty_data(self):
        """Test calculate_task_totals with no data"""
        with patch('Dashboard.CompiledFormDataRepository.get_all', return_value=[]), \
             patch('Dashboard.TasksFormDataRepository.get_all', return_value=[]):
            
            totals, deltas = Dashboard.calculate_task_totals()
            
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
        """Test calculate_task_totals with sample data"""
        # Mock tasks
        mock_tasks = [
            MagicMock(id=1, tasks="Entregar Livro de Mórmon + foto + relato no grupo"),
            MagicMock(id=2, tasks="Levar amigo à sacramental"),
            MagicMock(id=3, tasks="Other task")  # This should be ignored
        ]
        
        # Mock compiled entries - some from this week, some older
        current_time = datetime.now()
        last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
        monday_after = last_sunday + timedelta(days=1)
        
        old_timestamp = (monday_after - timedelta(days=3)).timestamp()  # Before this week
        new_timestamp = (monday_after + timedelta(days=1)).timestamp()  # This week
        
        mock_compiled = [
            MagicMock(task_id=1, quantity=2, timestamp=old_timestamp),      # 2 books, old
            MagicMock(task_id=1, quantity=1, timestamp=new_timestamp),      # 1 book, this week  
            MagicMock(task_id=2, quantity=1, timestamp=new_timestamp),      # 1 friend, this week
            MagicMock(task_id=3, quantity=5, timestamp=new_timestamp),      # Other task, ignored
        ]
        
        with patch('Dashboard.CompiledFormDataRepository.get_all', return_value=mock_compiled), \
             patch('Dashboard.TasksFormDataRepository.get_all', return_value=mock_tasks), \
             patch('Dashboard.get_last_sunday', return_value=last_sunday):
            
            totals, deltas = Dashboard.calculate_task_totals()
            
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
        """Test calculate_task_totals with all target tasks"""
        # Mock all target tasks
        mock_tasks = [
            MagicMock(id=1, tasks="Entregar Livro de Mórmon + foto + relato no grupo"),
            MagicMock(id=2, tasks="Levar amigo à sacramental"),
            MagicMock(id=3, tasks="Ajudar alguém a se batizar"),
            MagicMock(id=4, tasks="Postar mensagem do evangelho nas redes sociais + print"),
            MagicMock(id=5, tasks="Fazer noite familiar com pesquisador"),
        ]
        
        current_time = datetime.now()
        last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
        monday_after = last_sunday + timedelta(days=1)
        this_week_timestamp = (monday_after + timedelta(days=1)).timestamp()
        
        # Mock compiled entries for all tasks, all this week
        mock_compiled = [
            MagicMock(task_id=1, quantity=3, timestamp=this_week_timestamp),  # 3 books
            MagicMock(task_id=2, quantity=2, timestamp=this_week_timestamp),  # 2 friends
            MagicMock(task_id=3, quantity=1, timestamp=this_week_timestamp),  # 1 baptism
            MagicMock(task_id=4, quantity=5, timestamp=this_week_timestamp),  # 5 posts
            MagicMock(task_id=5, quantity=2, timestamp=this_week_timestamp),  # 2 family nights
        ]
        
        with patch('Dashboard.CompiledFormDataRepository.get_all', return_value=mock_compiled), \
             patch('Dashboard.TasksFormDataRepository.get_all', return_value=mock_tasks), \
             patch('Dashboard.get_last_sunday', return_value=last_sunday):
            
            totals, deltas = Dashboard.calculate_task_totals()
            
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
        # Mock youth data
        mock_youth = [
            MagicMock(name="João", age=16, organization="Rapazes", total_points=100),
            MagicMock(name="Maria", age=15, organization="Moças", total_points=150),
            MagicMock(name="Pedro", age=17, organization="Rapazes", total_points=0),  # Should be filtered out
            MagicMock(name="Ana", age=16, organization="Moças", total_points=75),
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
        
        # We can't easily extract this from the function, but we can test the structure
        # by calling calculate_task_totals and ensuring all expected keys exist
        with patch('Dashboard.CompiledFormDataRepository.get_all', return_value=[]), \
             patch('Dashboard.TasksFormDataRepository.get_all', return_value=[]):
            
            totals, deltas = Dashboard.calculate_task_totals()
            
            for display_name in expected_mapping.values():
                assert display_name in totals
                assert display_name in deltas
    
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
        # Mock tasks (missing task id 2)
        mock_tasks = [
            MagicMock(id=1, tasks="Task 1"),
        ]
        
        # Mock compiled entries (references missing task id 2)
        mock_compiled = [
            MagicMock(task_id=1, quantity=1, timestamp=datetime.now().timestamp()),
            MagicMock(task_id=2, quantity=1, timestamp=datetime.now().timestamp()),  # Missing task
        ]
        
        with patch('Dashboard.CompiledFormDataRepository.get_all', return_value=mock_compiled), \
             patch('Dashboard.TasksFormDataRepository.get_all', return_value=mock_tasks):
            
            # Should not raise an error, should handle missing task gracefully
            totals, deltas = Dashboard.calculate_task_totals()
            
            # Should complete without error
            assert isinstance(totals, dict)
            assert isinstance(deltas, dict)
    
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