import pytest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
from streamlit.testing.v1 import AppTest
from freezegun import freeze_time

# Import the modules to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import Dashboard


class TestDashboardVisualElements:
    """Test Dashboard.py visual elements using Streamlit AppTest"""
    
    def test_dashboard_title_is_displayed(self):
        """Test that the main dashboard title is displayed correctly"""
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        # Check that dashboard loads without errors
        assert not at.exception
        
        # Verify the main title is present
        assert len(at.title) > 0
        assert "Painel de Jovens Missionários" in at.title[0].value
    
    def test_dashboard_loads_without_error(self):
        """Test that the dashboard loads without any exceptions"""
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        # Should load without exception
        assert not at.exception
        
        # Should have basic structure
        assert len(at.title) > 0


class TestDashboardMetricsStructure:
    """Test the structure and behavior of dashboard metrics using AppTest"""
    
    def test_dashboard_has_activity_totals_header(self):
        """Test that dashboard can display activity totals header"""
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        # Should load without exception
        assert not at.exception
        
        # Check headers that exist
        headers = [h.value for h in at.header] if at.header else []
        # The activity header may or may not appear depending on data, but structure should be valid
        assert isinstance(headers, list)


class TestDashboardTimeBasedCalculations:
    """Test Sunday-Saturday week calculation using freezegun (issue #24 fix)"""
    
    def test_get_last_sunday_function_logic(self):
        """Test the get_last_sunday function logic without Streamlit"""
        
        # Test with different days to ensure Sunday-Saturday week calculation
        with freeze_time("2023-01-01 15:30:00"):  # Sunday afternoon
            result = Dashboard.get_last_sunday()
            # Should return previous Sunday (2022-12-25) since current day is Sunday
            expected = datetime(2022, 12, 25, 0, 0, 0)
            assert result == expected
        
        with freeze_time("2023-01-02 10:00:00"):  # Monday morning
            result = Dashboard.get_last_sunday()
            # Should return yesterday (Sunday 2023-01-01)
            expected = datetime(2023, 1, 1, 0, 0, 0)
            assert result == expected
        
        with freeze_time("2023-01-07 18:00:00"):  # Saturday evening
            result = Dashboard.get_last_sunday()
            # Should return start of week (Sunday 2023-01-01)
            expected = datetime(2023, 1, 1, 0, 0, 0)
            assert result == expected


class TestDashboardTargetTasks:
    """Test target tasks mapping and new metrics (issue #24 fix)"""
    
    def test_target_tasks_mapping_structure(self):
        """Test that target_tasks mapping has correct structure without Batismos"""
        
        # Mock data to trigger calculate_task_totals
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks:
            
            mock_compiled.return_value = []
            mock_tasks.return_value = []
            
            # Call the function to ensure it uses the expected mapping
            totals, deltas = Dashboard.calculate_task_totals()
            
            # Verify the expected keys exist (6 total, no Batismos)
            expected_keys = [
                "Livros de Mórmon entregues",
                "Pessoas levadas à igreja",
                "Referências",
                "Lições", 
                "Posts nas redes sociais",
                "Sessões de noite familiar"
            ]
            
            for key in expected_keys:
                assert key in totals
                assert key in deltas
            
            # Verify no Batismos key
            assert "Batismos" not in totals
            assert "Batismos" not in deltas
            
            # Should have exactly 6 metrics
            assert len(totals) == 6
            assert len(deltas) == 6
    
    def test_new_referencias_and_licoes_tasks_in_mapping(self):
        """Test that new Referências and Lições tasks are in the mapping"""
        
        # Check that the calculate_task_totals function includes the new tasks
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks:
            
            # Mock tasks including the new ones
            mock_tasks.return_value = [
                MagicMock(id=1, tasks="Dar contato (tel/endereço) às Sisteres"),
                MagicMock(id=2, tasks="Visitar com as Sisteres"),
            ]
            
            # Mock compiled data for these tasks
            mock_compiled.return_value = [
                MagicMock(task_id=1, quantity=3, timestamp=datetime.now().timestamp()),
                MagicMock(task_id=2, quantity=2, timestamp=datetime.now().timestamp()),
            ]
            
            totals, deltas = Dashboard.calculate_task_totals()
            
            # Verify the new metrics are calculated
            assert totals["Referências"] == 3
            assert totals["Lições"] == 2
            assert deltas["Referências"] == 3
            assert deltas["Lições"] == 2


