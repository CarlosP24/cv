import requests
import re
import os

# Download BibTeX data
url = "https://api.zotero.org/users/13410489/publications/items?format=bibtex"
response = requests.get(url)
bibtex_data = response.text

# Split entries
article_entries = []
misc_entries = []

# Use regex to split into entries
entries = re.split(r'(?=@\w+{)', bibtex_data)
for entry in entries:
    if entry.strip().startswith('@article'):
        article_entries.append(entry.strip())
    elif entry.strip().startswith('@misc'):
        misc_entries.append(entry.strip())

# Ensure database directory exists (relative to script location)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
database_dir = os.path.join(base_dir, 'database')
os.makedirs(database_dir, exist_ok=True)

# Write to database/pubs.bib
with open(os.path.join(database_dir, 'pubs.bib'), 'w', encoding='utf-8') as f:
    for entry in article_entries:
        f.write(entry + '\n\n')

# Write to database/preprints.bib
with open(os.path.join(database_dir, 'preprints.bib'), 'w', encoding='utf-8') as f:
    for entry in misc_entries:
        f.write(entry + '\n\n')

print("Done! Saved database/pubs.bib and database/preprints.bib.")