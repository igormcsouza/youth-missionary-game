import os
from typing import Optional, Sequence

from sqlmodel import SQLModel, Field, create_engine, Session, select


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
        with Session(engine) as session:
            entry = session.get(YouthFormData, youth_id)
            if entry:
                entry.total_points = new_total
                session.add(entry)
                session.commit()
                session.refresh(entry)
            return entry
    @staticmethod
    def store(name: str, age: int, organization: str, total_points: int) -> YouthFormData:
        entry = YouthFormData(name=name, age=age, organization=organization, total_points=total_points)
        with Session(engine) as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)
        return entry

    @staticmethod
    def get_all() -> Sequence[YouthFormData]:
        with Session(engine) as session:
            statement = select(YouthFormData)
            results = session.exec(statement).all()
        return results

    @staticmethod
    def delete(entry_id: int) -> bool:
        with Session(engine) as session:
            entry = session.get(YouthFormData, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False


class TasksFormData(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    tasks: str
    points: int
    repeatable: bool

class TasksFormDataRepository:
    @staticmethod
    def store(tasks: str, points: int, repeatable: bool) -> TasksFormData:
        entry = TasksFormData(tasks=tasks, points=points, repeatable=repeatable)
        with Session(engine) as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)
        return entry

    @staticmethod
    def get_all() -> Sequence[TasksFormData]:
        with Session(engine) as session:
            statement = select(TasksFormData)
            results = session.exec(statement).all()
        return results

    @staticmethod
    def delete(entry_id: int) -> bool:
        with Session(engine) as session:
            entry = session.get(TasksFormData, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

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
    def store(youth_id: int, task_id: int, timestamp: float, quantity: int, bonus: int) -> CompiledFormData:
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

    @staticmethod
    def get_all() -> Sequence[CompiledFormData]:
        with Session(engine) as session:
            statement = select(CompiledFormData)
            results = session.exec(statement).all()
        return results

    @staticmethod
    def delete(entry_id: int) -> bool:
        with Session(engine) as session:
            entry = session.get(CompiledFormData, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

# Connection strings
SQLITE_URL = default_db_path
POSTGRES_URL = os.getenv("POSTGRESCONNECTIONSTRING", "")

# Choose database based on environment variable
DB_URL = POSTGRES_URL if POSTGRES_URL else SQLITE_URL
engine = create_engine(DB_URL)

# Create tables
SQLModel.metadata.create_all(engine)
