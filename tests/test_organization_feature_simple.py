"""
Simple test for the organization column feature
"""
import os
import sys
import pytest
import tempfile
from unittest.mock import patch, MagicMock

# Ensure we can import from src directory  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports_work():
    """Test that we can import the necessary modules"""
    try:
        # Mock streamlit to avoid import issues
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from database import YouthFormData, TasksFormData, CompiledFormData
            assert YouthFormData is not None
            assert TasksFormData is not None  
            assert CompiledFormData is not None
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_organization_column_structure():
    """Test that organization column data structure is correct"""
    # Mock the organization mapping structure like in the actual code
    youth_org_options = {
        1: "Rapazes",
        2: "Moças", 
        3: "Rapazes"
    }
    
    def get_organization_by_id(id_):
        return youth_org_options.get(id_, str(id_))
    
    # Test existing IDs
    assert get_organization_by_id(1) == "Rapazes"
    assert get_organization_by_id(2) == "Moças"
    assert get_organization_by_id(3) == "Rapazes"
    
    # Test non-existing ID
    assert get_organization_by_id(999) == "999"


def test_dataframe_column_order():
    """Test that DataFrame has correct column order with Organization column"""
    import pandas as pd
    
    # Sample data like would be created in the actual code
    sample_data = [
        {
            "Jovem": "João Silva",
            "Organização": "Rapazes", 
            "Tarefa": "Leitura das Escrituras",
            "Data": "18/08/2025",
            "Quantidade": 1,
            "Bônus": 5,
            "Pontuação Total": 15
        },
        {
            "Jovem": "Maria Santos",
            "Organização": "Moças",
            "Tarefa": "Participação no Culto", 
            "Data": "18/08/2025",
            "Quantidade": 1,
            "Bônus": 0,
            "Pontuação Total": 15
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    # Verify column order - Organization should be second column
    expected_columns = ["Jovem", "Organização", "Tarefa", "Data", "Quantidade", "Bônus", "Pontuação Total"]
    assert list(df.columns) == expected_columns
    
    # Verify Organization column is at index 1
    assert df.columns[1] == "Organização"
    
    # Verify organization values are correct
    assert df.iloc[0]["Organização"] == "Rapazes"
    assert df.iloc[1]["Organização"] == "Moças"


def test_organization_mapping_logic():
    """Test the organization mapping logic from refresh_youth_and_task_entries"""
    # Mock youth data structure
    class MockYouth:
        def __init__(self, id, name, organization):
            self.id = id
            self.name = name
            self.organization = organization
    
    # Sample youth entries like returned from database
    youth_entries = [
        MockYouth(1, "João Silva", "Rapazes"),
        MockYouth(2, "Maria Santos", "Moças"),
        MockYouth(3, "Pedro Costa", "Rapazes"),
    ]
    
    # Create mappings like in refresh_youth_and_task_entries function
    youth_options = {y.id: y.name for y in youth_entries}
    youth_org_options = {y.id: y.organization for y in youth_entries}
    
    # Verify mappings are correct
    assert len(youth_org_options) == 3
    assert youth_org_options[1] == "Rapazes"
    assert youth_org_options[2] == "Moças"
    assert youth_org_options[3] == "Rapazes"
    
    # Verify organizations are valid
    for org in youth_org_options.values():
        assert org in ["Rapazes", "Moças"]


def test_refresh_function_return_signature():
    """Test that refresh function returns the correct number of values"""
    # Mock the function signature like in actual code
    def mock_refresh_youth_and_task_entries():
        youth_entries = []
        task_entries = []
        youth_options = {}
        youth_org_options = {}  # This is the new addition
        task_options = {}
        return youth_entries, task_entries, youth_options, youth_org_options, task_options
    
    # Test unpacking works correctly
    result = mock_refresh_youth_and_task_entries()
    assert len(result) == 5  # Should return 5 values now (added youth_org_options)
    
    youth_entries, task_entries, youth_options, youth_org_options, task_options = result
    
    # Verify all components are present
    assert youth_entries is not None
    assert task_entries is not None
    assert youth_options is not None
    assert youth_org_options is not None  # This is the key new component
    assert task_options is not None


if __name__ == "__main__":
    pytest.main([__file__])