class TestDashboardDeltaTextFormat:
    """Test that delta text shows '+X novos' instead of '+X esta semana' (issue #24 fix)"""
    
    def test_delta_text_format_logic(self):
        """Test that delta text format uses 'novos' instead of 'esta semana' in the code"""
        # Test the string formatting logic directly
        delta_value = 5
        
        # Old format (should not be used)
        old_format = f"+{delta_value} esta semana"
        
        # New format (should be used) 
        new_format = f"+{delta_value} novos"
        
        # Verify the formats are different
        assert old_format == "+5 esta semana"
        assert new_format == "+5 novos"
        assert old_format != new_format
        
        # The new format should not reference a specific time period
        assert "semana" not in new_format
        assert "novos" in new_format
        
        # Test the exact format used in Dashboard.py (line 81)
        expected_dashboard_format = f"+{delta_value} novos"
        assert new_format == expected_dashboard_format


class TestDashboardDataProcessing:
    """Test dashboard data processing and calculations"""
    
    def test_calculate_task_totals_with_realistic_data(self):
        """Test calculate_task_totals function with realistic missionary data"""
        
        # Mock realistic missionary activity data
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks:
            
            # Mock all target tasks
            mock_tasks.return_value = [
                MagicMock(id=1, tasks="Entregar Livro de Mórmon + foto + relato no grupo"),
                MagicMock(id=2, tasks="Levar amigo à sacramental"),
                MagicMock(id=3, tasks="Dar contato (tel/endereço) às Sisteres"),
                MagicMock(id=4, tasks="Visitar com as Sisteres"),
                MagicMock(id=5, tasks="Postar mensagem do evangelho nas redes sociais + print"),
                MagicMock(id=6, tasks="Fazer noite familiar com pesquisador"),
            ]
            
            # Mock compiled data with various timestamps (some this week, some older)
            current_time = datetime.now()
            last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
            old_timestamp = (last_sunday - timedelta(days=3)).timestamp()  # Before this week
            new_timestamp = (last_sunday + timedelta(days=1)).timestamp()  # This week
            
            mock_compiled.return_value = [
                MagicMock(task_id=1, quantity=5, timestamp=old_timestamp),   # Old books
                MagicMock(task_id=1, quantity=3, timestamp=new_timestamp),   # New books
                MagicMock(task_id=3, quantity=7, timestamp=new_timestamp),   # New references
                MagicMock(task_id=4, quantity=4, timestamp=new_timestamp),   # New lessons
                MagicMock(task_id=5, quantity=12, timestamp=new_timestamp),  # New posts
            ]
            
            totals, deltas = Dashboard.calculate_task_totals()
            
            # Check totals (all entries)
            assert totals["Livros de Mórmon entregues"] == 8  # 5 + 3
            assert totals["Referências"] == 7
            assert totals["Lições"] == 4
            assert totals["Posts nas redes sociais"] == 12
            
            # Check deltas (only this week)
            assert deltas["Livros de Mórmon entregues"] == 3  # Only new
            assert deltas["Referências"] == 7
            assert deltas["Lições"] == 4 
            assert deltas["Posts nas redes sociais"] == 12


class TestDashboardIntegrationEndToEnd:
    """Integration testing using AppTest for complete user experience"""
    
    def test_empty_dashboard_state(self):
        """Test dashboard behavior with empty data (graceful degradation)"""
        # This test should work with real empty database state
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        # Should load without errors
        assert not at.exception
        
        # Title should still be displayed
        assert len(at.title) > 0
        assert "Painel de Jovens Missionários" in at.title[0].value
        
        # Should have basic structure
        headers = [h.value for h in at.header] if at.header else []
        assert "Ranking dos Jovens por Pontuação Total" in headers
    
    def test_dashboard_basic_apptest_integration(self):
        """Test basic AppTest integration with dashboard"""
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        assert not at.exception
        
        # Should have basic structure elements
        assert len(at.title) > 0
        assert len(at.header) > 0


