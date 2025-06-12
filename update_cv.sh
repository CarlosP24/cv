#!/bin/sh

if [ "$#" -ne 7 ]; then
    echo "Usage: $0 <zotero_url> <talks_url> <outreach_url> <funding_url> <awards_url> <author_name> <output_pdf>"
    exit 1
fi

source ./bin/activate

ZOTERO_URL="$1"
TALKS_URL="$2"
OUTREACH_URL="$3"
FUNDING_URL="$4"
AWARDS_URL="$5"
AUTHOR_NAME="$6"
OUTPUT_PDF="$7"

python3 libraries/fetch_publications.py "$ZOTERO_URL" "$AUTHOR_NAME"
python3 libraries/js_to_bib.py conferences "$TALKS_URL" database/conferences.bib
python3 libraries/js_to_bib.py outreach "$OUTREACH_URL" database/outreach.bib
python3 libraries/js_to_bib.py funding "$FUNDING_URL" database/funding.bib
python3 libraries/js_to_bib.py awards "$AWARDS_URL" database/awards.bib

latexmk -synctex=1 -interaction=nonstopmode -file-line-error -lualatex CV.tex

mv CV.pdf "$OUTPUT_PDF"