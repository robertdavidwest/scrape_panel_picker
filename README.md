# Dependencies

### Python Packages:
* `beautifulsoup4` (web scraping)
* `pandas` (analysis)
* `numpy` (analysis)
* `nltk.corpus` (for stopwords in NLP analysis)

### Other:
* `pandoc` (to convert `.md` to `.html`)

# Py files

* `scrape_panel_picker.py`: Scrapes [http://panelpicker.sxsw.com/vote]() for all Panel proposals. Picks up all meta data, proposal titles and proposal descriptions. Stores the data in json
* * `analyse_panel_picker_data.py`: Reads in json, calculates distribution of meta data and creates tables (and option plots), uses NLP to find top N words in titles and descriptions (1 per item). Creates html report of results.