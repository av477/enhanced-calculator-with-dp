from app.calculation import CalculationFactory
from app.history import CalculationHistory


def test_history_adds_calculations_and_returns_an_immutable_view():
    history = CalculationHistory()
    calculation = CalculationFactory.create_calculation(2, "+", 3)

    history.add(calculation)

    assert history.get_all() == (calculation,)


def test_history_memento_restores_a_previous_snapshot():
    history = CalculationHistory()
    first = CalculationFactory.create_calculation(2, "+", 3)
    second = CalculationFactory.create_calculation(8, "*", 4)
    history.add(first)
    memento = history.create_memento()

    history.add(second)
    history.restore(memento)

    assert history.get_all() == (first,)

