import requests
import re
import os
import sys
import time
import json

def add_highlight_keyword(entry, author_name="Payá, Carlos", extra_keyword=None):
    # Find the author field
    author_match = re.search(r'author\s*=\s*[{"]([^}"]+)[}"]', entry, re.IGNORECASE)
    if not author_match:
        return entry  # No author field found, return as is

    authors = [a.strip() for a in author_match.group(1).replace('\n', ' ').split(' and ')]
    try:
        position = authors.index(author_name) + 1  # 1-based index
    except ValueError:
        position = 0  # Not found

    # Check for FTheory:number in note field
    ftheory_match = re.search(r'note\s*=\s*[{"][^}"]*FTheory:(\d+)[^}"]*[}"]', entry, re.IGNORECASE)
    highlight_dict = {position: ["highlight"]} if position else {}

    if ftheory_match:
        ftheory_number = int(ftheory_match.group(1))
        if ftheory_number in highlight_dict:
            if "first" not in highlight_dict[ftheory_number]:
                highlight_dict[ftheory_number].append("first")
        else:
            highlight_dict[ftheory_number] = ["first"]

    # Remove any existing author+an field
    entry = re.sub(
        r'\s*author\+an\s*=\s*\{[^}]*\},?\s*\n?', '', entry, flags=re.IGNORECASE
    )

    # Compose author+an string
    authoran_list = []
    for num, annots in sorted(highlight_dict.items()):
        authoran_list.append(f"{num}=" + ",".join(annots))
    authoran_field = ', '.join(authoran_list)

    # Insert author+an field before the last closing brace, with a comma
    if authoran_field:
        entry = re.sub(
            r'(\n})\s*$',
            f'\n\tauthor+an = {{{authoran_field}}}\n}}',
            entry,
            count=1
        )

    # Handle keywords field
    if extra_keyword:
        def append_keyword(m):
            existing = m.group(2).strip()
            keywords = [k.strip() for k in existing.split(',') if k.strip()]
            if extra_keyword not in keywords:
                keywords.append(extra_keyword)
            return m.group(1) + ', '.join(keywords)
        if re.search(r'keywords?\s*=', entry, re.IGNORECASE):
            entry = re.sub(
                r'(keywords?\s*=\s*[{"])([^}"]*)',
                append_keyword,
                entry,
                flags=re.IGNORECASE
            )
        else:
            entry = re.sub(
                r'(\n})\s*$',
                f',\n\tkeywords = {{{extra_keyword}}}\n}}',
                entry,
                count=1
            )
    return entry

def fix_misc_note(entry):
    # For @misc entries, keep only the first "arXiv:..." element in the note field
    if entry.strip().lower().startswith('@misc'):
        # Find the note field
        note_match = re.search(r'(note\s*=\s*\{)([^}]*)\}', entry, re.IGNORECASE)
        if note_match:
            note_content = note_match.group(2)
            # Find the first "arXiv:..." substring
            arxiv_match = re.search(r'arXiv:[^\s,;}\]]+', note_content)
            if arxiv_match:
                arxiv_str = arxiv_match.group(0)
                # Replace the note field with only the arXiv string
                entry = re.sub(
                    r'(note\s*=\s*\{)[^}]*\}',
                    rf'\1{arxiv_str}}}',
                    entry,
                    flags=re.IGNORECASE
                )
    return entry

def fix_month_brackets(entry):
    # Replace month = value or month = "value" with month = {value}
    return re.sub(
        r'month\s*=\s*["{]?([a-zA-Z]+)["}]?',
        r'month = {\1}',
        entry
    )

def multiline_bib_entry(entry):
    entry = re.sub(r',\s*(?=\w+\s*=)', ',\n\t', entry)
    entry = re.sub(r'(@\w+{)', r'\1\n\t', entry)
    return entry

def remove_unwanted_fields(entry):
    # Remove unwanted fields (case-insensitive), even if they contain special characters, line breaks, or braces
    fields = ['copyright', 'issn', 'shorttitle', 'abstract', 'urldate', 'url']
    for field in fields:
        entry = re.sub(
            rf'\s*{field}\s*=\s*\{{((?:[^{{}}]*|\{{[^{{}}]*\}})*)\}},?\s*\n?', '', entry, flags=re.IGNORECASE | re.DOTALL
        )
    return entry

def fetch_citation_metrics(entry):
    """
    Fetch citation metrics for @article entries with DOI and add citations field.
    """
    if not entry.strip().lower().startswith('@article'):
        return entry
    
    # Extract DOI from the entry
    doi_match = re.search(r'doi\s*=\s*[{"]([^}"]+)[}"]', entry, re.IGNORECASE)
    if not doi_match:
        return entry
    
    doi = doi_match.group(1).strip()
    
    try:
        # Fetch metrics from Dimensions API
        metrics_url = f"https://metrics-api.dimensions.ai/doi/{doi}"
        response = requests.get(metrics_url, timeout=10)
        
        if response.status_code == 200:
            metrics = response.json()
            times_cited = metrics.get('times_cited', 0)
            
            # Add citations field to the entry
            entry = re.sub(
                r'(\n})\s*$',
                f',\n\tcitations = {{{times_cited}}}\n}}',
                entry,
                count=1
            )
            
            print(f"Added citations ({times_cited}) for DOI: {doi}")
            
        else:
            print(f"Failed to fetch metrics for DOI: {doi} (status: {response.status_code})")
            
    except Exception as e:
        print(f"Error fetching metrics for DOI {doi}: {e}")
    
    # Add a small delay to be respectful to the API
    time.sleep(0.5)
    
    return entry

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fetch_publications.py <zotero_bibtex_url> <author_name>")
        sys.exit(1)

    url = sys.argv[1]
    author_name = sys.argv[2]

    response = requests.get(url)
    bibtex_data = response.text

    # Split entries
    all_entries = []

    # Use regex to split into entries
    entries = re.split(r'(?=@\w+{)', bibtex_data)

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        entry = fix_month_brackets(entry)
        entry = remove_unwanted_fields(entry)
        if entry.startswith('@article'):
            entry = add_highlight_keyword(entry, author_name=author_name, extra_keyword="journal")
            entry = fetch_citation_metrics(entry)  # Add this line
            all_entries.append(entry)
        elif entry.startswith('@misc'):
            entry = fix_misc_note(entry)
            all_entries.append(add_highlight_keyword(entry, author_name=author_name, extra_keyword="preprint"))
        else:
            all_entries.append(entry)

    # Ensure database directory exists (relative to script location)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    database_dir = os.path.join(base_dir, 'database')
    os.makedirs(database_dir, exist_ok=True)

    # Write to database/pubs.bib
    with open(os.path.join(database_dir, 'pubs.bib'), 'w', encoding='utf-8') as f:
        for entry in all_entries:
            f.write(multiline_bib_entry(entry) + '\n\n')

    print("Saved database/pubs.bib.")