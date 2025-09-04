import datetime as dt
import os
import sys
import time
from unittest.mock import patch

import pytest
from sqlmodel import SQLModel, create_engine

# Import the modules to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database import (
    CompiledFormDataRepository,
    TasksFormDataRepository,
    YouthFormDataRepository,
)
from utils import check_password


@pytest.mark.integration
class TestCompleteWorkflow:
    """Integration tests for the complete application workflow"""

    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Set up in-memory database for integration tests"""
        self.test_engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.test_engine)

        with patch("database.engine", self.test_engine):
            yield

    def test_complete_youth_task_workflow(self):
        """Test complete workflow: add youth -> add task -> record
        completion -> verify results"""
        with patch("database.engine", self.test_engine):
            # Step 1: Add a youth
            youth = YouthFormDataRepository.store(
                name="João Silva",
                age=16,
                organization="Rapazes",
                total_points=0,
            )

            assert youth is not None
            assert youth.name == "João Silva"
            assert youth.total_points == 0

            # Step 2: Add a task
            task = TasksFormDataRepository.store(
                tasks="Read scriptures", points=10, repeatable=True
            )

            assert task is not None
            assert task.tasks == "Read scriptures"
            assert task.points == 10
            assert task.repeatable is True

            # Step 3: Record task completion
            timestamp = time.time()
            compiled_entry = CompiledFormDataRepository.store(
                youth_id=youth.id,
                task_id=task.id,
                timestamp=timestamp,
                quantity=2,
                bonus=5,
            )

            assert compiled_entry is not None
            assert compiled_entry.youth_id == youth.id
            assert compiled_entry.task_id == task.id
            assert compiled_entry.quantity == 2
            assert compiled_entry.bonus == 5

            # Step 4: Calculate and update total points
            compiled_entries = CompiledFormDataRepository.get_all()
            task_by_id = {t.id: t for t in TasksFormDataRepository.get_all()}

            total_points = 0
            for entry in compiled_entries:
                if entry.youth_id == youth.id:
                    task_obj = task_by_id.get(entry.task_id)
                    if task_obj:
                        total_points += (
                            task_obj.points * entry.quantity + entry.bonus
                        )

            # Update youth total points
            YouthFormDataRepository.update_total_points(youth.id, total_points)

            # Step 5: Verify final state
            updated_youth = YouthFormDataRepository.get_all()[0]
            assert updated_youth.total_points == 25  # 10*2 + 5 = 25

            all_compiled = CompiledFormDataRepository.get_all()
            assert len(all_compiled) == 1

            all_tasks = TasksFormDataRepository.get_all()
            assert len(all_tasks) == 1

    def test_multiple_youth_multiple_tasks_workflow(self):
        """Test workflow with multiple youth and tasks"""
        with patch("database.engine", self.test_engine):
            # Add multiple youth
            youth1 = YouthFormDataRepository.store("João", 16, "Rapazes", 0)
            youth2 = YouthFormDataRepository.store("Maria", 15, "Moças", 0)

            # Add multiple tasks
            task1 = TasksFormDataRepository.store("Read scriptures", 10, True)
            task2 = TasksFormDataRepository.store("Attend church", 20, False)

            # Record multiple completions
            timestamp = time.time()

            # João completes both tasks
            CompiledFormDataRepository.store(
                youth1.id, task1.id, timestamp, 3, 0
            )  # 30 points
            CompiledFormDataRepository.store(
                youth1.id, task2.id, timestamp, 1, 5
            )  # 25 points

            # Maria completes one task
            CompiledFormDataRepository.store(
                youth2.id, task1.id, timestamp, 2, 10
            )  # 30 points

            # Calculate total points for all youth
            compiled_entries = CompiledFormDataRepository.get_all()
            task_by_id = {t.id: t for t in TasksFormDataRepository.get_all()}

            for youth in YouthFormDataRepository.get_all():
                total_points = 0
                for entry in compiled_entries:
                    if entry.youth_id == youth.id:
                        task_obj = task_by_id.get(entry.task_id)
                        if task_obj:
                            total_points += (
                                task_obj.points * entry.quantity + entry.bonus
                            )
                YouthFormDataRepository.update_total_points(
                    youth.id, total_points
                )

            # Verify results
            all_youth = YouthFormDataRepository.get_all()
            youth_by_name = {y.name: y for y in all_youth}

            assert youth_by_name["João"].total_points == 55  # 30 + 25
            assert youth_by_name["Maria"].total_points == 30  # 30

            # Verify data consistency
            assert len(CompiledFormDataRepository.get_all()) == 3
            assert len(TasksFormDataRepository.get_all()) == 2
            assert len(YouthFormDataRepository.get_all()) == 2

    def test_non_repeatable_task_workflow(self):
        """Test workflow with non-repeatable tasks"""
        with patch("database.engine", self.test_engine):
            # Add youth and non-repeatable task
            youth = YouthFormDataRepository.store("Pedro", 17, "Rapazes", 0)
            task = TasksFormDataRepository.store("Special event", 50, False)

            timestamp = time.time()

            # Record first completion
            entry1 = CompiledFormDataRepository.store(
                youth.id, task.id, timestamp, 1, 0
            )
            assert entry1 is not None

            # Check if entry exists today
            has_entry = CompiledFormDataRepository.has_entry_today(
                youth.id, task.id
            )
            assert has_entry is True

            # Simulate validation logic from page
            is_repeatable = task.repeatable
            quantity = 1

            # Should prevent second entry for non-repeatable task on same day
            should_allow_entry = not (not is_repeatable and has_entry)
            assert should_allow_entry is False

            # Should prevent quantity > 1 for non-repeatable task
            quantity = 2
            should_allow_quantity = not (not is_repeatable and quantity > 1)
            assert should_allow_quantity is False

    def test_authentication_workflow(self):
        """Test authentication workflow"""
        # Test without AUTH environment variable
        with patch.dict(os.environ, {}, clear=True):
            with patch("streamlit.error") as mock_error:
                result = check_password()
                assert result is False
                mock_error.assert_called_once()

        # Test with AUTH environment variable
        with patch.dict(os.environ, {"AUTH": "test_password"}):
            # Simulate correct password entry
            with patch("streamlit.session_state", {"password_correct": True}):
                result = check_password()
                assert result is True

            # Simulate incorrect password entry
            with patch("streamlit.session_state", {"password_correct": False}):
                with patch("streamlit.text_input"), patch("streamlit.error"):
                    result = check_password()
                    assert result is False


@pytest.mark.integration
class TestDashboardDataIntegration:
    """Integration tests for dashboard data processing"""

    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Set up in-memory database for dashboard tests"""
        self.test_engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.test_engine)

        with patch("database.engine", self.test_engine):
            yield

    def test_dashboard_missionary_activities_calculation(self):
        """Test missionary activities calculation with real data"""
        with patch("database.engine", self.test_engine):
            # Add youth
            youth1 = YouthFormDataRepository.store("João", 16, "Rapazes", 0)
            youth2 = YouthFormDataRepository.store("Maria", 15, "Moças", 0)

            # Add missionary tasks
            book_task = TasksFormDataRepository.store(
                "Entregar Livro de Mórmon + foto + relato no grupo", 50, True
            )
            church_task = TasksFormDataRepository.store(
                "Levar amigo à sacramental", 25, True
            )
            baptism_task = TasksFormDataRepository.store(
                "Ajudar alguém a se batizar", 100, False
            )

            # Record activities with different timestamps
            current_time = dt.datetime.now()
            this_week = current_time.timestamp()
            last_week = (current_time - dt.timedelta(days=7)).timestamp()

            # Add activities from different time periods
            CompiledFormDataRepository.store(
                youth1.id, book_task.id, last_week, 2, 0
            )  # Last week
            CompiledFormDataRepository.store(
                youth1.id, book_task.id, this_week, 1, 0
            )  # This week
            CompiledFormDataRepository.store(
                youth2.id, church_task.id, this_week, 3, 0
            )  # This week
            CompiledFormDataRepository.store(
                youth1.id, baptism_task.id, this_week, 1, 0
            )  # This week

            # Apply dashboard calculation logic
            compiled_entries = CompiledFormDataRepository.get_all()
            task_entries = TasksFormDataRepository.get_all()
            task_dict = {t.id: t for t in task_entries}

            # Define target tasks mapping (from Dashboard.py)
            target_tasks = {
                ("Entregar Livro de Mórmon + foto + relato no grupo"):
                    "Livros de Mórmon entregues",
                "Levar amigo à sacramental": "Pessoas levadas à igreja",
                "Ajudar alguém a se batizar": "Batismos",
                ("Postar mensagem do evangelho nas redes sociais + print"):
                    "Posts nas redes sociais",
                ("Fazer noite familiar com pesquisador"):
                    "Sessões de noite familiar",
            }

            # Calculate totals and deltas
            totals = dict.fromkeys(target_tasks.values(), 0)
            deltas = dict.fromkeys(target_tasks.values(), 0)

            # Calculate Monday after last Sunday timestamp
            last_sunday = current_time - dt.timedelta(
                days=current_time.weekday() + 1
            )
            monday_after = last_sunday + dt.timedelta(days=1)
            monday_timestamp = monday_after.timestamp()

            for entry in compiled_entries:
                task = task_dict.get(entry.task_id)
                if task and task.tasks in target_tasks:
                    display_name = target_tasks[task.tasks]
                    totals[display_name] += entry.quantity

                    if entry.timestamp >= monday_timestamp:
                        deltas[display_name] += entry.quantity

            # Verify calculations
            assert totals["Livros de Mórmon entregues"] == 3  # 2 + 1
            assert totals["Pessoas levadas à igreja"] == 3
            assert totals["Batismos"] == 1

            # Deltas should only count this week's activities
            assert (
                deltas["Livros de Mórmon entregues"] == 1
            )  # Only this week's entry
            assert deltas["Pessoas levadas à igreja"] == 3
            assert deltas["Batismos"] == 1

    def test_dashboard_ranking_calculation(self):
        """Test youth ranking calculation with real data"""
        with patch("database.engine", self.test_engine):
            # Add youth with different scores
            YouthFormDataRepository.store("João", 16, "Rapazes", 100)
            YouthFormDataRepository.store("Maria", 15, "Moças", 150)
            YouthFormDataRepository.store("Pedro", 17, "Rapazes", 0)
            YouthFormDataRepository.store("Ana", 16, "Moças", 75)

            # Apply dashboard ranking logic
            youth_entries = YouthFormDataRepository.get_all()
            filtered_youth = [y for y in youth_entries if y.total_points > 0]
            sorted_youth = sorted(
                filtered_youth, key=lambda y: y.total_points, reverse=True
            )

            # Verify ranking
            assert len(sorted_youth) == 3  # Pedro filtered out (0 points)
            assert sorted_youth[0].name == "Maria"  # 150 points
            assert sorted_youth[1].name == "João"  # 100 points
            assert sorted_youth[2].name == "Ana"  # 75 points

            # Create ranking DataFrame (as in Dashboard.py)
            ranking_data = [
                {
                    "Ranking": idx + 1,
                    "Nome": y.name,
                    "Idade": y.age,
                    "Organização": y.organization,
                    "Pontuação Total": y.total_points,
                }
                for idx, y in enumerate(sorted_youth)
            ]

            assert len(ranking_data) == 3
            assert ranking_data[0]["Ranking"] == 1
            assert ranking_data[0]["Nome"] == "Maria"
            assert ranking_data[1]["Ranking"] == 2
            assert ranking_data[1]["Nome"] == "João"

    def test_dashboard_organization_points_calculation(self):
        """Test organization points calculation"""
        with patch("database.engine", self.test_engine):
            # Add youth from different organizations
            YouthFormDataRepository.store("João", 16, "Rapazes", 100)
            YouthFormDataRepository.store("Pedro", 17, "Rapazes", 50)
            YouthFormDataRepository.store("Maria", 15, "Moças", 150)
            YouthFormDataRepository.store("Ana", 16, "Moças", 75)
            YouthFormDataRepository.store("Lucia", 14, "Moças", 25)

            # Apply dashboard organization calculation
            youth_entries = YouthFormDataRepository.get_all()
            young_man_points = sum(
                y.total_points
                for y in youth_entries
                if y.organization == "Rapazes"
            )
            young_woman_points = sum(
                y.total_points
                for y in youth_entries
                if y.organization == "Moças"
            )

            assert young_man_points == 150  # 100 + 50
            assert young_woman_points == 250  # 150 + 75 + 25

    def test_dashboard_task_points_calculation(self):
        """Test task points calculation for pie chart"""
        with patch("database.engine", self.test_engine):
            # Add tasks and youth
            task1 = TasksFormDataRepository.store("Task 1", 10, True)
            task2 = TasksFormDataRepository.store("Task 2", 20, True)
            task3 = TasksFormDataRepository.store("Task 3", 5, True)

            youth = YouthFormDataRepository.store(
                "Test Youth", 16, "Rapazes", 0
            )

            # Record task completions
            timestamp = time.time()
            CompiledFormDataRepository.store(
                youth.id, task1.id, timestamp, 2, 5
            )  # 10*2+5 = 25
            CompiledFormDataRepository.store(
                youth.id, task1.id, timestamp, 1, 0
            )  # 10*1+0 = 10
            CompiledFormDataRepository.store(
                youth.id, task2.id, timestamp, 1, 10
            )  # 20*1+10 = 30
            CompiledFormDataRepository.store(
                youth.id, task3.id, timestamp, 3, 0
            )  # 5*3+0 = 15

            # Apply dashboard task points calculation
            compiled_entries = CompiledFormDataRepository.get_all()
            task_entries = TasksFormDataRepository.get_all()
            task_dict = {t.id: t for t in task_entries}
            task_points = {}

            for entry in compiled_entries:
                task = task_dict.get(entry.task_id)
                if task:
                    points = task.points * entry.quantity + entry.bonus
                    task_points[task.tasks] = (
                        task_points.get(task.tasks, 0) + points
                    )

            # Verify task points calculation
            assert task_points["Task 1"] == 35  # 25 + 10
            assert task_points["Task 2"] == 30
            assert task_points["Task 3"] == 15


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling across the application"""

    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Set up in-memory database for error tests"""
        self.test_engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.test_engine)

        with patch("database.engine", self.test_engine):
            yield

    def test_database_operation_error_recovery(self):
        """Test error recovery in database operations"""
        with patch("database.engine", self.test_engine):
            # Test successful operation
            youth = YouthFormDataRepository.store("Test", 16, "Rapazes", 0)
            assert youth is not None

            # Test error handling with mock
            with patch("database.handle_database_operation") as mock_handler:
                mock_handler.return_value = None

                # This should return None due to mock
                result = YouthFormDataRepository.store(
                    "Test2", 16, "Rapazes", 0
                )
                assert result is None

                # get_all should return empty list on error
                result = YouthFormDataRepository.get_all()
                assert result == []

    def test_missing_data_handling(self):
        """Test handling of missing or inconsistent data"""
        with patch("database.engine", self.test_engine):
            # Add youth and task
            youth = YouthFormDataRepository.store("Test", 16, "Rapazes", 0)
            task = TasksFormDataRepository.store("Test Task", 10, True)

            # Add compiled entry
            CompiledFormDataRepository.store(
                youth.id, task.id, time.time(), 1, 0
            )

            # Delete the task (simulating missing foreign key)
            TasksFormDataRepository.delete(task.id)

            # Points calculation should handle missing task gracefully
            compiled_entries = CompiledFormDataRepository.get_all()
            task_by_id = {t.id: t for t in TasksFormDataRepository.get_all()}

            total_points = 0
            for entry in compiled_entries:
                if entry.youth_id == youth.id:
                    task_obj = task_by_id.get(entry.task_id)
                    if task_obj:  # This should be None now
                        total_points += (
                            task_obj.points * entry.quantity + entry.bonus
                        )

            # Should be 0 since task was deleted
            assert total_points == 0

    def test_edge_case_data_values(self):
        """Test handling of edge case data values"""
        with patch("database.engine", self.test_engine):
            # Test edge case values
            youth = YouthFormDataRepository.store(
                "", 0, "Rapazes", 0
            )  # Empty name, age 0
            assert youth is not None  # Database should accept this

            task = TasksFormDataRepository.store(
                "", 0, False
            )  # Empty task, 0 points
            assert task is not None

            # Test with very large values
            large_youth = YouthFormDataRepository.store(
                "X" * 100, 120, "Moças", 999999
            )
            assert large_youth is not None

            large_task = TasksFormDataRepository.store("Y" * 200, 999999, True)
            assert large_task is not None


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Integration tests for performance with larger datasets"""

    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Set up in-memory database for performance tests"""
        self.test_engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.test_engine)

        with patch("database.engine", self.test_engine):
            yield

    def test_large_dataset_operations(self):
        """Test operations with larger datasets"""
        with patch("database.engine", self.test_engine):
            # Add many youth
            youth_ids = []
            for i in range(50):
                org = "Rapazes" if i % 2 == 0 else "Moças"
                youth = YouthFormDataRepository.store(
                    f"Youth {i}", 15 + (i % 6), org, 0
                )
                youth_ids.append(youth.id)

            # Add many tasks
            task_ids = []
            for i in range(20):
                task = TasksFormDataRepository.store(
                    f"Task {i}", 5 + (i % 10), i % 2 == 0
                )
                task_ids.append(task.id)

            # Add many compiled entries
            timestamp = time.time()
            for i in range(200):
                youth_id = youth_ids[i % len(youth_ids)]
                task_id = task_ids[i % len(task_ids)]
                CompiledFormDataRepository.store(
                    youth_id, task_id, timestamp, 1 + (i % 3), i % 5
                )

            # Test retrieval performance
            all_youth = YouthFormDataRepository.get_all()
            all_tasks = TasksFormDataRepository.get_all()
            all_compiled = CompiledFormDataRepository.get_all()

            assert len(all_youth) == 50
            assert len(all_tasks) == 20
            assert len(all_compiled) == 200

            # Test points calculation performance
            task_by_id = {t.id: t for t in all_tasks}

            for youth in all_youth:
                total_points = 0
                for entry in all_compiled:
                    if entry.youth_id == youth.id:
                        task = task_by_id.get(entry.task_id)
                        if task:
                            total_points += (
                                task.points * entry.quantity + entry.bonus
                            )
                YouthFormDataRepository.update_total_points(
                    youth.id, total_points
                )

            # Verify final state
            updated_youth = YouthFormDataRepository.get_all()
            points_list = [y.total_points for y in updated_youth]

            # All youth should have some points calculated
            assert all(points >= 0 for points in points_list)
            assert any(
                points > 0 for points in points_list
            )  # At least some should have points
