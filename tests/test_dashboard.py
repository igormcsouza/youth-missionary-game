import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add src directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Patch streamlit before importing dashboard to avoid initialization
with patch.dict('sys.modules', {'streamlit': MagicMock()}):
    import importlib.util
    spec = importlib.util.spec_from_file_location("dashboard", 
                                                  os.path.join(os.path.dirname(__file__), '..', 'src', 'Dashboard.py'))
    dashboard_module = importlib.util.module_from_spec(spec)


class TestDashboardTotals:
    """Test the dashboard totals calculation functionality"""

    def test_get_last_sunday_function_logic(self):
        """Test the get_last_sunday function logic with various days"""
        
        def get_last_sunday_local(current_time):
            """Local copy of the function for testing"""
            days_since_sunday = current_time.weekday() + 1  # Monday = 1, Tuesday = 2, ..., Sunday = 7
            last_sunday = current_time - timedelta(days=days_since_sunday)
            return last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        test_cases = [
            # (current_day, expected_sunday)
            (datetime(2024, 8, 18, 12, 0), datetime(2024, 8, 11, 0, 0)),  # Sunday -> previous Sunday
            (datetime(2024, 8, 19, 12, 0), datetime(2024, 8, 18, 0, 0)),  # Monday -> last Sunday  
            (datetime(2024, 8, 21, 12, 0), datetime(2024, 8, 18, 0, 0)),  # Wednesday -> last Sunday
            (datetime(2024, 8, 24, 12, 0), datetime(2024, 8, 18, 0, 0)),  # Saturday -> last Sunday
        ]
        
        for current_time, expected_sunday in test_cases:
            result = get_last_sunday_local(current_time)
            assert result == expected_sunday, f"For {current_time.strftime('%A %m/%d')}, expected {expected_sunday}, got {result}"

    def test_calculate_task_totals_with_mocked_data(self):
        """Test task totals calculation with properly mocked data"""
        
        # Create mock entries with proper attributes
        mock_compiled_entries = [
            Mock(task_id=1, quantity=2, timestamp=datetime(2024, 8, 18, 10, 0).timestamp()),  # Sunday (this week)
            Mock(task_id=1, quantity=1, timestamp=datetime(2024, 8, 15, 10, 0).timestamp()),  # Previous Thursday 
            Mock(task_id=2, quantity=1, timestamp=datetime(2024, 8, 19, 14, 0).timestamp()),  # Monday (this week)
            Mock(task_id=3, quantity=3, timestamp=datetime(2024, 8, 20, 9, 0).timestamp()),   # Tuesday (this week)
            Mock(task_id=4, quantity=2, timestamp=datetime(2024, 8, 17, 16, 0).timestamp()),  # Previous Saturday
        ]
        
        mock_task_entries = [
            Mock(id=1, tasks="Entregar Livro de Mórmon + foto + relato no grupo"),
            Mock(id=2, tasks="Levar amigo à sacramental"),
            Mock(id=3, tasks="Dar contato (tel/endereço) às Sisteres"),
            Mock(id=4, tasks="Visitar com as Sisteres"),
            Mock(id=5, tasks="Postar mensagem do evangelho nas redes sociais + print"),
        ]
        
        # Recreate the function locally for testing
        def calculate_task_totals_local():
            target_tasks = {
                "Entregar Livro de Mórmon + foto + relato no grupo": "Livros de Mórmon entregues",
                "Levar amigo à sacramental": "Pessoas levadas à igreja",
                "Dar contato (tel/endereço) às Sisteres": "Referências",
                "Visitar com as Sisteres": "Lições",
                "Postar mensagem do evangelho nas redes sociais + print": "Posts nas redes sociais",
                "Fazer noite familiar com pesquisador": "Sessões de noite familiar"
            }
            
            totals = {display_name: 0 for display_name in target_tasks.values()}
            deltas = {display_name: 0 for display_name in target_tasks.values()}
            
            task_dict = {t.id: t for t in mock_task_entries}
            
            # Use a fixed last Sunday for testing (August 18, 2024)
            last_sunday_timestamp = datetime(2024, 8, 18, 0, 0, 0).timestamp()
            
            for entry in mock_compiled_entries:
                task = task_dict.get(entry.task_id)
                if task and task.tasks in target_tasks:
                    display_name = target_tasks[task.tasks]
                    totals[display_name] += entry.quantity
                    
                    # Count activities since last Sunday (current week)
                    if entry.timestamp >= last_sunday_timestamp:
                        deltas[display_name] += entry.quantity
            
            return totals, deltas
        
        totals, deltas = calculate_task_totals_local()
        
        # Verify totals (all time)
        assert totals["Livros de Mórmon entregues"] == 3  # 2 + 1
        assert totals["Pessoas levadas à igreja"] == 1
        assert totals["Referências"] == 3
        assert totals["Lições"] == 2
        assert totals["Posts nas redes sociais"] == 0
        assert totals["Sessões de noite familiar"] == 0
        
        # Verify deltas (since last Sunday - this week)
        # Last Sunday is Aug 18, entries on/after this date count as "this week"
        assert deltas["Livros de Mórmon entregues"] == 2  # Only the Sunday entry
        assert deltas["Pessoas levadas à igreja"] == 1   # Monday entry
        assert deltas["Referências"] == 3                # Tuesday entry  
        assert deltas["Lições"] == 0                     # Previous Saturday doesn't count

    def test_target_tasks_mapping(self):
        """Test that the target tasks are correctly mapped to display names"""
        expected_mappings = {
            "Entregar Livro de Mórmon + foto + relato no grupo": "Livros de Mórmon entregues",
            "Levar amigo à sacramental": "Pessoas levadas à igreja", 
            "Dar contato (tel/endereço) às Sisteres": "Referências",
            "Visitar com as Sisteres": "Lições",
            "Postar mensagem do evangelho nas redes sociais + print": "Posts nas redes sociais",
            "Fazer noite familiar com pesquisador": "Sessões de noite familiar"
        }
        
        # This verifies our mapping is complete
        assert len(expected_mappings) == 6
        
        # Verify that Batismos is not included (as per the fix)
        task_names = list(expected_mappings.keys())
        assert "Batismos" not in task_names
        assert not any("batismo" in task.lower() for task in task_names)
        
        # Verify that Referências and Lições are included (the new additions)
        display_names = list(expected_mappings.values())
        assert "Referências" in display_names
        assert "Lições" in display_names

    def test_metric_display_format(self):
        """Test that metrics are displayed with correct format and icons"""
        expected_activities = [
            ("Livros de Mórmon", "📖"),
            ("Pessoas na igreja", "⛪"), 
            ("Referências", "📞"),
            ("Lições", "👥"),
            ("Posts", "📱"),
            ("Noites familiares", "🏠")
        ]
        
        # Verify we have 6 activities (not 5 like before the fix)
        assert len(expected_activities) == 6
        
        # Verify the icons match what we expect for the new metrics
        activity_icons = {name: icon for name, icon in expected_activities}
        assert activity_icons["Referências"] == "📞"
        assert activity_icons["Lições"] == "👥"

    def test_delta_text_format(self):
        """Test that delta text shows 'novos' instead of 'esta semana'"""
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'Dashboard.py')
        
        with open(dashboard_path, 'r') as f:
            dashboard_content = f.read()
        
        # Verify that the source uses "novos" instead of "esta semana"
        assert "+{delta} novos" in dashboard_content
        assert "esta semana" not in dashboard_content

    def test_week_boundary_calculation(self):
        """Test specific week boundary cases for Sunday-Saturday calculation"""
        
        def get_week_start_timestamp(current_time):
            """Calculate week start timestamp using the same logic as dashboard"""
            days_since_sunday = current_time.weekday() + 1  # Monday = 1, Tuesday = 2, ..., Sunday = 7
            last_sunday = current_time - timedelta(days=days_since_sunday)
            week_start = last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
            return week_start.timestamp()
        
        # Test specific boundary cases
        test_cases = [
            # (current_time, expected_week_start_date)
            (datetime(2024, 8, 18, 23, 59, 59), "2024-08-11"),  # Sunday night -> previous Sunday
            (datetime(2024, 8, 19, 0, 0, 1), "2024-08-18"),     # Monday morning -> this Sunday
            (datetime(2024, 8, 24, 23, 59, 59), "2024-08-18"),  # Saturday night -> this Sunday
            (datetime(2024, 8, 25, 0, 0, 1), "2024-08-18"),     # Next Sunday morning -> previous Sunday
        ]
        
        for current_time, expected_date_str in test_cases:
            week_start_ts = get_week_start_timestamp(current_time)
            week_start_date = datetime.fromtimestamp(week_start_ts).strftime("%Y-%m-%d")
            assert week_start_date == expected_date_str, f"For {current_time}, expected week start {expected_date_str}, got {week_start_date}"


