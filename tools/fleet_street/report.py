import html
import os
import shutil
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit

from .budget import calculate_budget
from .files import canonical, json_text, write_new
from .validation import record, sequence, text


ASSETS = Path(__file__).parent / "assets"


def escaped(value: object, label: str) -> str:
    return html.escape(text(value, label), quote=True)


def source_html(value: object) -> str:
    source = record(value, {"label", "reference"}, "Source")
    label = escaped(source["label"], "source label")
    reference = text(source["reference"], "source reference")
    parsed = urlsplit(reference)
    if parsed.scheme:
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or any(character.isspace() for character in reference):
            raise ValueError("Source links require HTTPS and no embedded credentials")
        return f'<a href="{html.escape(reference, quote=True)}" rel="noreferrer noopener">{label}</a>'
    if reference.startswith(("/", "\\")) or ".." in reference.replace("\\", "/").split("/"):
        raise ValueError("Do not include absolute or parent-traversing local source paths in a report")
    return label + " — source reference <code>" + html.escape(reference) + "</code> (not included)"


def render_report(value: object, budget_input: object) -> tuple[str, dict[str, object]]:
    data = record(value, {"title", "subtitle", "status", "summary", "findings", "questions", "sources"}, "Report")
    title, subtitle, status, summary = (escaped(data[key], key) for key in ["title", "subtitle", "status", "summary"])
    findings: list[str] = []
    for entry in sequence(data["findings"], "findings"):
        finding = record(entry, {"label", "text"}, "Finding")
        label = text(finding["label"], "finding label")
        if label not in {"Supplied", "Verified", "Calculated", "Assumed", "Proposed", "Unknown"}:
            raise ValueError("Use an explicit supported finding category")
        findings.append(f'<li><span class="label">{html.escape(label)}:</span> {escaped(finding["text"], "finding text")}</li>')
    questions = ["<li>" + escaped(entry, "question") + "</li>" for entry in sequence(data["questions"], "questions")]
    sources = ["<li>" + source_html(entry) + "</li>" for entry in sequence(data["sources"], "sources")]
    budget = calculate_budget(budget_input)

    def money(value: object) -> str:
        return "GBP " + format(Decimal(str(value)), ",.2f")

    lines: list[str] = []
    for entry in sequence(budget["costs"], "calculated costs"):
        line = record(entry, {"label", "quantity", "unit_cost", "total"}, "Calculated cost")
        lines.append(f'<tr><td>{escaped(line["label"], "cost label")}</td><td>{line["quantity"]}</td><td>{money(line["total"])}</td></tr>')
    break_even = f'{budget["break_even_paid_tickets"]} paid tickets ({budget["break_even_occupancy_percent"]}% of saleable capacity)' if budget["break_even_possible"] else "Not achievable within the supplied saleable capacity"
    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="referrer" content="no-referrer"><title>{title} — feasibility note</title><link rel="icon" href="assets/proscenium.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/report.css"></head>
<body><main><header class="masthead"><p>FLEET STREET<br>THEATRE WORKING NOTE</p><img src="assets/proscenium.svg" alt="" width="160" height="120"></header>
<h1>{title}</h1><p class="subtitle">{subtitle}</p><p class="notice">{status}</p><p class="summary">{summary}</p>
<section aria-labelledby="budget"><h2 id="budget">Supplied cost scenario</h2><div class="totals"><div class="total"><span>Net receipts</span><strong>{money(budget["net_receipts"])}</strong></div><div class="total"><span>Total costs</span><strong>{money(budget["total_costs"])}</strong></div><div class="total"><span>Balance</span><strong>{money(budget["balance"])}</strong></div></div>
<p>Break-even: {break_even}. Expected paid tickets are a scenario assumption, not demonstrated demand.</p>
<div class="table-scroll"><table><thead><tr><th scope="col">Cost assumption</th><th scope="col">Quantity</th><th scope="col">Line total</th></tr></thead><tbody>{"".join(lines)}<tr><td>Contingency</td><td>On base costs</td><td>{money(budget["contingency"])}</td></tr></tbody></table></div><p>Excludes tax/VAT, payroll and cash-flow timing, grants, variable royalties and mixed ticket prices. <a href="data/budget.json">Calculated budget JSON</a></p></section>
<section aria-labelledby="findings"><h2 id="findings">Findings</h2><ul>{"".join(findings)}</ul></section>
<section aria-labelledby="questions"><h2 id="questions">Questions before commitment</h2><ol>{"".join(questions)}</ol></section>
<section aria-labelledby="sources"><h2 id="sources">Source references</h2><ul>{"".join(sources)}</ul></section>
<footer>This file is a locally prepared draft. Generating it does not publish it, confirm its statements or authorize disclosure. If released through crossfire, anyone with the resulting link can view every file in the publication.</footer></main></body></html>'''
    return document, budget


def create_report(value: object, budget_input: object, directory: Path) -> dict[str, object]:
    document, budget = render_report(value, budget_input)
    target = canonical(directory)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    target.mkdir(mode=0o700)
    try:
        write_new(target / "index.html", document + "\n")
        write_new(target / "data/budget.json", json_text(budget))
        for filename in ["report.css", "proscenium.svg"]:
            write_new(target / "assets" / filename, (ASSETS / filename).read_text())
    except BaseException:
        shutil.rmtree(target)
        raise
    os.chmod(target, 0o700)
    return {"directory": str(target), "files": 4, "published": False}
