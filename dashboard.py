"""
Renders the real run into docs/index.html, replacing the placeholder shell.

Regenerates the whole file from the shell's exact markup and style tokens; this
fills placeholders, it does not redesign. Self-contained: no JavaScript, no
external assets or fonts, no CDN. The avatar is a local relative path.

The Estate Overview page is where the briefing's "the rest are on the Estate
Overview" sentence has to be true, so this shows ALL surfaced findings, not the
top 3.

Rendered at run end only (from run_observation), never on a button tap.
"""

from telegram_out import _esc, _local_timestamp

OUTPUT_PATH = "docs/index.html"

STYLE = """    :root{--ink:#080808;--red:#E6392D;--blue:#1E5FBF;--yellow:#F4C430;--ivory:#F7F4ED;--slate:#6B7280;--line:1px solid rgba(8,8,8,.18)}

    *{box-sizing:border-box}
    html,body{margin:0;background:var(--ivory);color:var(--ink)}
    body{font-family:"Helvetica Neue",Arial,sans-serif;line-height:1.45}
    main{width:min(100% - 24px,720px);margin:auto;padding:16px 0 48px}

    header{display:flex;align-items:center;gap:12px;border-bottom:2px solid var(--ink);padding-bottom:14px}
    header img{width:44px;height:44px;display:block}
    .name{font-weight:800;letter-spacing:.08em;font-size:18px}
    .tagline{margin-top:3px;color:var(--slate);font-size:12px}

    .funnel{display:grid;grid-template-columns:1fr;gap:0;border:2px solid var(--ink);margin:20px 0}
    .cell{padding:16px;border-bottom:var(--line)}
    .cell:last-child{border-bottom:0}
    .cell .num{font-size:32px;font-weight:800;line-height:1}
    .cell .cap{font-size:10px;letter-spacing:.15em;font-weight:800;color:var(--slate);margin-top:8px}

    section{margin:24px 0}
    h2{font-size:20px;letter-spacing:-.01em;margin:0 0 14px;border-bottom:2px solid var(--ink);padding-bottom:8px}

    .card{border:2px solid var(--ink);padding:16px}
    .block{padding:12px 0;border-bottom:var(--line)}
    .block:first-child{padding-top:0}
    .label{font-size:10px;letter-spacing:.15em;font-weight:800;margin-bottom:6px}
    .value{font-size:14px}
    .reco{padding-top:12px;font-size:14px;font-weight:700}

    .quiet{font-size:14px;color:var(--slate)}

    footer{border-top:2px solid var(--ink);padding-top:14px;margin-top:28px;color:var(--slate);font-size:12px}"""


def _funnel(run_result):
    surfaced_count = len(run_result.surfaced)
    cells = [
        (run_result.observed_count, "OBSERVED"),
        (run_result.signaled_count, "SIGNALED"),
        (run_result.investigated_count, "INVESTIGATED"),
        (surfaced_count, "SURFACED"),
    ]
    inner = "\n".join(
        f'      <div class="cell"><div class="num">{num}</div>'
        f'<div class="cap">{cap}</div></div>'
        for num, cap in cells
    )
    return f'    <div class="funnel">\n{inner}\n    </div>'


def _finding_card(finding):
    checked = finding.what_checked
    checked_str = ", ".join(checked) if checked else "nothing"
    return (
        '      <div class="card">\n'
        '        <div class="block">\n'
        '          <div class="label">WHY THIS SURFACED</div>\n'
        f'          <div class="value">{_esc(finding.why_surfaced)}</div>\n'
        "        </div>\n"
        '        <div class="block">\n'
        '          <div class="label">WHAT I CHECKED</div>\n'
        f'          <div class="value">{_esc(checked_str)}</div>\n'
        "        </div>\n"
        '        <div class="block">\n'
        '          <div class="label">WHAT I FOUND</div>\n'
        f'          <div class="value">{_esc(finding.what_found)}</div>\n'
        "        </div>\n"
        '        <div class="block">\n'
        "          <div class=\"label\">WHAT I CAN'T KNOW</div>\n"
        f'          <div class="value">{_esc(finding.what_cant_know)}</div>\n'
        "        </div>\n"
        f'        <div class="reco">Recommendation: {_esc(finding.recommendation)}'
        f". {_esc(finding.recommendation_reason)}</div>\n"
        "      </div>"
    )


def _needs_you_section(run_result):
    if not run_result.surfaced:
        return (
            "    <section>\n"
            "      <h2>Needs you</h2>\n"
            '      <div class="quiet">Nothing surfaced this run. Nothing needs '
            "you right now.</div>\n"
            "    </section>"
        )
    cards = "\n".join(_finding_card(f) for f in run_result.surfaced)
    return "    <section>\n      <h2>Needs you</h2>\n" + cards + "\n    </section>"


def _quiet_section(run_result):
    """
    Two distinguished groups. The person switch (I -> you) carries the
    distinction and is intentional; the labels are not a matched pair.
      I DIDN'T SURFACE THESE   -> the model's SUPPRESS findings
      YOU ALREADY DECIDED THESE -> auto_suppressed_note entries
    """
    parts = []

    if run_result.suppressed:
        rows = "\n".join(
            f'      <div class="value">{_esc(f.repo)}: '
            f"{_esc(f.recommendation_reason)}</div>"
            for f in run_result.suppressed
        )
        parts.append(
            '      <div class="label">I DIDN\'T SURFACE THESE</div>\n' + rows
        )

    if run_result.auto_suppressed_note:
        rows = "\n".join(
            f'      <div class="value">{_esc(note)}</div>'
            for note in run_result.auto_suppressed_note
        )
        parts.append(
            '      <div class="label">YOU ALREADY DECIDED THESE</div>\n' + rows
        )

    if not parts:
        body = '      <div class="quiet">Nothing quiet to report.</div>'
    else:
        body = '\n      <div class="block"></div>\n'.join(parts)

    return "    <section>\n      <h2>Quiet</h2>\n" + body + "\n    </section>"


def render_html(run_result):
    """Build the full self-contained HTML string for the Estate Overview page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Observator Clew: Estate Overview</title>
  <style>
{STYLE}
  </style>
</head>
<body>
  <main>
    <header>
      <img src="assets/avatar-256.png" alt="Observator Clew">
      <div>
        <div class="name">OBSERVATOR CLEW</div>
        <div class="tagline">Creating is becoming nearly free. Maintaining never did.</div>
      </div>
    </header>

{_funnel(run_result)}

{_needs_you_section(run_result)}

{_quiet_section(run_result)}

    <footer>Last observation: {_esc(_local_timestamp(run_result.run_at))}</footer>
  </main>
</body>
</html>
"""


def render_dashboard(run_result, output_path=OUTPUT_PATH):
    """Write the rendered page to disk, replacing the placeholder shell."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(render_html(run_result))