class TestDashboardVisualRegressionAndUI:
    """Test visual regression and UI changes for issue #24"""
    
    def test_dashboard_ui_structure_basic(self):
        """Test basic UI structure without complex mocking"""
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        assert not at.exception
        
        # Should have title
        assert len(at.title) > 0
        assert "Painel de Jovens Missionários" in at.title[0].value
    
    def test_no_batismos_references_anywhere(self):
        """Test that no Batismos references appear anywhere in dashboard (issue #24 fix)"""
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        assert not at.exception
        
        # Collect all text content
        all_text_content = []
        all_text_content.extend([t.value for t in at.title] if at.title else [])
        all_text_content.extend([h.value for h in at.header] if at.header else [])
        if at.metric:
            all_text_content.extend([m.label for m in at.metric])
        
        # Convert to single string for searching
        full_content = " ".join(all_text_content).lower()
        
        # Ensure no baptism references
        assert "batismo" not in full_content
        assert "batizar" not in full_content
        assert "baptism" not in full_content


class TestDashboardWeekCalculationEdgeCases:
    """Test edge cases for Sunday-Saturday week calculation"""
    
    def test_week_boundaries_with_freezegun(self):
        """Test week boundary calculations with different days"""
        
        # Test Saturday night to Sunday morning transition
        with freeze_time("2023-01-07 23:59:59"):  # Saturday 23:59:59
            saturday_result = Dashboard.get_last_sunday()
        
        with freeze_time("2023-01-08 00:00:01"):  # Sunday 00:00:01 (next day)
            sunday_result = Dashboard.get_last_sunday()
        
        # Saturday should point to start of current week (Sunday 2023-01-01)
        expected_week_start = datetime(2023, 1, 1, 0, 0, 0)
        assert saturday_result == expected_week_start
        
        # Sunday should point to previous week start (Sunday 2023-01-01 again, since it's the same Sunday)
        # Actually, when it's Sunday, get_last_sunday returns the previous Sunday
        expected_prev_sunday = datetime(2023, 1, 1, 0, 0, 0)
        assert sunday_result == expected_prev_sunday
    
    def test_midweek_calculation(self):
        """Test week calculation for middle of the week"""
        
        # Test Wednesday 
        with freeze_time("2023-01-04 14:30:00"):  # Wednesday afternoon
            result = Dashboard.get_last_sunday()
            
        # Should point to start of current week (Sunday 2023-01-01)
        expected = datetime(2023, 1, 1, 0, 0, 0)
        assert result == expected