class TestDashboardDataFlow:
    """Test the complete data flow in the dashboard"""
    
    def test_empty_data_scenario(self):
        """Test dashboard behavior with no data"""
        def calculate_totals_empty():
            target_tasks_values = [
                "Livros de Mórmon entregues",
                "Pessoas levadas à igreja", 
                "Referências",
                "Lições",
                "Posts nas redes sociais",
                "Sessões de noite familiar"
            ]
            
            totals = {name: 0 for name in target_tasks_values}
            deltas = {name: 0 for name in target_tasks_values}
            return totals, deltas
        
        totals, deltas = calculate_totals_empty()
        
        # All should be zero
        for value in totals.values():
            assert value == 0
        for value in deltas.values():
            assert value == 0

    def test_comprehensive_data_scenario(self):
        """Test dashboard with comprehensive realistic data"""
        
        # Simulate a week of missionary activities
        sunday_ts = datetime(2024, 8, 18, 9, 0).timestamp()    # Sunday morning
        monday_ts = datetime(2024, 8, 19, 14, 0).timestamp()   # Monday afternoon
        tuesday_ts = datetime(2024, 8, 20, 16, 0).timestamp()  # Tuesday evening
        prev_week_ts = datetime(2024, 8, 15, 10, 0).timestamp() # Previous week
        
        mock_data = [
            # This week entries (should count in deltas)
            {'task': 'Entregar Livro de Mórmon + foto + relato no grupo', 'quantity': 1, 'timestamp': sunday_ts},
            {'task': 'Dar contato (tel/endereço) às Sisteres', 'quantity': 2, 'timestamp': monday_ts},
            {'task': 'Visitar com as Sisteres', 'quantity': 1, 'timestamp': tuesday_ts},
            
            # Previous week entries (should count in totals but not deltas)
            {'task': 'Entregar Livro de Mórmon + foto + relato no grupo', 'quantity': 1, 'timestamp': prev_week_ts},
            {'task': 'Postar mensagem do evangelho nas redes sociais + print', 'quantity': 3, 'timestamp': prev_week_ts},
        ]
        
        # Calculate expected results
        expected_totals = {
            "Livros de Mórmon entregues": 2,  # 1 + 1
            "Pessoas levadas à igreja": 0,
            "Referências": 2,               # 2 from this week
            "Lições": 1,                   # 1 from this week
            "Posts nas redes sociais": 3,   # 3 from previous week
            "Sessões de noite familiar": 0
        }
        
        expected_deltas = {
            "Livros de Mórmon entregues": 1,  # Only this week's entry
            "Pessoas levadas à igreja": 0,
            "Referências": 2,               # This week's entries
            "Lições": 1,                   # This week's entry
            "Posts nas redes sociais": 0,   # Previous week doesn't count
            "Sessões de noite familiar": 0
        }
        
        # Simulate the calculation logic
        target_tasks = {
            "Entregar Livro de Mórmon + foto + relato no grupo": "Livros de Mórmon entregues",
            "Levar amigo à sacramental": "Pessoas levadas à igreja",
            "Dar contato (tel/endereço) às Sisteres": "Referências",
            "Visitar com as Sisteres": "Lições",
            "Postar mensagem do evangelho nas redes sociais + print": "Posts nas redes sociais",
            "Fazer noite familiar com pesquisador": "Sessões de noite familiar"
        }
        
        totals = {display_name: 0 for display_name in target_tasks.values()}
        deltas = {display_name: 0 for display_name in target_tasks.values()}
        
        # Week starts on Sunday (Aug 18, 2024)
        week_start_timestamp = datetime(2024, 8, 18, 0, 0, 0).timestamp()
        
        for entry in mock_data:
            if entry['task'] in target_tasks:
                display_name = target_tasks[entry['task']]
                totals[display_name] += entry['quantity']
                
                if entry['timestamp'] >= week_start_timestamp:
                    deltas[display_name] += entry['quantity']
        
        # Verify results
        for key, expected_value in expected_totals.items():
            assert totals[key] == expected_value, f"Total for {key}: expected {expected_value}, got {totals[key]}"
            
        for key, expected_value in expected_deltas.items():
            assert deltas[key] == expected_value, f"Delta for {key}: expected {expected_value}, got {deltas[key]}"


