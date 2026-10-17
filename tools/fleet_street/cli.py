import argparse
import sys
from decimal import DecimalException
from pathlib import Path

from .budget import calculate_budget
from .configuration import configure
from .files import json_text, read_json, write_new
from .report import create_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline tools for the fleet-street theatre example. No enrollment, model calls or publication.")
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("configure", help="Prepare a private working fleet without enrolling or starting it")
    setup.add_argument("--server", required=True)
    setup.add_argument("--owner", required=True)
    setup.add_argument("--prefix", required=True)
    setup.add_argument("--model")
    budget = commands.add_parser("budget", help="Calculate one explicit paid-ticket scenario")
    budget.add_argument("--input", required=True, type=Path)
    budget.add_argument("--output", required=True, type=Path)
    report = commands.add_parser("report", help="Format a local HTML/CSS/SVG directory; never publish it")
    report.add_argument("--input", required=True, type=Path)
    report.add_argument("--budget", required=True, type=Path)
    report.add_argument("--directory", required=True, type=Path)
    options = parser.parse_args(argv)
    try:
        if options.command == "configure":
            result = configure(options.server, options.owner, options.prefix, options.model)
        elif options.command == "budget":
            result = calculate_budget(read_json(options.input))
            write_new(options.output, json_text(result))
        else:
            result = create_report(read_json(options.input), read_json(options.budget), options.directory)
        print(json_text(result), end="")
        return 0
    except (OSError, ValueError, DecimalException) as error:
        print(f"fleet-street: {error}", file=sys.stderr)
        return 2
