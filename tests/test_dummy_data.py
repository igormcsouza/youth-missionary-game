import os
import sys
import tempfile
from unittest.mock import patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from sqlmodel import SQLModel, create_engine

from database import (
    CompiledFormDataRepository,
    TasksFormDataRepository,
    YouthFormDataRepository,
    populate_dummy_data,
)


class TestDummyDataPopulation:
    """Test dummy data population functionality"""

    def setup_method(self):
        """Set up test database for each test"""
        self.test_engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.test_engine)

    def test_populate_dummy_data_not_enabled_by_default(self):
        """Test that dummy data is not populated when POPULATEDUMMY is not set"""
        with patch("database.engine", self.test_engine):
            # Ensure POPULATEDUMMY is not set
            with patch.dict(os.environ, {}, clear=True):
                populate_dummy_data()
                
                # Verify no data was populated
                assert len(YouthFormDataRepository.get_all()) == 0
                assert len(TasksFormDataRepository.get_all()) == 0
                assert len(CompiledFormDataRepository.get_all()) == 0

    def test_populate_dummy_data_enabled_with_true_value(self):
        """Test that dummy data is populated when POPULATEDUMMY=true"""
        with patch("database.engine", self.test_engine):
            with patch.dict(os.environ, {"POPULATEDUMMY": "true"}):
                populate_dummy_data()
                
                # Verify data was populated
                youth_data = YouthFormDataRepository.get_all()
                task_data = TasksFormDataRepository.get_all()
                compiled_data = CompiledFormDataRepository.get_all()
                
                assert len(youth_data) >= 20, f"Expected >=20 youth, got {len(youth_data)}"
                assert len(task_data) >= 20, f"Expected >=20 tasks, got {len(task_data)}"
                assert len(compiled_data) >= 50, f"Expected >=50 compiled entries, got {len(compiled_data)}"

    def test_populate_dummy_data_case_insensitive(self):
        """Test that POPULATEDUMMY accepts TRUE, True, true, etc."""
        test_values = ["TRUE", "True", "true", "tRuE"]
        
        for value in test_values:
            # Create a fresh test engine for each test
            test_engine = create_engine("sqlite:///:memory:")
            SQLModel.metadata.create_all(test_engine)
            
            with patch("database.engine", test_engine):
                with patch.dict(os.environ, {"POPULATEDUMMY": value}):
                    populate_dummy_data()
                    
                    # Verify data was populated
                    youth_data = YouthFormDataRepository.get_all()
                    assert len(youth_data) >= 20, f"Failed for POPULATEDUMMY={value}"

    def test_populate_dummy_data_false_values_ignored(self):
        """Test that false-like values for POPULATEDUMMY are ignored"""
        false_values = ["false", "False", "FALSE", "0", "no", ""]
        
        for value in false_values:
            # Create a fresh test engine for each test
            test_engine = create_engine("sqlite:///:memory:")
            SQLModel.metadata.create_all(test_engine)
            
            with patch("database.engine", test_engine):
                with patch.dict(os.environ, {"POPULATEDUMMY": value}):
                    populate_dummy_data()
                    
                    # Verify no data was populated
                    youth_data = YouthFormDataRepository.get_all()
                    assert len(youth_data) == 0, f"Unexpectedly populated for POPULATEDUMMY={value}"

    def test_dummy_data_avoids_duplicates(self):
        """Test that dummy data population avoids duplicates"""
        with patch("database.engine", self.test_engine):
            with patch.dict(os.environ, {"POPULATEDUMMY": "true"}):
                # Populate once
                populate_dummy_data()
                first_count = len(YouthFormDataRepository.get_all())
                
                # Try to populate again
                with patch("builtins.print") as mock_print:
                    populate_dummy_data()
                    
                # Verify no additional data was added
                second_count = len(YouthFormDataRepository.get_all())
                assert first_count == second_count
                
                # Verify the "already exists" message was printed
                mock_print.assert_called_with("Dummy data already exists, skipping population.")

    def test_dummy_data_contains_expected_task_names(self):
        """Test that dummy data includes the task names expected by Dashboard.py"""
        expected_tasks = [
            "Entregar Livro de Mórmon + foto + relato no grupo",
            "Levar amigo à sacramental",
            "Dar contato (tel/endereço) às Sisteres",
            "Visitar com as Sisteres",
            "Postar mensagem do evangelho nas redes sociais + print",
            "Fazer noite familiar com pesquisador",
        ]
        
        with patch("database.engine", self.test_engine):
            with patch.dict(os.environ, {"POPULATEDUMMY": "true"}):
                populate_dummy_data()
                
                # Get all task names
                task_data = TasksFormDataRepository.get_all()
                task_names = [task.tasks for task in task_data]
                
                # Verify all expected tasks are present
                for expected_task in expected_tasks:
                    assert expected_task in task_names, f"Missing expected task: {expected_task}"

    def test_dummy_data_youth_organizations(self):
        """Test that dummy data includes both Rapazes and Moças organizations"""
        with patch("database.engine", self.test_engine):
            with patch.dict(os.environ, {"POPULATEDUMMY": "true"}):
                populate_dummy_data()
                
                youth_data = YouthFormDataRepository.get_all()
                organizations = [youth.organization for youth in youth_data]
                
                assert "Rapazes" in organizations
                assert "Moças" in organizations
                
                # Verify we have reasonable numbers of each
                rapazes_count = organizations.count("Rapazes")
                mocas_count = organizations.count("Moças")
                
                assert rapazes_count >= 5, f"Expected >=5 Rapazes, got {rapazes_count}"
                assert mocas_count >= 5, f"Expected >=5 Moças, got {mocas_count}"

    def test_dummy_data_timestamps_are_recent(self):
        """Test that compiled data timestamps are from the last 3 weeks"""
        import time
        
        with patch("database.engine", self.test_engine):
            with patch.dict(os.environ, {"POPULATEDUMMY": "true"}):
                populate_dummy_data()
                
                compiled_data = CompiledFormDataRepository.get_all()
                current_time = time.time()
                three_weeks_ago = current_time - (21 * 24 * 60 * 60)
                
                for entry in compiled_data:
                    assert entry.timestamp >= three_weeks_ago, f"Entry timestamp {entry.timestamp} is older than 3 weeks"
                    assert entry.timestamp <= current_time, f"Entry timestamp {entry.timestamp} is in the future"

    def test_dummy_data_error_handling(self):
        """Test error handling when dummy data population fails"""
        with patch("database.engine", self.test_engine):
            with patch.dict(os.environ, {"POPULATEDUMMY": "true"}):
                # Mock a failure during population
                with patch("database.Session") as mock_session:
                    mock_session.side_effect = Exception("Test error")
                    
                    with patch("builtins.print") as mock_print:
                        populate_dummy_data()
                        
                    # Verify error was handled and printed
                    error_calls = [call for call in mock_print.call_args_list if "Error populating dummy data" in str(call)]
                    assert len(error_calls) > 0, "Expected error message was not printed"

    def test_dummy_data_has_valid_foreign_keys(self):
        """Test that compiled data has valid foreign keys to youth and tasks"""
        with patch("database.engine", self.test_engine):
            with patch.dict(os.environ, {"POPULATEDUMMY": "true"}):
                populate_dummy_data()
                
                youth_data = YouthFormDataRepository.get_all()
                task_data = TasksFormDataRepository.get_all()
                compiled_data = CompiledFormDataRepository.get_all()
                
                youth_ids = {youth.id for youth in youth_data}
                task_ids = {task.id for task in task_data}
                
                for entry in compiled_data:
                    assert entry.youth_id in youth_ids, f"Invalid youth_id {entry.youth_id}"
                    assert entry.task_id in task_ids, f"Invalid task_id {entry.task_id}"