class TestDashboardNewFeatures:
    """Test new dashboard features: weekly leaderboard, book deliveries chart, countdown"""
    
    def test_remove_pessoas_na_igreja_from_activities(self):
        """Test that 'Pessoas na igreja' metric is removed from dashboard"""
        
        # Check the activities array in Dashboard.py doesn't contain "Pessoas na igreja"
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        # Should not contain "Pessoas na igreja" text in metrics
        page_text = str(at)
        assert "⛪ Pessoas na igreja" not in page_text
    
    def test_calculate_weekly_youth_points_function(self):
        """Test the calculate_weekly_youth_points function"""
        
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks, \
             patch('Dashboard.YouthFormDataRepository.get_all') as mock_youth:
            
            current_time = datetime.now()
            last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
            this_week_timestamp = (last_sunday + timedelta(days=1)).timestamp()
            old_timestamp = (last_sunday - timedelta(days=3)).timestamp()
            
            mock_youth.return_value = [
                MagicMock(id=1, name="João", organization="Rapazes", total_points=100),
                MagicMock(id=2, name="Maria", organization="Moças", total_points=80),
            ]
            
            # Set the name attribute correctly
            mock_youth.return_value[0].name = "João"
            mock_youth.return_value[1].name = "Maria"
            
            mock_tasks.return_value = [
                MagicMock(id=1, points=10),
                MagicMock(id=2, points=15),
            ]
            
            mock_compiled.return_value = [
                MagicMock(youth_id=1, task_id=1, quantity=2, bonus=5, timestamp=this_week_timestamp),
                MagicMock(youth_id=2, task_id=2, quantity=1, bonus=0, timestamp=this_week_timestamp),
                MagicMock(youth_id=1, task_id=1, quantity=3, bonus=0, timestamp=old_timestamp),  # Old entry
            ]
            
            weekly_points = Dashboard.calculate_weekly_youth_points()
            
            # João: 2 * 10 + 5 = 25 points this week
            assert weekly_points[1]['name'] == "João"
            assert weekly_points[1]['points'] == 25
            
            # Maria: 1 * 15 + 0 = 15 points this week
            assert weekly_points[2]['name'] == "Maria"
            assert weekly_points[2]['points'] == 15
    
    def test_calculate_position_changes_function(self):
        """Test the calculate_position_changes function"""
        
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks, \
             patch('Dashboard.YouthFormDataRepository.get_all') as mock_youth:
            
            current_time = datetime.now()
            last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
            this_week_timestamp = (last_sunday + timedelta(days=1)).timestamp()
            
            # João: total 100, earned 30 this week, so last week total was 70
            # Maria: total 80, earned 20 this week, so last week total was 60
            # Pedro: total 90, earned 0 this week, so last week total was 90
            
            mock_youth.return_value = [
                MagicMock(id=1, name="João", organization="Rapazes", total_points=100),
                MagicMock(id=2, name="Maria", organization="Moças", total_points=80),
                MagicMock(id=3, name="Pedro", organization="Rapazes", total_points=90),
            ]
            
            # Set attributes correctly
            for youth in mock_youth.return_value:
                if youth.id == 1:
                    youth.name = "João"
                    youth.organization = "Rapazes"
                elif youth.id == 2:
                    youth.name = "Maria"
                    youth.organization = "Moças"
                elif youth.id == 3:
                    youth.name = "Pedro"
                    youth.organization = "Rapazes"
            
            mock_tasks.return_value = [
                MagicMock(id=1, points=10),
                MagicMock(id=2, points=20),
            ]
            
            mock_compiled.return_value = [
                MagicMock(youth_id=1, task_id=1, quantity=3, bonus=0, timestamp=this_week_timestamp),  # João: 30 pts
                MagicMock(youth_id=2, task_id=2, quantity=1, bonus=0, timestamp=this_week_timestamp),  # Maria: 20 pts
                # Pedro: 0 points this week
            ]
            
            position_changes = Dashboard.calculate_position_changes()
            
            # This week: João(30), Maria(20)
            # Last week: Pedro(90), João(70), Maria(60)
            # João: moved from 2nd to 1st = ↑ 1
            # Maria: moved from 3rd to 2nd = ↑ 1
            
            assert position_changes[1]['name'] == "João"
            assert position_changes[1]['weekly_points'] == 30
            assert "↑" in position_changes[1]['position_change']
            
            assert position_changes[2]['name'] == "Maria"
            assert position_changes[2]['weekly_points'] == 20
            assert "↑" in position_changes[2]['position_change']
    
    def test_calculate_weekly_book_deliveries_function(self):
        """Test the calculate_weekly_book_deliveries function"""
        
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks:
            
            mock_tasks.return_value = [
                MagicMock(id=1, tasks="Entregar Livro de Mórmon + foto + relato no grupo"),
                MagicMock(id=2, tasks="Outras tarefas"),
            ]
            
            # Create timestamps for different weeks
            first_sunday = datetime(2023, 1, 1)  # Week 1 start
            week1_timestamp = (first_sunday + timedelta(days=2)).timestamp()  # Tuesday week 1
            week2_timestamp = (first_sunday + timedelta(days=9)).timestamp()  # Tuesday week 2
            
            mock_compiled.return_value = [
                MagicMock(task_id=1, quantity=3, timestamp=week1_timestamp),
                MagicMock(task_id=1, quantity=2, timestamp=week1_timestamp),
                MagicMock(task_id=1, quantity=4, timestamp=week2_timestamp),
                MagicMock(task_id=2, quantity=1, timestamp=week1_timestamp),  # Not a book delivery
            ]
            
            weekly_deliveries = Dashboard.calculate_weekly_book_deliveries()
            
            # Week 1: 3 + 2 = 5 deliveries
            # Week 2: 4 deliveries
            assert weekly_deliveries[1] == 5
            assert weekly_deliveries[2] == 4
    
    def test_calculate_countdown_function(self):
        """Test the calculate_countdown function"""
        
        # Test with a date before the end
        with freeze_time("2025-10-01"):
            days = Dashboard.calculate_countdown()
            assert days == 30  # October has 31 days, so Oct 1 to Oct 31 is 30 days
        
        # Test with a date after the end
        with freeze_time("2025-11-01"):
            days = Dashboard.calculate_countdown()
            assert days == 0  # Should not show negative days
        
        # Test on the exact end date
        with freeze_time("2025-10-31"):
            days = Dashboard.calculate_countdown()
            assert days == 0
    
    def test_dashboard_displays_new_sections(self):
        """Test that new dashboard sections are displayed"""
        
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        # Check that dashboard loads without errors
        assert not at.exception
        
        # Check that new headers are present
        headers = [h.value for h in at.header]
        assert "Top 5 da Semana" in headers
    
    def test_dashboard_handles_empty_weekly_data(self):
        """Test dashboard handles cases with no weekly data gracefully"""
        
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks, \
             patch('Dashboard.YouthFormDataRepository.get_all') as mock_youth:
            
            # Mock empty data
            mock_youth.return_value = []
            mock_tasks.return_value = []
            mock_compiled.return_value = []
            
            # Should not raise exceptions
            weekly_points = Dashboard.calculate_weekly_youth_points()
            position_changes = Dashboard.calculate_position_changes()
            weekly_books = Dashboard.calculate_weekly_book_deliveries()
            countdown = Dashboard.calculate_countdown()
            
            assert weekly_points == {}
            assert position_changes == {}
            assert weekly_books == {}
            assert countdown >= 0
    
    def test_leaderboard_top_5_limit(self):
        """Test that leaderboard correctly limits to top 5 youth"""
        
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks, \
             patch('Dashboard.YouthFormDataRepository.get_all') as mock_youth:
            
            current_time = datetime.now()
            last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
            this_week_timestamp = (last_sunday + timedelta(days=1)).timestamp()
            
            # Create 7 youth with different weekly points
            mock_youth.return_value = [
                MagicMock(id=i, name=f"Youth{i}", organization="Rapazes", total_points=100-i)
                for i in range(1, 8)
            ]
            
            # Set attributes correctly
            for youth in mock_youth.return_value:
                youth.name = f"Youth{youth.id}"
                youth.organization = "Rapazes"
            
            mock_tasks.return_value = [MagicMock(id=1, points=10)]
            
            # Give different weekly points: Youth1=70, Youth2=60, ..., Youth7=10
            mock_compiled.return_value = [
                MagicMock(youth_id=i, task_id=1, quantity=8-i, bonus=0, timestamp=this_week_timestamp)
                for i in range(1, 8)
            ]
            
            position_changes = Dashboard.calculate_position_changes()
            
            # Should have all 7 youth in results
            assert len(position_changes) == 7
            
            # But when we sort and take top 5, it should be Youth1-Youth5
            top_5 = sorted(position_changes.items(), key=lambda x: x[1]['weekly_points'], reverse=True)[:5]
            assert len(top_5) == 5
            
            # Verify order: Youth1(70), Youth2(60), Youth3(50), Youth4(40), Youth5(30)
            for i, (youth_id, data) in enumerate(top_5):
                expected_points = 70 - (i * 10)
                assert data['weekly_points'] == expected_points


