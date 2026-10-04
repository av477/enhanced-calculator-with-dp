# Enhanced Calculator

A Python command-line calculator with a read-evaluate-print loop (REPL), six arithmetic operations, and persistent pandas-backed CSV calculation history. Its code is organized into focused modules under `app/`.

## Features

- Addition, subtraction, multiplication, division, power, and nth root
- Operation names, aliases, and symbols:
   - Addition: `add`, `sum`, `+`
   - Subtraction: `subtract`, `minus`, `-`
   - Multiplication: `multiply`, `times`, `*`
   - Division: `divide`, `div`, `/`
   - Power: `power`, `pow`, `^`
   - Root: `root`, `nthroot`, `√` (enter the radicand, then the root degree)
- REPL commands: `help`, `history`, `clear`, `undo`, `redo`, `save`, `load`, and `exit` (`quit` and `q` also exit)
- Undo and redo of successful calculations
- Observer notifications, logging, and automatic CSV history persistence
- Strategy-based operations instantiated through an operation factory
- A `Calculator` facade coordinating operations, observers, history, and undo/redo
- Input validation for invalid operations, malformed numbers, and non-finite values
- Clear division-by-zero errors
- Calculation instances created through `CalculationFactory`
- Unit tests with 100% statement and branch coverage enforced in CI

## Requirements

- Python 3.11 or newer
- pip
- pandas

## Setup

Run these commands from the project root. A virtual environment keeps the project dependencies separate from other Python installations.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If PowerShell blocks activation scripts, allow script execution for the current terminal session, then activate the environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

The editable installation installs the runtime dependency and the optional development dependencies (`pytest` and `pytest-cov`).

## Run

Start the calculator from the project root:

```console
python -m app.calculator_repl
```

## Configuration

Settings can be provided through environment variables or a `.env` file in the
working directory. Process environment variables take precedence over `.env`.
All settings are validated on startup; invalid values are reported before the
REPL starts.

| Variable | Default | Description |
| --- | --- | --- |
| `CALCULATOR_HISTORY_FILE` | `calculator_history.csv` | CSV path; must end in `.csv` |
| `CALCULATOR_AUTOSAVE_HISTORY` | `true` | Enable automatic CSV saving (`true`/`false`, `1`/`0`, `yes`/`no`, or `on`/`off`) |
| `CALCULATOR_LOG_LEVEL` | `INFO` | `CRITICAL`, `ERROR`, `WARNING`, `INFO`, or `DEBUG` |

Copy `.env.example` to `.env` to customize these settings locally. `.env` is
excluded from version control.

Choose an operation, then enter two finite numbers when prompted. For root, enter the radicand followed by the root degree:

```text
Choose an operation: add
Enter the first number: 10
Enter the second number: 5
Result: 15.0
Choose an operation: history
1. 10.0 + 5.0 = 15.0
Choose an operation: exit
Goodbye!
```

Enter `help` to list commands, operations, and aliases. Enter `history` to display successful calculations. `clear` removes calculations from the current history (and can itself be undone); `undo` and `redo` move between history states. `save` writes to the configured CSV path, and `load` replaces current history from that path. A new calculation clears redo state. The REPL loads the configured CSV from the working directory at startup and automatically saves changes when auto-save is enabled. Invalid input displays an error and returns to the operation prompt. Division by zero is rejected without adding a result to history.

Input validation uses both common error-handling styles: the REPL checks operation names before requesting operands (LBYL), while numeric conversion and CSV file operations attempt the action and handle expected exceptions (EAFP). Errors such as invalid operations, malformed numbers, invalid CSV data, and missing or inaccessible files are reported without terminating the REPL.

## Design patterns

- **Strategy and Factory:** `OperationFactory` creates an interchangeable arithmetic strategy for the selected operation. `CalculationFactory` normalizes user aliases and creates calculation requests.
- **Observer:** `Calculator` notifies registered observers after calculations, undo, and redo. `LoggingObserver` logs events; `AutoSaveHistoryObserver` writes the current history as CSV.
- **Memento:** `CalculationHistory` creates immutable `CalculatorMemento` snapshots. The `Calculator` facade retains undo and redo snapshots.
- **Facade:** `Calculator` provides one interface to execution, history, observers, undo, and redo.

To configure automatic history saving and loading, pass the same CSV path to the history observer and load it when constructing the calculator:

```python
from app.calculator import Calculator
from pathlib import Path

from app.calculator_observers import AutoSaveHistoryObserver, LoggingObserver
from app.history import CalculationHistory

history_path = Path("calculator_history.csv")
history = (
    CalculationHistory.from_csv(history_path).get_all()
    if history_path.exists()
    else ()
)

calculator = Calculator(
    observers=[
        LoggingObserver(),
        AutoSaveHistoryObserver(history_path),
    ],
    initial_history=history,
)
calculator.calculate(2, "power", 3)
```

## Use the Calculation API

Calculation instances normalize operation names, aliases, and symbols before execution:

```python
from app.calculation import CalculationFactory

calculation = CalculationFactory.create_calculation(12, "*", 3)
print(calculation.calculate())  # 36
```

The `calculate(first_number, operation, second_number)` helper provides the same calculation behavior without retaining a calculation object.

## Project Layout

```text
app/
   calculator_repl.py       REPL and command-line entry point
   calculation.py           Calculation objects, factory, and helpers
   calculator_config.py     Operation names, aliases, and symbols
   calculator_memento.py    Immutable calculator state snapshots
   calculator_observers.py  Observer protocol, logging, and CSV auto-save
   calculator.py            Facade with operation execution and undo/redo
   exceptions.py            Calculator-specific exceptions
   history.py               pandas-backed history and CSV import/export
   input_validators.py      Numeric input validation
   operations.py            Arithmetic functions
tests/                      Pytest unit and CLI integration tests
```

## Run Tests

Run all unit and integration tests:

```console
python -m pytest
```

Measure statement and branch coverage and require both to reach 100%:

```console
python -m pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=100
```

Coverage exclusions should be reserved for code that cannot meaningfully be exercised by a test. `# pragma: no cover` excludes the marked line from the report and can exclude an entire conditional clause. `# pragma: no branch` marks a deliberately partial branch as intentional. Prefer adding tests for reachable paths; this project currently needs no coverage exclusions.

## Continuous Integration

The GitHub Actions workflow at `.github/workflows/python-tests.yml` installs the project with development dependencies, runs pytest with branch coverage enabled, and fails if total coverage is below 100%.
