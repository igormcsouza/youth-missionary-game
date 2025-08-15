import os
from typing import Optional, Sequence

from sqlmodel import SQLModel, Field, create_engine, Session, select
from utils import handle_database_operation


# Define the model for YouthFormData
default_db_path = "sqlite:///youth_data.db"

class YouthFormData(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
    organization: str
    total_points: int

class YouthFormDataRepository:
    @staticmethod
    def update_total_points(youth_id: int, new_total: int):
        def _update_operation():
            with Session(engine) as session:
                entry = session.get(YouthFormData, youth_id)
                if entry:
                    entry.total_points = new_total
                    session.add(entry)
                    session.commit()
                    session.refresh(entry)
                return entry
        
        return handle_database_operation(
            _update_operation, 
            "atualização da pontuação do jovem"
        )
    
    @staticmethod
    def store(name: str, age: int, organization: str, total_points: int) -> Optional[YouthFormData]:
        def _store_operation():
            entry = YouthFormData(name=name, age=age, organization=organization, total_points=total_points)
            with Session(engine) as session:
                session.add(entry)
                session.commit()
                session.refresh(entry)
            return entry
        
        return handle_database_operation(
            _store_operation,
            "cadastro do jovem"
        )

    @staticmethod
    def get_all() -> Sequence[YouthFormData]:
        def _get_all_operation():
            with Session(engine) as session:
                statement = select(YouthFormData)
                results = session.exec(statement).all()
            return results
        
        result = handle_database_operation(
            _get_all_operation,
            "busca dos jovens cadastrados"
        )
        return result if result is not None else []

    @staticmethod
    def delete(entry_id: int) -> bool:
        def _delete_operation():
            with Session(engine) as session:
                entry = session.get(YouthFormData, entry_id)
                if entry:
                    session.delete(entry)
                    session.commit()
                    return True
                return False
        
        result = handle_database_operation(
            _delete_operation,
            "exclusão do jovem"
        )
        return result if result is not None else False


class TasksFormData(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    tasks: str
    points: int
    repeatable: bool

class TasksFormDataRepository:
    @staticmethod
    def store(tasks: str, points: int, repeatable: bool) -> Optional[TasksFormData]:
        def _store_operation():
            entry = TasksFormData(tasks=tasks, points=points, repeatable=repeatable)
            with Session(engine) as session:
                session.add(entry)
                session.commit()
                session.refresh(entry)
            return entry
        
        return handle_database_operation(
            _store_operation,
            "cadastro da tarefa"
        )

    @staticmethod
    def get_all() -> Sequence[TasksFormData]:
        def _get_all_operation():
            with Session(engine) as session:
                statement = select(TasksFormData)
                results = session.exec(statement).all()
            return results
        
        result = handle_database_operation(
            _get_all_operation,
            "busca das tarefas cadastradas"
        )
        return result if result is not None else []

    @staticmethod
    def delete(entry_id: int) -> bool:
        def _delete_operation():
            with Session(engine) as session:
                entry = session.get(TasksFormData, entry_id)
                if entry:
                    session.delete(entry)
                    session.commit()
                    return True
                return False
        
        result = handle_database_operation(
            _delete_operation,
            "exclusão da tarefa"
        )
        return result if result is not None else False

class CompiledFormData(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    youth_id: int = Field(foreign_key="youthformdata.id")
    task_id: int = Field(foreign_key="tasksformdata.id")
    timestamp: float
    quantity: int
    bonus: int

class CompiledFormDataRepository:
    @staticmethod
    def store(youth_id: int, task_id: int, timestamp: float, quantity: int, bonus: int) -> Optional[CompiledFormData]:
        def _store_operation():
            entry = CompiledFormData(
                youth_id=youth_id,
                task_id=task_id,
                timestamp=timestamp,
                quantity=quantity,
                bonus=bonus
            )
            with Session(engine) as session:
                session.add(entry)
                session.commit()
                session.refresh(entry)
            return entry
        
        return handle_database_operation(
            _store_operation,
            "registro da tarefa compilada"
        )

    @staticmethod
    def get_all() -> Sequence[CompiledFormData]:
        def _get_all_operation():
            with Session(engine) as session:
                statement = select(CompiledFormData)
                results = session.exec(statement).all()
            return results
        
        result = handle_database_operation(
            _get_all_operation,
            "busca dos registros de tarefas"
        )
        return result if result is not None else []

    @staticmethod
    def delete(entry_id: int) -> bool:
        def _delete_operation():
            with Session(engine) as session:
                entry = session.get(CompiledFormData, entry_id)
                if entry:
                    session.delete(entry)
                    session.commit()
                    return True
                return False
        
        result = handle_database_operation(
            _delete_operation,
            "exclusão do registro de tarefa"
        )
        return result if result is not None else False

# Connection strings
SQLITE_URL = default_db_path
POSTGRES_URL = os.getenv("POSTGRESCONNECTIONSTRING", "")

# Choose database based on environment variable
DB_URL = POSTGRES_URL if POSTGRES_URL else SQLITE_URL

try:
    engine = create_engine(DB_URL)
    # Create tables
    SQLModel.metadata.create_all(engine)
except Exception as e:
    # If PostgreSQL connection fails, fallback to SQLite
    if POSTGRES_URL:
        print(f"Warning: PostgreSQL connection failed ({str(e)}), falling back to SQLite")
        try:
            engine = create_engine(SQLITE_URL)
            SQLModel.metadata.create_all(engine)
        except Exception as sqlite_error:
            print(f"Critical: SQLite fallback also failed ({str(sqlite_error)})")
            # Create a minimal working engine for error handling
            engine = create_engine("sqlite:///:memory:")
            SQLModel.metadata.create_all(engine)
    else:
        print(f"Warning: SQLite database issue ({str(e)}), using in-memory database")
        # Create a minimal working engine for error handling
        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)
