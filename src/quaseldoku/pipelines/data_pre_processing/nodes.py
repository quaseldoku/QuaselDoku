"""
This is a boilerplate pipeline 'data_pre_processing'
generated using Kedro 0.18.0
"""

import pandas as pd
import re

from typing import Any, Callable, Dict
from bs4 import BeautifulSoup

def filter_doku(partitioned_input: Dict[str, Callable[[], Any]], params: Dict) -> Dict[str, Callable[[], Any]]:
    """
    flatten input where html files can occur on multiple levels, as well as filter out files that match certain string.
    Return new Dictionary with filenames and load functions from which a PartioniedDataset can be created and persisted.

    Args:
        partitioned_input: A dictionary with partition ids (file path) as keys and load functions as values.

    Returns:
        Dictionary with the partitions to create.
    """

    result = {}

    for partition_key, partition_load_func in sorted(partitioned_input.items()):

        exclude = False
        for string in params['exclude_docs']:
            if string in partition_key:
                exclude = True
                break

        if exclude: continue

        # suffix gets lost when loading files using suffix as filter, so needs to be appended back here
        filename = partition_key.replace('/', '_') + 'html'
        result[filename] = partition_load_func # append new filename with load function to results dictionary

    return result


def parse_html(doc: str) -> list:
    # TODO : DOKU

    # parse html
    parsed = BeautifulSoup(doc, 'html.parser')

    # get title
    title = parsed.h1.get_text()

    # gather subtopics
    sub_topics = []
    for sub_topic in parsed.find_all('h2'):
        sub_topics.append(sub_topic.get_text())

    # gather main text body
    body = parsed.get_text()

    # use regex to strip new line marker
    body_clean = re.sub(r'\n\s*\n', r'\n\n', parsed.get_text().strip(), flags=re.M)

    # gather all links from document
    links = []
    for link in parsed.find_all('a'):
        links.append(link.get('href'))

    # # gather all paragraphs
    # ps = []
    # for text in parsed.find_all('p'):
    #     ps.append(text.get_text())

    # gather images
    imgs = []
    for img in parsed.find_all('img'):
        imgs.append(img.get('src'))

    return [title, sub_topics, body_clean, links, imgs]


def parse_html_and_combine(partitioned_input: Dict[str, Callable[[], Any]], params: Dict) -> pd.DataFrame:
    """
    parse information from a array of html documents and bundle them together in a csv.

    Args:
        partitioned_input: A dictionary with partition ids (file path) as keys and load functions as values.

    Returns:
        Pandas DataFrame.
    """

    results = []

    for partition_key, partition_load_func in sorted(partitioned_input.items()):

        print(f'parsing file: {partition_key}')

        # parse doc
        data = parse_html(partition_load_func())

        # append filename to beginning of list
        filename = partition_key # + 'html'
        data.insert(0, filename)

        # append to list of results
        results.append(data)

    # convert into DataFrame
    df = pd.DataFrame(results)
    df.columns = ['filename', 'title', 'sub_topics', 'body', 'links', 'imgs']
    
    return df