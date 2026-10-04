import importlib
import runpy
import sys

# This module tests interactive CLI behavior and the script entry points from the user's perspective.


def test_run_interactive_handles_valid_and_invalid_operations(monkeypatch, capsys):
    responses = iter(["add", "5", "3", "divide", "10", "0", "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    calculate_and_print = False
    try:
        from app.calculator_repl import run_interactive

        run_interactive()
        calculate_and_print = True
    except Exception:
        pass

    captured = capsys.readouterr()
    assert calculate_and_print is True
    assert "Professional Calculator" in captured.out
    assert "Result: 8.0" in captured.out or "Result: 8" in captured.out
    assert "Cannot divide by zero" in captured.out


def test_run_interactive_help_history_and_exit(monkeypatch, capsys):
    responses = iter(["help", "history", "add", "4", "2", "history", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    from app.calculator_repl import run_interactive

    run_interactive()

    captured = capsys.readouterr()
    assert "Commands: help, history, undo, redo, exit" in captured.out
    assert "No calculations in history." in captured.out
    assert "1. 4.0 + 2.0 = 6.0" in captured.out
    assert "Goodbye!" in captured.out


def test_run_interactive_handles_end_of_input(monkeypatch, capsys):
    def raise_eof(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    from app.calculator_repl import run_interactive

    run_interactive()

    assert "Goodbye!" in capsys.readouterr().out


def test_run_interactive_invalid_operation_shows_available_choices(monkeypatch, capsys):
    responses = iter(["sqrt", "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    from app.calculator_repl import run_interactive

    run_interactive()

    captured = capsys.readouterr()
    assert "Invalid operation" in captured.out
    assert "add (+)" in captured.out
    assert "subtract (-)" in captured.out
    assert "multiply (*)" in captured.out
    assert "divide (/)" in captured.out
    assert "power (^)" in captured.out
    assert "root (√)" in captured.out


def test_run_interactive_power_and_root_show_results_and_history(monkeypatch, capsys):
    responses = iter(["power", "2", "3", "root", "27", "3", "history", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    from app.calculator_repl import run_interactive

    run_interactive()

    output = capsys.readouterr().out
    assert "Result: 8" in output
    assert "Result: 3.0" in output
    assert "1. 2.0 ^ 3.0 = 8" in output
    assert "2. 3.0√(27.0) = 3.0" in output


def test_run_interactive_invalid_root_does_not_add_history(monkeypatch, capsys):
    responses = iter(["root", "-16", "2", "history", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    from app.calculator_repl import run_interactive

    run_interactive()

    output = capsys.readouterr().out
    assert "odd integer root degree" in output
    assert "No calculations in history." in output


def test_run_interactive_undo_and_redo_commands(monkeypatch, capsys):
    responses = iter(
        ["add", "4", "2", "undo", "history", "redo", "history", "exit"]
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    from app.calculator_repl import run_interactive

    run_interactive()

    output = capsys.readouterr().out
    assert "Undid the last calculation." in output
    assert "Redid the last calculation." in output
    assert "No calculations in history." in output
    assert "1. 4.0 + 2.0 = 6.0" in output


def test_run_interactive_rejects_non_finite_numbers(monkeypatch, capsys):
    responses = iter(["add", "nan", "5", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    from app.calculator_repl import run_interactive

    run_interactive()

    captured = capsys.readouterr()
    assert "Please enter a finite number" in captured.out


def test_run_interactive_invalid_number_prompts_user_again(monkeypatch, capsys):
    responses = iter(["add", "abc", "5", "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    from app.calculator_repl import run_interactive

    run_interactive()

    captured = capsys.readouterr()
    assert "Invalid first number" in captured.out
    assert "Please enter a valid number" in captured.out


def test_cli_module_runs_main(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt="": "quit")
    sys.modules.pop("app.calculator_repl", None)
    runpy.run_module("app.calculator_repl", run_name="__main__")

    captured = capsys.readouterr()
    assert "Professional Calculator" in captured.out
    assert "Goodbye!" in captured.out


def test_cli_module_import_does_not_run_interactive(capsys):
    sys.modules.pop("app.calculator_repl", None)
    cli_module = importlib.import_module("app.calculator_repl")

    assert callable(cli_module.run_interactive)
    assert capsys.readouterr().out == ""


def test_calculator_repl_module_runs_main(monkeypatch, capsys):
    responses = iter(["quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    sys.modules.pop("app.calculator_repl", None)
    runpy.run_module("app.calculator_repl", run_name="__main__")

    captured = capsys.readouterr()
    assert "Professional Calculator" in captured.out
    assert "Goodbye!" in captured.out
