---
name: web-tool
description: The web-tool skill defines two core network skill scripts available in the system, which can be used to perform advanced queries across multiple search engines, as well as scrape and extract in-depth readable content from web pages using a headless browser.
---

# 网页搜索与内容提取技能 (Web Search & Fetch SKILL)

This document defines two core network skill scripts available in the system: `web_search.py` and `web_fetch.py`. These tools can be used to perform advanced queries across multiple search engines, as well as scrape and extract in-depth readable content from web pages using a headless browser.

## Available scripts

- **`scripts/web_search.py`** – Performs a web search using multiple search engine backends.
- **`scripts/web_fetch.py`** – Fetches and extracts readable content from specific URLs using a headless browser.

## `web_search.py`

### Usage

usage: web_search.py [-h] [--region REGION] [--safesearch {on,moderate,off}] [--timelimit {d,w,m,y}] [--max-results MAX_RESULTS] [--page PAGE]
                     [--backend {auto,bing,brave,duckduckgo,google,grokipedia,mojeek,yandex,yahoo,wikipedia}] [--detailed_content] [--readable_text]
                     query

Performs a web search using multiple search engine backends

positional arguments:
  query                 Search query text

options:
  -h, --help            show this help message and exit
  --region REGION       Region code (default: us-en)
  --safesearch {on,moderate,off}
                        Safe search level (default: off)
  --timelimit {d,w,m,y}
                        Time limit: d, w, m, y (default: None)
  --max-results MAX_RESULTS
                        Maximum number of results (default: 10)
  --page PAGE           Page number (default: 1)
  --backend {auto,bing,brave,duckduckgo,google,grokipedia,mojeek,yandex,yahoo,wikipedia}
                        Backend engine (default: auto)
  --detailed_content    Will fetch and extract readable content using a headless browser.
  --readable_text       Print results as readable text

### Examples

- **Basic Search:** Search for results about Python programming
  `uv run scripts/web_search.py "Python programming"`
- **Detailed Content Retrieval:** Search and extract the full webpage content for all results about Python programming
  `uv run scripts/web_search.py "Python programming" --detailed_content`
- **Specify Search Engine and Time Range:** Search for last week's news about OpenAI updates on Google
  `uv run scripts/web_search.py "OpenAI updates" --backend google --timelimit w`


## `web_fetch.py`

### Usage

usage: web_fetch.py [-h] [--url URL]

Fetch and extract readable content from given URLs using a headless browser.

options:
  -h, --help  show this help message and exit
  --url URL   A URL to fetch and extract content from (can be used multiple times)

### Examples

- **Fetch a single webpage:** `uv run scripts/web_fetch.py --url "https://example.com/article1"`
- **Batch fetch multiple webpages:** `uv run scripts/web_fetch.py --url "https://example.com/page1" --url "https://example.com/page2"`

## Typical Workflow

In practical automation tasks or AI agent invocations, these two scripts are typically used in tandem:

1. First, `web_search.py` is employed to locate the source links (URLs) of relevant information.
2. The selected URLs are then passed to `web_fetch.py` to perform in-depth reading, content summarization, or information extraction.
