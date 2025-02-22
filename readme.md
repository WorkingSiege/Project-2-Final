# Background

The UNL directory search has a minimum character count, and I wanted to ensure I was optimizing our queries to extract the most amount of data with the lowest number of requests. To do this, I downloaded a database of 151k of the most popular surnames, then I pre-processed (analysis/pre_processed.ipynb) them into 27k deduplicated surnames reduced to the first 4 characters.

Then, I built a multithreaded crawler to fetch, parse, and store the student profile information. To build a seamless experience with the GUI, I'm using multiprocessing's Manager and Queue to communicate the progress of the crawl and add new profiles to the data table, all in real time. I also did my best to implement pagination, as otherwise trying to load thousands of profiles is horribly slow and a bad user experience.

If given more time to improve, I would've fixed a few minor search bugs. Mainly, when you search while the crawler is active, it is does not persist your search query causing new profiles that do not match it to show up.

# How to Run

1. Install all requires dependencies

```
poetry install
```

2. Run main.py

```
poetry run python main.py
```

In accordance with [PEP-8](https://peps.python.org/pep-0008/), all imports are absolute imports. If you are running into module not found errors, ensure that the project has been added to PYTHONPATH.
#   P r o j e c t - 2 - F i n a l  
 