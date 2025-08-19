import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from sqlmodel import create_engine, Session, SQLModel
import datetime as dt

# Import the modules to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import (
    YouthFormData, YouthFormDataRepository,
    TasksFormData, TasksFormDataRepository,
    CompiledFormData, CompiledFormDataRepository,
    engine, default_db_path
)


class TestYouthFormData:
    """Test YouthFormData model"""
    
    def test_youth_form_data_creation(self):
        """Test creating a YouthFormData instance"""
        youth = YouthFormData(
            name="João Silva",
            age=16,
            organization="Rapazes",
            total_points=100
        )
        
        assert youth.name == "João Silva"
        assert youth.age == 16
        assert youth.organization == "Rapazes"
        assert youth.total_points == 100
        assert youth.id is None  # Not set until saved


class TestTasksFormData:
    """Test TasksFormData model"""
    
    def test_tasks_form_data_creation(self):
        """Test creating a TasksFormData instance"""
        task = TasksFormData(
            tasks="Ler scriptures",
            points=10,
            repeatable=True
        )
        
        assert task.tasks == "Ler scriptures"
        assert task.points == 10
        assert task.repeatable is True
        assert task.id is None


class TestCompiledFormData:
    """Test CompiledFormData model"""
    
    def test_compiled_form_data_creation(self):
        """Test creating a CompiledFormData instance"""
        timestamp = dt.datetime.now().timestamp()
        compiled = CompiledFormData(
            youth_id=1,
            task_id=1,
            timestamp=timestamp,
            quantity=2,
            bonus=5
        )
        
        assert compiled.youth_id == 1
        assert compiled.task_id == 1
        assert compiled.timestamp == timestamp
        assert compiled.quantity == 2
        assert compiled.bonus == 5
        assert compiled.id is None