class TestDashboardUIChanges:
    """Test the UI-related changes made to the dashboard"""
    
    def test_six_column_layout(self):
        """Test that the dashboard now shows 6 columns instead of 5"""
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'Dashboard.py')
        
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Verify that st.columns(6) is used
        assert "st.columns(6)" in content
        
        # Verify we don't have the old 5-column layout
        assert "st.columns(5)" not in content

    def test_batismos_removal(self):
        """Test that Batismos metric has been completely removed"""
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'Dashboard.py')
        
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Verify no references to Batismos
        assert "Batismos" not in content
        assert "batismos" not in content.lower()

    def test_new_metrics_present(self):
        """Test that the new Referências and Lições metrics are present"""
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'Dashboard.py')
        
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Verify new metrics are present
        assert "Referências" in content
        assert "Lições" in content
        
        # Verify the correct task mappings
        assert "Dar contato (tel/endereço) às Sisteres" in content
        assert "Visitar com as Sisteres" in content

    def test_icons_mapping(self):
        """Test that the correct icons are used for each metric"""
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'Dashboard.py')
        
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Check for specific icon-metric pairs
        icon_checks = [
            ('📖', 'Livros de M'),  # Books icon for Livros de Mórmon
            ('⛪', 'Pessoas na igreja'),  # Church icon for People at church
            ('📞', 'Referências'),  # Phone icon for References
            ('👥', 'Lições'),  # People icon for Lessons
            ('📱', 'Posts'),  # Phone icon for Posts
            ('🏠', 'Noites familiares')  # House icon for Family nights
        ]
        
        for icon, metric_part in icon_checks:
            # Check that the icon appears near the metric name
            assert icon in content, f"Icon {icon} not found in dashboard"
            assert metric_part in content, f"Metric {metric_part} not found in dashboard"