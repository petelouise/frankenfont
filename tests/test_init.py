import pytest
from pathlib import Path
import sys

# Adjust the import path if necessary
sys.path.append(str(Path(__file__).resolve().parents[1]))

import src.frankenfont  # Importing to trigger any initialization code

def test_init():
    """Test that the frankenfont package initializes without errors."""
    try:
        _ = src.frankenfont.__version__  # Example attribute
    except AttributeError:
        pass  # If no attributes to test, just ensure no exceptions were raised
    except Exception as e:
        pytest.fail(f"Initialization of frankenfont raised an exception: {e}")
