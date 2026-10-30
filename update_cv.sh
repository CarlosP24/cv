#!/bin/sh

if [ "$#" -lt 6 ] || [ "$#" -gt 8 ]; then
    echo "Usage: $0 <zotero_url> <talks_url> <outreach_url> <funding_url> <awards_url> <author_name> [arxiv_publications_js_path] [students_url]"
    exit 1
fi

source ./bin/activate

ZOTERO_URL="$1"
TALKS_URL="$2"
OUTREACH_URL="$3"
FUNDING_URL="$4"
AWARDS_URL="$5"
AUTHOR_NAME="$6"
ARXIV_JS="$7"
STUDENTS_URL="$8"

python3 libraries/fetch_publications.py "$ZOTERO_URL" "$AUTHOR_NAME" $ARXIV_JS
python3 libraries/js_to_bib.py conferences "$TALKS_URL" database/conferences.bib
python3 libraries/js_to_bib.py outreach "$OUTREACH_URL" database/outreach.bib
python3 libraries/js_to_bib.py funding "$FUNDING_URL" database/funding.bib
python3 libraries/js_to_bib.py awards "$AWARDS_URL" database/awards.bib
# Without a students feed, the committed database/students.tex is used as is
if [ -n "$STUDENTS_URL" ]; then
    python3 libraries/js_to_bib.py students "$STUDENTS_URL" database/students.tex
fi

#latexmk -synctex=1 -interaction=nonstopmode -file-line-error -lualatex CV.tex

#mv CV.pdf "$OUTPUT_PDF"