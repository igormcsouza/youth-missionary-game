import datetime as dt
import os
from collections.abc import Sequence

from sqlmodel import Field, Session, SQLModel, create_engine, select

from utils import handle_database_operation

# Define the model for YouthFormData
default_db_path = "sqlite:///youth_data.db"


class YouthFormData(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
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
            _update_operation, "atualização da pontuação do jovem"
        )

    @staticmethod
    def store(
        name: str, age: int, organization: str, total_points: int
    ) -> YouthFormData | None:
        def _store_operation():
            entry = YouthFormData(
                name=name,
                age=age,
                organization=organization,
                total_points=total_points,
            )
            with Session(engine) as session:
                session.add(entry)
                session.commit()
                session.refresh(entry)
            return entry

        return handle_database_operation(_store_operation, "cadastro do jovem")

    @staticmethod
    def get_all() -> Sequence[YouthFormData]:
        def _get_all_operation():
            with Session(engine) as session:
                statement = select(YouthFormData)
                results = session.exec(statement).all()
            return results

        result = handle_database_operation(
            _get_all_operation, "busca dos jovens cadastrados"
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
            _delete_operation, "exclusão do jovem"
        )
        return result if result is not None else False


class TasksFormData(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    tasks: str
    points: int
    repeatable: bool


class TasksFormDataRepository:
    @staticmethod
    def store(
        tasks: str, points: int, repeatable: bool
    ) -> TasksFormData | None:
        def _store_operation():
            entry = TasksFormData(
                tasks=tasks, points=points, repeatable=repeatable
            )
            with Session(engine) as session:
                session.add(entry)
                session.commit()
                session.refresh(entry)
            return entry

        return handle_database_operation(
            _store_operation, "cadastro da tarefa"
        )

    @staticmethod
    def get_all() -> Sequence[TasksFormData]:
        def _get_all_operation():
            with Session(engine) as session:
                statement = select(TasksFormData)
                results = session.exec(statement).all()
            return results

        result = handle_database_operation(
            _get_all_operation, "busca das tarefas cadastradas"
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
            _delete_operation, "exclusão da tarefa"
        )
        return result if result is not None else False


class CompiledFormData(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    youth_id: int = Field(foreign_key="youthformdata.id")
    task_id: int = Field(foreign_key="tasksformdata.id")
    timestamp: float
    quantity: int
    bonus: int


class CompiledFormDataRepository:
    @staticmethod
    def store(
        youth_id: int,
        task_id: int,
        timestamp: float,
        quantity: int,
        bonus: int,
    ) -> CompiledFormData | None:
        def _store_operation():
            entry = CompiledFormData(
                youth_id=youth_id,
                task_id=task_id,
                timestamp=timestamp,
                quantity=quantity,
                bonus=bonus,
            )
            with Session(engine) as session:
                session.add(entry)
                session.commit()
                session.refresh(entry)
            return entry

        return handle_database_operation(
            _store_operation, "registro da tarefa compilada"
        )

    @staticmethod
    def get_all() -> Sequence[CompiledFormData]:
        def _get_all_operation():
            with Session(engine) as session:
                statement = select(CompiledFormData)
                results = session.exec(statement).all()
            return results

        result = handle_database_operation(
            _get_all_operation, "busca dos registros de tarefas"
        )
        return result if result is not None else []

    @staticmethod
    def has_entry_today(youth_id: int, task_id: int) -> bool:
        """Check if there's already an entry for the same youth and task
        on the same day"""

        def _check_operation():
            today = dt.date.today()
            today_start = dt.datetime.combine(today, dt.time.min)
            tomorrow_start = today_start + dt.timedelta(days=1)

            today_start_timestamp = today_start.timestamp()
            tomorrow_start_timestamp = tomorrow_start.timestamp()

            with Session(engine) as session:
                statement = select(CompiledFormData).where(
                    CompiledFormData.youth_id == youth_id,
                    CompiledFormData.task_id == task_id,
                    CompiledFormData.timestamp >= today_start_timestamp,
                    CompiledFormData.timestamp < tomorrow_start_timestamp,
                )
                result = session.exec(statement).first()
                return result is not None

        result = handle_database_operation(
            _check_operation, "verificação de entrada existente no dia"
        )
        return result if result is not None else False

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
            _delete_operation, "exclusão do registro de tarefa"
        )
        return result if result is not None else False


def populate_dummy_data():
    """Populate database with dummy data for testing purposes.
    Only runs if POPULATEDUMMY environment variable is set to 'true'."""
    
    if os.getenv("POPULATEDUMMY", "").lower() != "true":
        return
    
    # Check if data already exists to avoid duplicates
    if YouthFormDataRepository.get_all():
        print("Dummy data already exists, skipping population.")
        return
    
    try:
        import time
        current_time = time.time()
        
        # Calculate timestamps for the last 3 weeks
        week1_timestamps = []
        week2_timestamps = []
        week3_timestamps = []
        
        for days_ago in range(20, 14, -1):  # Week 1: 20-15 days ago
            week1_timestamps.append(current_time - (days_ago * 24 * 60 * 60))
        
        for days_ago in range(14, 7, -1):   # Week 2: 14-8 days ago
            week2_timestamps.append(current_time - (days_ago * 24 * 60 * 60))
            
        for days_ago in range(7, 0, -1):    # Week 3: 7-1 days ago
            week3_timestamps.append(current_time - (days_ago * 24 * 60 * 60))
        
        with Session(engine) as session:
            # First, populate youth data
            youth_data = [
                ("João Silva", 16, "Rapazes", 150),
                ("Pedro Santos", 17, "Rapazes", 180),
                ("Carlos Oliveira", 15, "Rapazes", 120),
                ("Lucas Ferreira", 18, "Rapazes", 220),
                ("Gabriel Costa", 16, "Rapazes", 95),
                ("Rafael Lima", 17, "Rapazes", 175),
                ("André Souza", 15, "Rapazes", 140),
                ("Mateus Almeida", 18, "Rapazes", 200),
                ("Thiago Rocha", 16, "Rapazes", 85),
                ("Fernando Dias", 17, "Rapazes", 165),
                ("Gustavo Martins", 15, "Rapazes", 110),
                ("Diego Castro", 18, "Rapazes", 190),
                ("Maria Silva", 16, "Moças", 170),
                ("Ana Santos", 17, "Moças", 205),
                ("Julia Oliveira", 15, "Moças", 135),
                ("Beatriz Ferreira", 18, "Moças", 240),
                ("Carla Costa", 16, "Moças", 115),
                ("Isabella Lima", 17, "Moças", 185),
                ("Sophia Souza", 15, "Moças", 155),
                ("Vitória Almeida", 18, "Moças", 210),
                ("Camila Rocha", 16, "Moças", 125),
                ("Letícia Dias", 17, "Moças", 175),
                ("Gabriela Martins", 15, "Moças", 145),
                ("Laura Castro", 18, "Moças", 195),
                ("Amanda Ribeiro", 16, "Moças", 160),
                ("Jéssica Pereira", 17, "Moças", 180),
            ]
            
            for name, age, org, points in youth_data:
                youth = YouthFormData(
                    name=name, age=age, organization=org, total_points=points
                )
                session.add(youth)
            
            # Populate task data
            task_data = [
                ("Entregar Livro de Mórmon + foto + relato no grupo", 25, True),
                ("Levar amigo à sacramental", 20, True),
                ("Dar contato (tel/endereço) às Sisteres", 15, True),
                ("Visitar com as Sisteres", 30, True),
                ("Postar mensagem do evangelho nas redes sociais + print", 10, True),
                ("Fazer noite familiar com pesquisador", 25, True),
                ("Orar em família", 5, True),
                ("Ler as escrituras por 30 minutos", 10, True),
                ("Participar da reunião sacramental", 15, False),
                ("Frequentar aula da escola dominical", 10, False),
                ("Participar da reunião do sacerdócio/moças", 10, False),
                ("Visita domiciliar com o bispo", 20, True),
                ("Conversar sobre o evangelho com um amigo", 15, True),
                ("Compartilhar testemunho nas redes sociais", 12, True),
                ("Jejuar e orar por alguém específico", 15, True),
                ("Ajudar no templo", 30, True),
                ("Participar de atividade de serviço", 20, True),
                ("Estudar um discurso da conferência geral", 8, True),
                ("Memorizar uma escritura", 10, True),
                ("Convidar alguém para uma atividade da igreja", 18, True),
                ("Fazer indexação familiar", 12, True),
                ("Organizar noite familiar extra", 15, True),
                ("Visitar membro menos ativo", 25, True),
                ("Participar de projeto de bem-estar", 20, True),
                ("Estudar Livro de Mórmon em grupo", 12, True),
            ]
            
            for task_name, points, repeatable in task_data:
                task = TasksFormData(
                    tasks=task_name, points=points, repeatable=repeatable
                )
                session.add(task)
            
            session.commit()
            session.refresh(youth)  # Get the IDs
            
            # Now populate compiled data with proper timestamps
            compiled_entries = [
                # Week 1 entries (using week1_timestamps)
                (1, 1, week1_timestamps[0], 2, 5),
                (2, 2, week1_timestamps[1], 1, 0),
                (3, 3, week1_timestamps[2], 3, 2),
                (4, 4, week1_timestamps[3], 1, 0),
                (5, 5, week1_timestamps[4], 2, 3),
                (6, 6, week1_timestamps[5], 1, 0),
                (7, 7, week1_timestamps[0], 5, 0),
                (8, 8, week1_timestamps[1], 3, 1),
                (9, 9, week1_timestamps[2], 1, 0),
                (10, 10, week1_timestamps[3], 2, 0),
                (11, 11, week1_timestamps[4], 1, 0),
                (12, 12, week1_timestamps[5], 1, 5),
                (13, 1, week1_timestamps[0], 1, 0),
                (14, 2, week1_timestamps[1], 2, 2),
                (15, 3, week1_timestamps[2], 2, 1),
                (16, 4, week1_timestamps[3], 1, 0),
                (17, 5, week1_timestamps[4], 3, 2),
                (18, 6, week1_timestamps[5], 1, 0),
                
                # Week 2 entries (using week2_timestamps)
                (19, 13, week2_timestamps[0], 2, 1),
                (20, 14, week2_timestamps[1], 1, 0),
                (21, 15, week2_timestamps[2], 1, 3),
                (22, 16, week2_timestamps[3], 1, 0),
                (23, 17, week2_timestamps[4], 2, 1),
                (24, 18, week2_timestamps[5], 3, 0),
                (25, 19, week2_timestamps[6], 1, 2),
                (1, 20, week2_timestamps[0], 2, 0),
                (2, 21, week2_timestamps[1], 1, 1),
                (3, 22, week2_timestamps[2], 1, 0),
                (4, 23, week2_timestamps[3], 1, 2),
                (5, 24, week2_timestamps[4], 2, 0),
                (6, 25, week2_timestamps[5], 1, 1),
                (7, 1, week2_timestamps[6], 1, 0),
                (8, 2, week2_timestamps[0], 1, 0),
                (9, 3, week2_timestamps[1], 2, 1),
                (10, 4, week2_timestamps[2], 1, 0),
                (11, 5, week2_timestamps[3], 1, 2),
                (12, 6, week2_timestamps[4], 2, 0),
                
                # Week 3 entries (using week3_timestamps)
                (13, 7, week3_timestamps[0], 3, 1),
                (14, 8, week3_timestamps[1], 2, 0),
                (15, 9, week3_timestamps[2], 1, 0),
                (16, 10, week3_timestamps[3], 1, 1),
                (17, 11, week3_timestamps[4], 1, 0),
                (18, 12, week3_timestamps[5], 1, 3),
                (19, 1, week3_timestamps[6], 2, 2),
                (20, 2, week3_timestamps[0], 1, 0),
                (21, 3, week3_timestamps[1], 3, 1),
                (22, 4, week3_timestamps[2], 1, 0),
                (23, 5, week3_timestamps[3], 2, 2),
                (24, 6, week3_timestamps[4], 1, 0),
                (25, 13, week3_timestamps[5], 1, 1),
                (26, 14, week3_timestamps[6], 2, 0),
                (1, 15, week3_timestamps[0], 1, 0),
                (2, 16, week3_timestamps[1], 1, 2),
                (3, 17, week3_timestamps[2], 2, 0),
                (4, 18, week3_timestamps[3], 1, 1),
                (5, 19, week3_timestamps[4], 1, 0),
                (6, 20, week3_timestamps[5], 2, 1),
                (7, 21, week3_timestamps[6], 1, 0),
                
                # Additional entries to ensure we have 50+ compiled entries
                (8, 1, week3_timestamps[1], 1, 1),
                (9, 2, week3_timestamps[2], 2, 0),
                (10, 3, week3_timestamps[3], 1, 2),
                (11, 4, week3_timestamps[4], 1, 0),
                (12, 5, week3_timestamps[5], 3, 1),
                (13, 6, week3_timestamps[6], 1, 0),
                (14, 1, week3_timestamps[0], 1, 3),
                (15, 2, week3_timestamps[1], 2, 0),
                (16, 3, week3_timestamps[2], 1, 1),
                (17, 4, week3_timestamps[3], 1, 0),
                (18, 5, week3_timestamps[4], 2, 2),
                (19, 6, week3_timestamps[5], 1, 0),
            ]
            
            for youth_id, task_id, timestamp, quantity, bonus in compiled_entries:
                compiled = CompiledFormData(
                    youth_id=youth_id,
                    task_id=task_id,
                    timestamp=timestamp,
                    quantity=quantity,
                    bonus=bonus
                )
                session.add(compiled)
            
            session.commit()
        
        print("Successfully populated database with dummy data.")
        
    except Exception as e:
        print(f"Error populating dummy data: {str(e)}")
        import traceback
        traceback.print_exc()


# Connection strings
SQLITE_URL = default_db_path
POSTGRES_URL = os.getenv("POSTGRESCONNECTIONSTRING", "")

# Choose database based on environment variable
DB_URL = POSTGRES_URL if POSTGRES_URL else SQLITE_URL

try:
    engine = create_engine(DB_URL)
    # Create tables
    SQLModel.metadata.create_all(engine)
    # Populate dummy data if requested
    populate_dummy_data()
except Exception as e:
    # If PostgreSQL connection fails, fallback to SQLite
    if POSTGRES_URL:
        print(
            f"Warning: PostgreSQL connection failed ({str(e)}), "
            f"falling back to SQLite"
        )
        try:
            engine = create_engine(SQLITE_URL)
            SQLModel.metadata.create_all(engine)
            # Populate dummy data if requested
            populate_dummy_data()
        except Exception as sqlite_error:
            print(
                f"Critical: SQLite fallback also failed ({str(sqlite_error)})"
            )
            # Create a minimal working engine for error handling
            engine = create_engine("sqlite:///:memory:")
            SQLModel.metadata.create_all(engine)
    else:
        print(
            f"Warning: SQLite database issue ({str(e)}), "
            f"using in-memory database"
        )
        # Create a minimal working engine for error handling
        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)
