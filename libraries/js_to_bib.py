import requests
import re
import sys
import json
from datetime import datetime
import os

def extract_json(js_text, callback):
    match = re.search(rf'{callback}\(\s*({{[\s\S]*?}})\s*\);', js_text)
    if not match:
        raise ValueError(f"Could not find {callback} JSON object in JS file.")
    return json.loads(match.group(1))

def bib_conference(row):
    type_w_titles = ["Poster", "Oral", "Tutorial", "Contributed"]
    outreach_types = ["Speaker", "Workshopper", "Logistics"]
    key = "".join(row.get("url_slug", "").split(" "))
    bib = f"@unpublished{{{key},\n"
    bib += f"title = {{{row.get('title', '')}}},\n"
    bib += f"venue = {{{row.get('venue', '')}, {row.get('location', '')}}},\n"
    date_str = row.get("date", "")
    if date_str:
        try:
            month, year = date_str.split(" ")
            month_num = datetime.strptime(month, "%B").strftime("%m")
            bib += f"month = {{{month_num}}},\n"
            bib += f"year = {{{year}}},\n"
        except Exception:
            pass
    type_ = row.get('type', '')
    bib += f"keywords = {{{type_}}},\n"
    # Slides (PDF or Quarto HTML) are the link target; outreach falls back to the event page
    slides_url = row.get('pdf_url', '') or row.get('html_url', '')
    url = ''
    if type_ in type_w_titles:
        bib += f"type = {{ {type_} title:}},\n"
        bib += f"note = {{{row.get('cont_title', '')}}},\n"
        url = slides_url
    elif type_ in outreach_types:
        bib += f"type = {{ Role:}},\n"
        bib += f"note = {{{type_.lower()}}},\n"
        url = slides_url or row.get('talk_url', '')
    if url:
        bib += f"url = {{{url}}},\n"
    bib += f"}}\n"
    return bib

def bib_funding(row):
    key = f"{row.get('code', '')}"
    bib = f"@funding{{{key},\n"
    bib += f"title = {{{row.get('title', '')}}},\n"
    bib += f"code = {{{row.get('code', '')}}},\n"
    bib += f"agency = {{{row.get('agency', '')}}},\n"
    begin = row.get('begin', '')
    end = row.get('end', '')
    period = f"{begin}-{end}" if begin and end else ""
    if begin:
        bib += f"year = {{{begin}}},\n"
    if period:
        bib += f"period = {{{period}}},\n"
    bib += f"institution = {{{row.get('institution', '')}}},\n"
    value = row.get('value', "")
    if value:
        bib += f"value = {{{value}}},\n"
    PI = row.get('PI', "")
    if PI:
        bib += f"pis = {{{PI}}},\n"
    bib += f"keywords = {{{row.get('type', '')}}},\n"
    bib += f"}}\n"
    return bib

def bib_award(row):
    key = f"{row.get('code', '')}"
    bib = f"@award{{{key},\n"
    bib += f"title = {{{row.get('title', '')}}},\n"
    bib += f"institution = {{{row.get('institution', '')}}},\n"
    bib += f"year = {{{row.get('year', '')}}},\n"
    worktitle = row.get('worktitle', "")
    if worktitle:
        bib += f"worktitle = {{{worktitle}}},\n"
    note = row.get('note', "")
    if note:
        bib += f"note = {{{note}}},\n"
    editions = row.get('editions', "")
    if editions:
        bib += f"period = {{{editions}}},\n"
    bib += f"}}\n"
    return bib

# Supervised students are written as \job entries (see structure.tex), not bib entries
STUDENT_KINDS = {
    "bachelor": "Bachelor's Thesis",
    "master": "Master's Thesis",
    "phd": "PhD Thesis",
    "short-stay": "Short stay",
}

def student_date_key(row):
    # "Sep 2024" / "September 2024" -> (2024, 9)
    parts = row.get("begin", "").split()
    try:
        month = datetime.strptime(parts[0][:3], "%b").month if len(parts) > 1 else 0
        return (int(parts[-1]), month)
    except (ValueError, IndexError):
        return (0, 0)

def tex_student(row):
    type_ = row.get("type", "")
    kind = STUDENT_KINDS.get(type_.lower(), type_)
    is_main = row.get("role", "").lower() == "supervisor"
    # \href inside a macro argument needs % and # escaped
    url = row.get("url", "").replace("%", r"\%").replace("#", r"\#")
    others = row.get("other_supervisors", "")
    if others:
        label = "Co-supervisor" if is_main else "Main supervisor"
        plural = "s" if (" and " in others or "," in others) else ""
        others = f"{label}{plural}: {others}"
    details = []
    if row.get("institution"):
        details.append(f"Institution: {row['institution']}")
    if row.get("title"):
        label = "Project" if type_.lower() == "short-stay" else "Title"
        details.append(f"{label}: \\textit{{{row['title']}}}")
    tex = "\\job\n"
    tex += f"{{{row.get('begin', '')} -}}{{{row.get('end', '') or 'Present'}}}\n"
    tex += f"{{{row.get('name', '')} - {kind}}}\n"
    tex += f"{{{url}}}\n"
    tex += f"{{{others}}}\n"
    tex += "{" + r" \\ ".join(details) + "}\n\n"
    return tex

# Map mode to callback and bib function
MODES = {
    "conferences": ("talksFeed", bib_conference),
    "outreach": ("outreachFeed", bib_conference),
    "funding": ("fundingFeed", bib_funding),
    "awards": ("awardsFeed", bib_award),
    "students": ("studentsFeed", tex_student),
}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python js_to_bib.py <mode> <js_url_or_path> [output.bib]")
        sys.exit(1)
    mode = sys.argv[1]
    js_input = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else f"{mode}.bib"

    if mode not in MODES:
        print(f"Unknown mode '{mode}'. Choose from: {', '.join(MODES.keys())}")
        sys.exit(1)

    callback, bib_func = MODES[mode]

    # Determine if input is a URL or a local file path
    if js_input.startswith("http://") or js_input.startswith("https://"):
        response = requests.get(js_input)
        js_text = response.text
    elif os.path.isfile(js_input):
        with open(js_input, "r", encoding="utf-8") as f:
            js_text = f.read()
    else:
        print(f"Input '{js_input}' is not a valid URL or file path.")
        sys.exit(1)

    data = extract_json(js_text, callback)
    entries = data.get("entries", [])
    if mode == "students":
        # Newest first; bib entries are sorted by biblatex instead
        entries = sorted(entries, key=student_date_key, reverse=True)

    with open(output, "w") as f:
        for row in entries:
            f.write(bib_func(row))

    print(f"Saved {output}")