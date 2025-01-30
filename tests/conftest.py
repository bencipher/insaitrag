import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="function")
def mock_os_environ(monkeypatch):
    """
    Fixture to mock os.environ.
    """
    monkeypatch.setattr(os, "environ", {})
    return {}


@pytest.fixture(scope="function")
def mock_os_system(monkeypatch):
    """
    Fixture to mock os.system.
    """
    mock_system = patch("os.system").start()
    yield mock_system
    patch.stopall()


@pytest.fixture(scope="function")
def mock_subprocess_run(monkeypatch):
    """
    Fixture to mock subprocess.run.
    """
    print("I am here now")
    mock_run = patch("subprocess.run").start()
    print("was it patched or running streamlit")
    yield mock_run
    print("yielded")
    patch.stopall()


@pytest.fixture(scope="function")
def mock_input(monkeypatch):
    """
    Fixture to mock input function.
    """
    def mock_input_side_effect(*args, **kwargs):
        return next(mock_input_side_effect.return_values)
    mock_input_side_effect.return_values = iter([])
    monkeypatch.setattr("builtins.input", mock_input_side_effect)
    return mock_input_side_effect