"""Observer interfaces and built-in calculation event observers."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.calculation import Calculation


@dataclass(frozen=True)
class CalculationEvent:
    """A calculator state change published to registered observers."""

    action: str
    history: tuple[Calculation, ...]
    calculation: Calculation | None = None
    result: float | None = None


class CalculationObserver(Protocol):
    """Receives calculator state change notifications."""

    def update(self, event: CalculationEvent) -> None:
        """React to a calculation or history state change."""


class LoggingObserver:
    """Log calculation, undo, and redo events through Python logging."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(__name__)

    def update(self, event: CalculationEvent) -> None:
        if event.calculation is not None:
            self._logger.info(
                "%s %s %s = %s",
                event.calculation.first_number,
                event.calculation.symbol,
                event.calculation.second_number,
                event.result,
            )
        else:
            self._logger.info("Calculator history action: %s", event.action)


class AutoSaveHistoryObserver:
    """Persist the latest calculation history as JSON after every state change."""

    def __init__(self, file_path: str | Path) -> None:
        self._file_path = Path(file_path)

    def update(self, event: CalculationEvent) -> None:
        records = [
            {
                "first_number": calculation.first_number,
                "operation": calculation.operation,
                "second_number": calculation.second_number,
                "result": calculation.calculate(),
            }
            for calculation in event.history
        ]
        self._file_path.write_text(
            json.dumps(records, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
