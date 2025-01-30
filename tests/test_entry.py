from unittest.mock import call, patch
import pytest
from entry import main 


@pytest.fixture(scope="function")
def setup_mock_input(mock_input):
    """
    Setup mock input for entry.py tests.
    """
    def setup(return_values):
        mock_input.return_values = iter(return_values)
    return setup


def test_main_screen_all_modes(setup_mock_input):
    setup_mock_input(["0"])

    with patch("builtins.print") as mock_print:
        main()

    mock_print.assert_any_call("How would you like to run the agent?")
    mock_print.assert_any_call("1. CLI Mode")
    mock_print.assert_any_call("2. Browser Mode (Streamlit)")
    mock_print.assert_any_call("0. Exit")

def test_entry_cli_mode(setup_mock_input, mock_os_system):
    """
    Test entry main function with CLI mode choice.
    """
    setup_mock_input(["1"])

    with patch("builtins.print") as mock_print:
        main()

    mock_print.assert_any_call("Running in CLI mode...")
    mock_os_system.assert_called_once_with("python src/agent.py cli")


def test_entry_browser_mode(setup_mock_input, mock_os_system):
    """
    Test entry main function with Browser mode choice.
    """
    setup_mock_input(["2"])

    with patch("builtins.print") as mock_print:
        main()

    mock_print.assert_any_call("Launching in Browser mode...")
    mock_os_system.assert_called_once_with("streamlit run src/agent.py")


def test_entry_exit(setup_mock_input, mock_os_system, mock_subprocess_run):
    """
    Test entry main function with exit choice.
    """
    setup_mock_input(["0"])

    with patch("builtins.print") as mock_print:
        main()

    mock_print.assert_any_call("Exiting the program.")
    mock_os_system.assert_not_called()
    mock_subprocess_run.assert_not_called()


def test_entry_invalid_choice(setup_mock_input, mock_os_system, mock_subprocess_run):
    """
    Test entry main function with invalid choice.
    """
    setup_mock_input(["3", "0"])

    with patch("builtins.print") as mock_print:
        main()

    
    mock_print.assert_any_call("Invalid choice. Please enter 1 for CLI mode, 2 for Browser mode, or 0 to exit.")
    mock_print.assert_any_call("Exiting the program.")
    
    mock_os_system.assert_not_called()
    mock_subprocess_run.assert_not_called()


def test_entry_max_attempts(setup_mock_input, mock_os_system, mock_subprocess_run):
    """
    Test entry main function with exceeding maximum attempts.
    """
    invalid_choices = ["3"] * 5 + ["0"]
    setup_mock_input(invalid_choices)

    with patch("builtins.print") as mock_print:
        main()

    for _ in range(5):
        mock_print.assert_any_call("Invalid choice. Please enter 1 for CLI mode, 2 for Browser mode, or 0 to exit.")

    mock_print.assert_any_call("You have exceeded the maximum number of attempts. Exiting.")
    mock_os_system.assert_not_called()
    mock_subprocess_run.assert_not_called()