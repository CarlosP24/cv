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
        bib = f"@funding{{{key},\n"
        bib += f"title = {{{row['title']}}},\n"
        bib += f"code = {{{row['code']}}},\n"
        bib += f"agency = {{{row['agency']}}},\n"
        begin = row['begin']
        end = row['end']
        period = f"{begin}-{end}"
        bib += f"year = {{{begin}}},\n"
        bib += f"period = {{{period}}},\n"
        bib += f"institution = {{{row['institution']}}},\n"
        value = row['value']
        if not pd.isna(value):
            bib += f"value = {{{value}}},\n"
        PI = row['PI']
        if not pd.isna(PI):
            bib += f"pis = {{{PI}}},\n"
        bib += f"keywords = {{{row['type']}}},\n"
        bib += f"}}\n"
        f.write(bib)