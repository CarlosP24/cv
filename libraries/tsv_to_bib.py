import pandas as pd
import os
import sys
from datetime import datetime

input = sys.argv[1]
output = sys.argv[2]

tsv = pd.read_csv(input, sep = "\t", header = 0)

type_w_titles = ["Poster", "Oral", "Contributed"]
outreach_types = ["Workshopper", "Logistics"]

with open(output, "w") as f:
    for index, row in tsv.iterrows():
        key = "".join(row["url_slug"].split(" "))
        bib = f"@unpublished{{{key},\n"
        bib += f"title = {{{row['title']}}},\n"
        bib += f"venue = {{{row['venue']}, {row['location']}}},\n"
        month, year = row["date"].split(" ")
        month = datetime.strptime(month, "%B").strftime("%m")
        bib += f"month = {{{month}}},\n"
        bib += f"year = {{{year}}},\n"
        type = row['type']
        bib += f"keywords = {{{type}}},\n"
        if type in type_w_titles:
            bib += f"type = {{ {type} title:}},\n"
            bib += f"note = {{{row['cont_title']}}},\n"
            bib += f"url = {{{row['pdf_url']}}},\n"
        elif type in outreach_types:
            bib += f"type = {{ Role:}},\n"
            bib += f"note = {{{type.lower()}}},\n"
            bib += f"url = {{{row['talk_url']}}},\n"
        bib += f"}}\n"
        f.write(bib)