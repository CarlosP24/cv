#!/bin/sh
# Update CV
# Update bib databases
# Update publications in web first!! 
# requires local environment with python3 and pandas

source ./bin/activate    

python3 libraries/fetch_publications.py
python3 libraries/tsv_to_bib.py ../Personal_web/db/outreach.tsv database/outreach.bib
python3 libraries/tsv_to_bib.py ../Personal_web/db/talks.tsv database/conferences.bib
python3 libraries/tsv_to_bib_funding.py ../Personal_web/db/funding.tsv database/funding.bib
python3 libraries/tsv_to_bib_awards.py ../Personal_web/db/awards.tsv database/awards.bib

latexmk -synctex=1 -interaction=nonstopmode -file-line-error -lualatex CV.tex

cp CV.pdf ../Personal_web/files/