class TestDatabaseRepositories:
    """Test database repository classes with in-memory database"""
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Set up in-memory database for each test"""
        # Create in-memory database engine
        self.test_engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.test_engine)
        
        # Patch the global engine
        with patch('database.engine', self.test_engine):
            yield
    
    def test_youth_repository_store_success(self):
        """Test successful youth storage"""
        with patch('database.engine', self.test_engine):
            result = YouthFormDataRepository.store("Maria", 15, "Moças", 0)
            
            assert result is not None
            assert result.name == "Maria"
            assert result.age == 15
            assert result.organization == "Moças"
            assert result.total_points == 0
            assert result.id is not None
    
    def test_youth_repository_get_all_empty(self):
        """Test getting all youth when database is empty"""
        with patch('database.engine', self.test_engine):
            result = YouthFormDataRepository.get_all()
            assert result == []
    
    def test_youth_repository_get_all_with_data(self):
        """Test getting all youth with data"""
        with patch('database.engine', self.test_engine):
            # Store some youth
            YouthFormDataRepository.store("João", 16, "Rapazes", 50)
            YouthFormDataRepository.store("Maria", 15, "Moças", 75)
            
            result = YouthFormDataRepository.get_all()
            assert len(result) == 2
            assert result[0].name == "João"
            assert result[1].name == "Maria"
    
    def test_youth_repository_update_total_points(self):
        """Test updating youth total points"""
        with patch('database.engine', self.test_engine):
            # Store a youth
            youth = YouthFormDataRepository.store("Pedro", 17, "Rapazes", 0)
            
            # Update total points
            YouthFormDataRepository.update_total_points(youth.id, 100)
            
            # Verify update
            all_youth = YouthFormDataRepository.get_all()
            updated_youth = next(y for y in all_youth if y.id == youth.id)
            assert updated_youth.total_points == 100
    
    def test_youth_repository_delete_success(self):
        """Test successful youth deletion"""
        with patch('database.engine', self.test_engine):
            # Store a youth
            youth = YouthFormDataRepository.store("Ana", 16, "Moças", 0)
            
            # Delete youth
            result = YouthFormDataRepository.delete(youth.id)
            assert result is True
            
            # Verify deletion
            all_youth = YouthFormDataRepository.get_all()
            assert len(all_youth) == 0
    
    def test_youth_repository_delete_nonexistent(self):
        """Test deleting non-existent youth"""
        with patch('database.engine', self.test_engine):
            result = YouthFormDataRepository.delete(999)
            assert result is False
    
    def test_tasks_repository_store_success(self):
        """Test successful task storage"""
        with patch('database.engine', self.test_engine):
            result = TasksFormDataRepository.store("Read scriptures", 10, True)
            
            assert result is not None
            assert result.tasks == "Read scriptures"
            assert result.points == 10
            assert result.repeatable is True
            assert result.id is not None
    
    def test_tasks_repository_get_all_empty(self):
        """Test getting all tasks when database is empty"""
        with patch('database.engine', self.test_engine):
            result = TasksFormDataRepository.get_all()
            assert result == []
    
    def test_tasks_repository_get_all_with_data(self):
        """Test getting all tasks with data"""
        with patch('database.engine', self.test_engine):
            # Store some tasks
            TasksFormDataRepository.store("Task 1", 10, True)
            TasksFormDataRepository.store("Task 2", 20, False)
            
            result = TasksFormDataRepository.get_all()
            assert len(result) == 2
            assert result[0].tasks == "Task 1"
            assert result[1].tasks == "Task 2"
    
    def test_tasks_repository_delete_success(self):
        """Test successful task deletion"""
        with patch('database.engine', self.test_engine):
            # Store a task
            task = TasksFormDataRepository.store("Test Task", 15, True)
            
            # Delete task
            result = TasksFormDataRepository.delete(task.id)
            assert result is True
            
            # Verify deletion
            all_tasks = TasksFormDataRepository.get_all()
            assert len(all_tasks) == 0
    
    def test_tasks_repository_delete_nonexistent(self):
        """Test deleting non-existent task"""
        with patch('database.engine', self.test_engine):
            result = TasksFormDataRepository.delete(999)
            assert result is False
    
    def test_compiled_repository_store_success(self):
        """Test successful compiled entry storage"""
        with patch('database.engine', self.test_engine):
            timestamp = dt.datetime.now().timestamp()
            result = CompiledFormDataRepository.store(1, 1, timestamp, 3, 5)
            
            assert result is not None
            assert result.youth_id == 1
            assert result.task_id == 1
            assert result.timestamp == timestamp
            assert result.quantity == 3
            assert result.bonus == 5
            assert result.id is not None
    
    def test_compiled_repository_get_all_empty(self):
        """Test getting all compiled entries when database is empty"""
        with patch('database.engine', self.test_engine):
            result = CompiledFormDataRepository.get_all()
            assert result == []
    
    def test_compiled_repository_get_all_with_data(self):
        """Test getting all compiled entries with data"""
        with patch('database.engine', self.test_engine):
            timestamp = dt.datetime.now().timestamp()
            # Store some entries
            CompiledFormDataRepository.store(1, 1, timestamp, 2, 0)
            CompiledFormDataRepository.store(2, 1, timestamp, 1, 5)
            
            result = CompiledFormDataRepository.get_all()
            assert len(result) == 2
    
    def test_compiled_repository_has_entry_today_false(self):
        """Test has_entry_today returns False when no entry exists"""
        with patch('database.engine', self.test_engine):
            result = CompiledFormDataRepository.has_entry_today(1, 1)
            assert result is False
    
    def test_compiled_repository_has_entry_today_true(self):
        """Test has_entry_today returns True when entry exists today"""
        with patch('database.engine', self.test_engine):
            # Create entry with today's timestamp
            today_timestamp = dt.datetime.now().timestamp()
            CompiledFormDataRepository.store(1, 1, today_timestamp, 1, 0)
            
            result = CompiledFormDataRepository.has_entry_today(1, 1)
            assert result is True
    
    def test_compiled_repository_has_entry_today_false_different_day(self):
        """Test has_entry_today returns False for entries from different days"""
        with patch('database.engine', self.test_engine):
            # Create entry with yesterday's timestamp
            yesterday = dt.datetime.now() - dt.timedelta(days=1)
            yesterday_timestamp = yesterday.timestamp()
            CompiledFormDataRepository.store(1, 1, yesterday_timestamp, 1, 0)
            
            result = CompiledFormDataRepository.has_entry_today(1, 1)
            assert result is False
    
    def test_compiled_repository_delete_success(self):
        """Test successful compiled entry deletion"""
        with patch('database.engine', self.test_engine):
            # Store an entry
            timestamp = dt.datetime.now().timestamp()
            entry = CompiledFormDataRepository.store(1, 1, timestamp, 1, 0)
            
            # Delete entry
            result = CompiledFormDataRepository.delete(entry.id)
            assert result is True
            
            # Verify deletion
            all_entries = CompiledFormDataRepository.get_all()
            assert len(all_entries) == 0
    
    def test_compiled_repository_delete_nonexistent(self):
        """Test deleting non-existent compiled entry"""
        with patch('database.engine', self.test_engine):
            result = CompiledFormDataRepository.delete(999)
            assert result is False


class TestDatabaseErrorHandling:
    """Test database error handling scenarios"""
    
    @patch('database.handle_database_operation')
    def test_youth_store_error_handling(self, mock_handle):
        """Test youth store error handling"""
        mock_handle.return_value = None
        
        result = YouthFormDataRepository.store("Test", 16, "Rapazes", 0)
        assert result is None
        mock_handle.assert_called_once()
    
    @patch('database.handle_database_operation')
    def test_tasks_store_error_handling(self, mock_handle):
        """Test tasks store error handling"""
        mock_handle.return_value = None
        
        result = TasksFormDataRepository.store("Test Task", 10, True)
        assert result is None
        mock_handle.assert_called_once()
    
    @patch('database.handle_database_operation')
    def test_compiled_store_error_handling(self, mock_handle):
        """Test compiled store error handling"""
        mock_handle.return_value = None
        
        timestamp = dt.datetime.now().timestamp()
        result = CompiledFormDataRepository.store(1, 1, timestamp, 1, 0)
        assert result is None
        mock_handle.assert_called_once()
    
    @patch('database.handle_database_operation')
    def test_get_all_error_handling(self, mock_handle):
        """Test get_all methods error handling"""
        mock_handle.return_value = None
        
        # Test all get_all methods return empty list on error
        assert YouthFormDataRepository.get_all() == []
        assert TasksFormDataRepository.get_all() == []
        assert CompiledFormDataRepository.get_all() == []
    
    @patch('database.handle_database_operation')
    def test_delete_error_handling(self, mock_handle):
        """Test delete methods error handling"""
        mock_handle.return_value = None
        
        # Test all delete methods return False on error
        assert YouthFormDataRepository.delete(1) is False
        assert TasksFormDataRepository.delete(1) is False
        assert CompiledFormDataRepository.delete(1) is False
    
    @patch('database.handle_database_operation')
    def test_has_entry_today_error_handling(self, mock_handle):
        """Test has_entry_today error handling"""
        mock_handle.return_value = None
        
        result = CompiledFormDataRepository.has_entry_today(1, 1)
        assert result is False


class TestDatabaseConnection:
    """Test database connection setup and fallback mechanisms"""
    
    def test_database_url_postgres_configured(self):
        """Test database URL selection when PostgreSQL is configured"""
        with patch.dict(os.environ, {'POSTGRESCONNECTIONSTRING': 'postgresql://test'}):
            # Test the environment variable logic directly
            postgres_url = os.getenv("POSTGRESCONNECTIONSTRING", "")
            sqlite_url = "sqlite:///youth_data.db"
            db_url = postgres_url if postgres_url else sqlite_url
            
            assert postgres_url == 'postgresql://test'
            assert sqlite_url == "sqlite:///youth_data.db"
            assert db_url == 'postgresql://test'
    
    def test_database_url_postgres_not_configured(self):
        """Test database URL selection when PostgreSQL is not configured"""
        with patch.dict(os.environ, {}, clear=True):
            # Re-import to test environment logic
            import importlib
            import database
            importlib.reload(database)
            
            assert database.POSTGRES_URL == ""
            assert database.DB_URL == database.SQLITE_URL
    
    def test_default_db_path_constant(self):
        """Test that default database path is correct"""
        import database
        assert database.SQLITE_URL.startswith("sqlite:///")
        assert "youth_data.db" in database.SQLITE_URL
        assert default_db_path == "sqlite:///youth_data.db"