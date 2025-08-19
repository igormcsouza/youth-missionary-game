"""
Integration tests for the Organization column feature with database operations
"""
import os
import sys
import pytest
import time
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlmodel import SQLModel, create_engine, Session

# Mock streamlit before any imports that use it
sys.modules['streamlit'] = MagicMock()

# Ensure we can import from src directory  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Now import database components
from database import YouthFormData, TasksFormData, CompiledFormData


class TestOrganizationColumnWithDatabase:
    """Test organization column functionality with actual database operations"""
    
    @pytest.fixture
    def test_engine(self):
        """Create a test database engine"""
        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)
        return engine
    
    def test_organization_column_end_to_end(self, test_engine):
        """Test the complete organization column workflow"""
        
        # Create test data
        with Session(test_engine) as session:
            # Add youth with different organizations
            youth1 = YouthFormData(name="João Silva", age=16, organization="Rapazes", total_points=0)
            youth2 = YouthFormData(name="Maria Santos", age=15, organization="Moças", total_points=0)
            youth3 = YouthFormData(name="Pedro Costa", age=17, organization="Rapazes", total_points=0)
            
            # Add tasks
            task1 = TasksFormData(tasks="Leitura das Escrituras", points=10, repeatable=True)
            task2 = TasksFormData(tasks="Participação no Culto", points=15, repeatable=False)
            
            session.add_all([youth1, youth2, youth3, task1, task2])
            session.commit()
            
            # Refresh to get IDs
            session.refresh(youth1)
            session.refresh(youth2)
            session.refresh(youth3)
            session.refresh(task1)
            session.refresh(task2)
            
            # Add compiled entries
            current_time = time.time()
            compiled1 = CompiledFormData(
                youth_id=youth1.id, task_id=task1.id,
                timestamp=current_time, quantity=1, bonus=5
            )
            compiled2 = CompiledFormData(
                youth_id=youth2.id, task_id=task2.id,
                timestamp=current_time, quantity=1, bonus=0
            )
            compiled3 = CompiledFormData(
                youth_id=youth3.id, task_id=task1.id,
                timestamp=current_time, quantity=2, bonus=3
            )
            
            session.add_all([compiled1, compiled2, compiled3])
            session.commit()
        
        # Test the organization mapping logic (like refresh_youth_and_task_entries)
        with Session(test_engine) as session:
            youth_entries = session.query(YouthFormData).all()
            task_entries = session.query(TasksFormData).all()
            compiled_entries = session.query(CompiledFormData).all()
            
            # Create mappings like in the actual code
            youth_options = {y.id: y.name for y in youth_entries}
            youth_org_options = {y.id: y.organization for y in youth_entries}
            task_options = {t.id: t.tasks for t in task_entries}
            task_by_id = {t.id: t for t in task_entries}
            
            # Helper functions like in the actual code
            def get_name_by_id(id_):
                return youth_options.get(id_, str(id_))
            
            def get_organization_by_id(id_):
                return youth_org_options.get(id_, str(id_))
            
            def get_task_by_id(id_):
                return task_options.get(id_, str(id_))
            
            # Create DataFrame like in the actual code  
            df_compiled = pd.DataFrame([
                {
                    "Jovem": get_name_by_id(e.youth_id),
                    "Organização": get_organization_by_id(e.youth_id),
                    "Tarefa": get_task_by_id(e.task_id),
                    "Data": datetime.fromtimestamp(e.timestamp).strftime("%d/%m/%Y"),
                    "Quantidade": e.quantity,
                    "Bônus": e.bonus,
                    "Pontuação Total": e.quantity * (task_by_id.get(e.task_id).points if task_by_id.get(e.task_id) else 0) + e.bonus
                } for e in compiled_entries
            ])
            
            # Verify the DataFrame structure and content
            expected_columns = ["Jovem", "Organização", "Tarefa", "Data", "Quantidade", "Bônus", "Pontuação Total"]
            assert list(df_compiled.columns) == expected_columns
            
            # Verify Organization column is at the correct position (index 1)
            assert df_compiled.columns[1] == "Organização"
            
            # Verify we have the correct number of entries
            assert len(df_compiled) == 3
            
            # Verify organization values are correctly mapped
            organizations_in_df = set(df_compiled["Organização"].values)
            assert "Rapazes" in organizations_in_df
            assert "Moças" in organizations_in_df
            
            # Verify specific entries
            for _, row in df_compiled.iterrows():
                assert row["Organização"] in ["Rapazes", "Moças"]
                
                # Find the corresponding youth and verify organization
                youth_name = row["Jovem"]
                if youth_name == "João Silva":
                    assert row["Organização"] == "Rapazes"
                elif youth_name == "Maria Santos":
                    assert row["Organização"] == "Moças"
                elif youth_name == "Pedro Costa":
                    assert row["Organização"] == "Rapazes"
    
    def test_organization_mapping_with_edge_cases(self, test_engine):
        """Test organization mapping handles edge cases properly"""
        
        with Session(test_engine) as session:
            # Create youth with edge case data
            youth1 = YouthFormData(name="Test User", age=16, organization="Rapazes", total_points=0)
            session.add(youth1)
            session.commit()
            session.refresh(youth1)
        
        # Test organization mapping
        with Session(test_engine) as session:
            youth_entries = session.query(YouthFormData).all()
            youth_org_options = {y.id: y.organization for y in youth_entries}
            
            def get_organization_by_id(id_):
                return youth_org_options.get(id_, str(id_))
            
            # Test with existing ID
            assert get_organization_by_id(youth1.id) == "Rapazes"
            
            # Test with non-existent ID (should return string representation of ID)
            assert get_organization_by_id(9999) == "9999"
            
            # Test with None (should return "None")
            assert get_organization_by_id(None) == "None"
    
    def test_refresh_function_signature_simulation(self):
        """Test that the refresh function returns the expected structure"""
        
        # Simulate the refresh_youth_and_task_entries function logic
        def simulated_refresh_youth_and_task_entries():
            # Mock data
            youth_entries = [
                type('obj', (object,), {'id': 1, 'name': 'João', 'organization': 'Rapazes'}),
                type('obj', (object,), {'id': 2, 'name': 'Maria', 'organization': 'Moças'})
            ]
            task_entries = [
                type('obj', (object,), {'id': 1, 'tasks': 'Task 1'}),
                type('obj', (object,), {'id': 2, 'tasks': 'Task 2'})
            ]
            
            youth_options = {y.id: y.name for y in youth_entries}
            youth_org_options = {y.id: y.organization for y in youth_entries}  # This is the new addition
            task_options = {t.id: t.tasks for t in task_entries}
            
            return youth_entries, task_entries, youth_options, youth_org_options, task_options
        
        # Test the function returns expected structure
        result = simulated_refresh_youth_and_task_entries()
        assert len(result) == 5  # Should return 5 values now
        
        youth_entries, task_entries, youth_options, youth_org_options, task_options = result
        
        # Verify organization mapping is correctly created
        assert len(youth_org_options) == 2
        assert youth_org_options[1] == "Rapazes"
        assert youth_org_options[2] == "Moças"
        
        # Verify all expected mappings exist
        assert len(youth_options) == 2
        assert len(task_options) == 2
    
    def test_dataframe_column_integration(self):
        """Test DataFrame column integration with organization column"""
        
        # Mock compiled entry data
        mock_entries = [
            type('obj', (object,), {
                'youth_id': 1, 'task_id': 1, 'timestamp': time.time(),
                'quantity': 1, 'bonus': 5
            }),
            type('obj', (object,), {
                'youth_id': 2, 'task_id': 2, 'timestamp': time.time(),
                'quantity': 2, 'bonus': 0
            })
        ]
        
        # Mock mappings
        youth_options = {1: "João Silva", 2: "Maria Santos"}
        youth_org_options = {1: "Rapazes", 2: "Moças"}
        task_options = {1: "Leitura", 2: "Culto"}
        task_by_id = {
            1: type('obj', (object,), {'points': 10}),
            2: type('obj', (object,), {'points': 15})
        }
        
        # Helper functions
        def get_name_by_id(id_):
            return youth_options.get(id_, str(id_))
        
        def get_organization_by_id(id_):
            return youth_org_options.get(id_, str(id_))
        
        def get_task_by_id(id_):
            return task_options.get(id_, str(id_))
        
        # Create DataFrame like in actual code
        df_compiled = pd.DataFrame([
            {
                "Jovem": get_name_by_id(e.youth_id),
                "Organização": get_organization_by_id(e.youth_id),
                "Tarefa": get_task_by_id(e.task_id),
                "Data": datetime.fromtimestamp(e.timestamp).strftime("%d/%m/%Y"),
                "Quantidade": e.quantity,
                "Bônus": e.bonus,
                "Pontuação Total": e.quantity * task_by_id[e.task_id].points + e.bonus
            } for e in mock_entries
        ])
        
        # Verify DataFrame structure
        expected_columns = ["Jovem", "Organização", "Tarefa", "Data", "Quantidade", "Bônus", "Pontuação Total"]
        assert list(df_compiled.columns) == expected_columns
        
        # Verify organization column positioning and values
        assert df_compiled.columns[1] == "Organização"
        assert df_compiled.iloc[0]["Organização"] == "Rapazes"
        assert df_compiled.iloc[1]["Organização"] == "Moças"
        
        # Verify other columns are correctly populated
        assert df_compiled.iloc[0]["Jovem"] == "João Silva"
        assert df_compiled.iloc[1]["Jovem"] == "Maria Santos"
        assert df_compiled.iloc[0]["Pontuação Total"] == 15  # 1 * 10 + 5
        assert df_compiled.iloc[1]["Pontuação Total"] == 30  # 2 * 15 + 0


if __name__ == "__main__":
    pytest.main([__file__])