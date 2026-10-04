"""Session history for successful calculations."""

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


class CalculationHistory:
    """Store calculations and support snapshot-based state restoration."""

    def __init__(self) -> None:
        self._calculations: list[Calculation] = []

    def add(self, calculation: Calculation) -> None:
        """Append a successful calculation to history."""
        self._calculations.append(calculation)

    def get_all(self) -> tuple[Calculation, ...]:
        """Return an immutable view of the current history."""
        return tuple(self._calculations)

    def create_memento(self) -> CalculatorMemento:
        """Capture the current history for later restoration."""
        return CalculatorMemento(self.get_all())

    def restore(self, memento: CalculatorMemento) -> None:
        """Replace the current history with a previously captured snapshot."""
        self._calculations = list(memento.calculations)

