"""Professional Calculator command loop and CLI entry point."""

from colorama import Fore, init

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import (
    INVALID_OPERATION_MESSAGE,
    OPERATION_ALIASES,
    OPERATION_SYMBOLS,
    VALID_OPERATIONS,
)
from app.calculator_observers import LoggingObserver
from app.exceptions import InvalidOperationError
from app.input_validators import parse_number

init(autoreset=True)

OPERATION_COLORS = {
    "add": Fore.CYAN,
    "subtract": Fore.YELLOW,
    "multiply": Fore.MAGENTA,
    "divide": Fore.RED,
    "power": Fore.GREEN,
    "root": Fore.BLUE,
}


def _print_help() -> None:
    """Display the commands and arithmetic operations available in the REPL."""
    print("Commands: help, history, undo, redo, exit")
    print(
        "Operations: "
        + ", ".join(
            f"{name} ({OPERATION_SYMBOLS[name]})" for name in OPERATION_ALIASES
        )
    )
    print(
        "Aliases: "
        + ", ".join(
            alias
            for aliases in OPERATION_ALIASES.values()
            for alias in aliases[1:-1]
        )
    )


def _print_history(history: tuple[Calculation, ...]) -> None:
    """Display successful calculations recorded during this session."""
    if not history:
        print("No calculations in history.")
        return

    for index, calculation in enumerate(history, start=1):
        result = calculation.calculate()
        if calculation.operation == "root":
            expression = (
                f"{calculation.second_number}√({calculation.first_number})"
            )
        else:
            expression = (
                f"{calculation.first_number} {calculation.symbol} "
                f"{calculation.second_number}"
            )
        print(f"{index}. {expression} = {result}")


def run_interactive(calculator: Calculator | None = None) -> None:
    """Run the calculator's read-evaluate-print loop."""
    calculator = calculator or Calculator(observers=(LoggingObserver(),))
    print("-------------------- Professional Calculator --------------------")
    print("Available operations: " + ", ".join(OPERATION_ALIASES))
    print("----------------------------------------------------------------")

    for operation_name, aliases in OPERATION_ALIASES.items():
        symbol = OPERATION_SYMBOLS[operation_name]
        print(
            OPERATION_COLORS[operation_name]
            + f"For {operation_name}, enter: {', '.join(aliases[:-1])}, or {symbol}"
        )

    print("----------------------------------------------------------------")
    print(
        "Type 'help' for commands, 'history' for results, 'undo' or 'redo' "
        "to change history, or 'exit' to quit."
    )

    while True:
        try:
            operation = input("Choose an operation: ").strip()
            command = operation.lower()

            if command in {"quit", "exit", "q"}:
                print("Goodbye!")
                break
            if command == "help":
                _print_help()
                continue
            if command == "history":
                _print_history(calculator.history)
                continue
            if command == "undo":
                print(
                    "Undid the last calculation."
                    if calculator.undo()
                    else "Nothing to undo."
                )
                continue
            if command == "redo":
                print(
                    "Redid the last calculation."
                    if calculator.redo()
                    else "Nothing to redo."
                )
                continue

            if command not in VALID_OPERATIONS:
                raise InvalidOperationError(INVALID_OPERATION_MESSAGE)

            first_number = parse_number(
                input(
                    "Enter the number to take a root of: "
                    if command in {"root", "nthroot", "√"}
                    else "Enter the first number: "
                ).strip(),
                "first",
            )
            second_number = parse_number(
                input(
                    "Enter the root degree: "
                    if command in {"root", "nthroot", "√"}
                    else "Enter the second number: "
                ).strip(),
                "second",
            )
            result = calculator.calculate(first_number, command, second_number)
            print(f"Result: {result}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        except ValueError as exc:
            print(f"Error: {exc}")
        except ZeroDivisionError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    run_interactive()