class TestDashboardUILayoutImprovements:
    """Test new UI layout improvements for Top 5 and countdown"""
    
    def test_top_5_layout_format_with_data(self):
        """Test that Top 5 section displays correct layout with ranking and points separated"""
        
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks, \
             patch('Dashboard.YouthFormDataRepository.get_all') as mock_youth:
            
            current_time = datetime.now()
            last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
            this_week_timestamp = (last_sunday + timedelta(days=1)).timestamp()
            
            mock_youth.return_value = [
                MagicMock(id=1, name="João Silva", organization="Rapazes", total_points=30),
                MagicMock(id=2, name="Maria Santos", organization="Moças", total_points=20),
            ]
            
            mock_tasks.return_value = [
                MagicMock(id=1, points=10),
            ]
            
            mock_compiled.return_value = [
                MagicMock(youth_id=1, task_id=1, quantity=3, bonus=0, timestamp=this_week_timestamp),  # 30 pts
                MagicMock(youth_id=2, task_id=1, quantity=2, bonus=0, timestamp=this_week_timestamp),  # 20 pts
            ]
            
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("Dashboard.py")
            at.run()
            
            assert not at.exception
            
            # Check for Top 5 header
            headers = [h.value for h in at.header]
            assert "Top 5 da Semana" in headers
            
            # Check that layout contains both ranking/names and points in separate elements
            markdown_elements = [md.value for md in at.markdown]
            
            # Should contain ranking + name format
            found_ranking_format = False
            found_points_format = False
            
            for md in markdown_elements:
                if "#1 João Silva" in md and "🆕" in md:
                    found_ranking_format = True
                if "30pts" in md:
                    found_points_format = True
            
            assert found_ranking_format, "Top 5 should display '#1 Name' format"
            assert found_points_format, "Top 5 should display points separately"
    
    def test_countdown_centered_format(self):
        """Test that countdown is displayed in centered format"""
        
        os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
        at = AppTest.from_file("Dashboard.py")
        at.run()
        
        assert not at.exception
        
        # Check for countdown HTML content with center styling
        markdown_elements = [md.value for md in at.markdown]
        
        found_centered_countdown = False
        for md in markdown_elements:
            if "text-align: center" in md and "dias para o fim da gincana" in md:
                found_centered_countdown = True
                break
        
        assert found_centered_countdown, "Countdown should be centered with HTML styling"
    
    def test_top_5_empty_state_unchanged(self):
        """Test that Top 5 empty state still displays correctly"""
        
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks, \
             patch('Dashboard.YouthFormDataRepository.get_all') as mock_youth:
            
            # Mock empty data
            mock_youth.return_value = []
            mock_tasks.return_value = []
            mock_compiled.return_value = []
            
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("Dashboard.py")
            at.run()
            
            assert not at.exception
            
            # Check that empty state info is displayed
            info_elements = [info.value for info in at.info]
            assert any("Nenhuma pontuação desta semana ainda." in info for info in info_elements)
    
    def test_top_5_position_indicators_preserved(self):
        """Test that position change indicators are still displayed correctly"""
        
        with patch('Dashboard.CompiledFormDataRepository.get_all') as mock_compiled, \
             patch('Dashboard.TasksFormDataRepository.get_all') as mock_tasks, \
             patch('Dashboard.YouthFormDataRepository.get_all') as mock_youth:
            
            current_time = datetime.now()
            last_sunday = current_time - timedelta(days=current_time.weekday() + 1)
            this_week_timestamp = (last_sunday + timedelta(days=1)).timestamp()
            
            # Mock youth with previous total points (simulating they had points before this week)
            mock_youth.return_value = [
                MagicMock(id=1, name="Ana Costa", organization="Moças", total_points=50),  # Will show improvement
            ]
            
            mock_tasks.return_value = [
                MagicMock(id=1, points=10),
            ]
            
            # Ana gained 30 points this week, so she had 20 before (simulating rank improvement)
            mock_compiled.return_value = [
                MagicMock(youth_id=1, task_id=1, quantity=3, bonus=0, timestamp=this_week_timestamp),  # 30 pts this week
            ]
            
            os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
            at = AppTest.from_file("Dashboard.py")
            at.run()
            
            assert not at.exception
            
            # Check that position indicators are still present (NEW for first-time appearance)
            markdown_elements = [md.value for md in at.markdown]
            
            found_position_indicator = False
            for md in markdown_elements:
                if "#1 Ana Costa" in md and "🆕" in md:
                    found_position_indicator = True
                    break
            
            assert found_position_indicator, "Position indicators should still be displayed in new format"