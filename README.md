# CV
Nice and curated CV made from js files in my website.

## Setup

1. Install [pyenv](https://github.com/pyenv/pyenv).
2. Run `pyenv install` to install the required Python version.
3. Run `pyenv local $(cat .python-version)` to set the local Python version.
4. Run `pip install -r requirements.txt` to install dependencies.


## Usage
'''
./update_cv.sh \
  "https://api.zotero.org/users/13410489/publications/items?format=bibtex" \
  "https://carlosp24.github.io/js/talks.js" \
  "https://carlosp24.github.io/js/outreach.js" \
  "https://carlosp24.github.io/js/funding.js" \
  "https://carlosp24.github.io/js/awards.js" \
  "Payá, Carlos" \
  "MyCV.pdf"
'''