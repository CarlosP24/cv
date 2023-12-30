import pandas as pd
import os
import sys
from datetime import datetime

input = sys.argv[1]
output = sys.argv[2]

tsv = pd.read_csv(input, sep = "\t", header = 0)

with open(output, "w") as f:
    for index, row in tsv.iterrows():
        key = f"{row['code']}"
        bib = f"@award{{{key},\n"
        bib += f"title = {{{row['title']}}},\n"
        bib += f"institution = {{{row['institution']}}},\n"
        bib += f"year = {{{row['year']}}},\n"
        worktitle = row['worktitle']
        if not pd.isna(worktitle):
            bib += f"worktitle = {{{worktitle}}},\n"
        note = row['note']
        if not pd.isna(note):
            bib += f"note = {{{note}}},\n"
        editions = row['editions']
        if not pd.isna(editions):
            bib += f"period = {{{editions}}},\n"
        bib += f"}}\n"
        f.write(bib)