#!/bin/sh
# Update CV

# Update bib databases
# Update publications in web first!! 

python3 libraries/tsv_to_bib.py ../Personal_web/markdown_generator/outreach.tsv database/outreach.bib
python3 libraries/tsv_to_bib.py ../Personal_web/markdown_generator/talks.tsv database/conferences.bib
python3 libraries/tsv_to_bib_funding.py database/funding.tsv database/funding.bib
python3 libraries/tsv_to_bib_awards.py database/awards.tsv database/awards.bib

latexmk -synctex=1 -interaction=nonstopmode -file-line-error -lualatex CV.tex

cp CV.pdf ../Personal_web/files/