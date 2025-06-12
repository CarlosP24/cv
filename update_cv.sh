#!/bin/sh

source ./bin/activate    

python3 libraries/fetch_publications.py https://api.zotero.org/users/13410489/publications/items?format=bibtex "Payá, Carlos"
python3 libraries/js_to_bib.py conferences https://carlosp24.github.io/js/talks.js database/conferences.bib
python3 libraries/js_to_bib.py outreach https://carlosp24.github.io/js/outreach.js database/outreach.bib
python3 libraries/js_to_bib.py funding https://carlosp24.github.io/js/funding.js database/funding.bib
python3 libraries/js_to_bib.py awards https://carlosp24.github.io/js/awards.js database/awards.bib

latexmk -synctex=1 -interaction=nonstopmode -file-line-error -lualatex CV.tex

cp CV.pdf ../Personal_web/files/