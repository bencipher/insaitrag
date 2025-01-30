from unittest.mock import call, patch
import pytest

from main import start


@pytest.mark.parametrize(
    "run_mode, expected_output, expected_system_call",
    [
        ("cli", "Running in CLI mode...", ["python src/agent.py cli"]),
        ("browser", "Launching in Browser mode...", ["streamlit run src/agent.py"]),
        ("invalid", "Invalid mode - exiting...", []),
    ],
)
def test_main(
    mock_os_environ,
    mock_os_system,
    run_mode,
    expected_output,
    expected_system_call,
):
    """
    Test main function with different RUN_MODE values.
    """
    mock_os_environ["RUN_MODE"] = run_mode
    with patch("builtins.print") as mock_print:
        start()
    print(f"{mock_os_environ=}")
    mock_print.assert_any_call(expected_output)

    if run_mode == "cli":
        mock_os_system.assert_has_calls([call(expected_system_call[0])])
    elif run_mode == "browser":
        mock_os_system.assert_called_once_with(expected_system_call[0])
    else:
        mock_os_system.assert_not_called()


def test_main_no_run_mode(mock_os_environ, mock_os_system, mock_subprocess_run):
    """
    Test main function when RUN_MODE environment variable is not set.
    """
    mock_os_environ.pop("RUN_MODE", None)

    with patch("builtins.print") as mock_print:
        start()

    mock_print.assert_any_call("Invalid mode - exiting...")
    mock_os_system.assert_not_called()
    mock_subprocess_run.assert_not_called()
