import json
import logging

import pytest

from app.calculator import Calculator
from app.calculator_observers import AutoSaveHistoryObserver, LoggingObserver
from app.operations import (
    AdditionStrategy,
    DivisionStrategy,
    OperationFactory,
    PowerStrategy,
    RootStrategy,
)


def test_calculator_facade_executes_and_tracks_successful_calculations():
    calculator = Calculator()

    assert calculator.calculate(2, "+", 3) == 5
    assert len(calculator.history) == 1
    assert calculator.history[0].operation == "add"


def test_failed_calculation_does_not_change_history_or_undo_state():
    calculator = Calculator()

    with pytest.raises(ZeroDivisionError):
        calculator.calculate(2, "divide", 0)

    assert calculator.history == ()
    assert calculator.undo() is False


def test_undo_redo_restore_history_and_new_calculation_discards_redo():
    calculator = Calculator()
    calculator.calculate(2, "+", 3)
    calculator.calculate(4, "*", 5)

    assert calculator.undo() is True
    assert [item.operation for item in calculator.history] == ["add"]
    assert calculator.redo() is True
    assert [item.operation for item in calculator.history] == ["add", "multiply"]

    assert calculator.undo() is True
    calculator.calculate(8, "-", 1)
    assert calculator.redo() is False
    assert [item.operation for item in calculator.history] == ["add", "subtract"]


def test_observers_receive_calculation_undo_and_redo_events():
    class RecordingObserver:
        def __init__(self):
            self.actions = []

        def update(self, event):
            self.actions.append((event.action, len(event.history)))

    observer = RecordingObserver()
    calculator = Calculator(observers=(observer,))
    calculator.calculate(3, "^", 2)
    calculator.undo()
    calculator.redo()

    assert observer.actions == [("calculate", 1), ("undo", 0), ("redo", 1)]


def test_observers_can_be_added_and_removed():
    class RecordingObserver:
        def __init__(self):
            self.events = 0

        def update(self, event):
            self.events += 1

    observer = RecordingObserver()
    calculator = Calculator()
    calculator.add_observer(observer)
    calculator.add_observer(observer)
    calculator.calculate(1, "add", 1)
    calculator.remove_observer(observer)
    calculator.calculate(2, "add", 2)

    assert observer.events == 1


def test_logging_observer_logs_calculation(caplog):
    calculator = Calculator(observers=(LoggingObserver(),))

    with caplog.at_level(logging.INFO, logger="app.calculator_observers"):
        calculator.calculate(3, "*", 4)

    assert "3 * 4 = 12" in caplog.text


def test_autosave_observer_writes_calculations_and_tracks_undo_redo(tmp_path):
    history_file = tmp_path / "history.json"
    calculator = Calculator(observers=(AutoSaveHistoryObserver(history_file),))
    calculator.calculate(2, "^", 3)
    records = json.loads(history_file.read_text(encoding="utf-8"))
    assert records == [
        {
            "first_number": 2,
            "operation": "power",
            "second_number": 3,
            "result": 8,
        }
    ]

    calculator.undo()
    assert json.loads(history_file.read_text(encoding="utf-8")) == []
    calculator.redo()
    assert json.loads(history_file.read_text(encoding="utf-8")) == records


@pytest.mark.parametrize(
    ("operation", "strategy_type"),
    [
        ("+", AdditionStrategy),
        ("/", DivisionStrategy),
        ("pow", PowerStrategy),
        ("√", RootStrategy),
    ],
)
def test_operation_factory_creates_strategies_from_names_aliases_and_symbols(
    operation, strategy_type
):
    assert isinstance(OperationFactory.create(operation), strategy_type)


def test_operation_factory_rejects_unsupported_operations():
    with pytest.raises(ValueError, match="Invalid operation"):
        OperationFactory.create("mod")
