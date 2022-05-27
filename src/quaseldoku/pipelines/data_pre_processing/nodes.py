"""
This is a boilerplate pipeline 'data_pre_processing'
generated using Kedro 0.18.0
"""

import pandas as pd
import re
import datasets
import hashlib
import base64

from whoosh.index import create_in
from whoosh.analysis import StemFilter, RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.fields import Schema, TEXT, ID

from pathlib import Path
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

        if exclude:
            continue

        # suffix gets lost when loading files using suffix as filter, so needs to be appended back here
        filename = partition_key.replace('/', '_') + 'html'
        # append new filename with load function to results dictionary
        result[filename] = partition_load_func

    return result


def generate_hash_from_text(text: str) -> str:
    """
    generate a alpha-numerical hash from a given text str. Uses md5 algorithm.
    Args:
        text: string to be hashed
    Return:
        hash of fixed length of text input (hash usually ends with '==' which are cut off here)
    """
    return base64.b64encode(hashlib.md5(text.encode('utf-8')).digest()).decode()[:-2]


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
        filename = partition_key  # + 'html'
        data.insert(0, filename)

        # append to list of results
        results.append(data)

    # convert into DataFrame
    df = pd.DataFrame(results)
    df.columns = ['filename', 'title', 'sub_topics', 'body', 'links', 'imgs']

    return df


def download_germanquad(path_to_load_script: str) -> pd.DataFrame:
    """
    loads the germanQuAD Dataset via huggingface 'datasets' module, 
    extracts only the test split and converts it to pandas DataFrame.
    Also adds a column 'Hash' where context is hashed, which is needed when creating a search index on this dataset.

    Args:
        path_to_load_script: path where the germanquad load script is stored which is needed for downloading the dataset

    Returns:
        germanSQuAD test set as pandas DataFrame
    """
    germansquad = datasets.load_dataset(path_to_load_script)
    germansquad_df = germansquad['test'].to_pandas()
    germansquad_df['hash'] = germansquad_df['context'].apply(lambda x: generate_hash_from_text(x))
    return germansquad_df


def create_document_index(documents: pd.DataFrame, stopwords: list, indexdir_path: str):
    '''
    Creates a searchable index for a bunch of documents that need too be rows of a pandas DataFrame. 
    The DataFrame also needs at least on column containing a document identifier (hash) called 'Hash',
    as well as a column named 'Body' containing the text body of the document.
    It uses the library woosh to do so that provides handy functions for formatting the documents text bodies before indexing them;
    namely removing punctuation, stop words, lower case conversion as well as stemming.
    It saves the index back to disk at a given location. This location needs to be referenced later when querying the index.
    The content itself is not stored only the id and the indexed text body.
    So in order to retrieve the original document after a query, the document must be linked by its hash. 

    Args:
        documents: pd.DataFrame containing text documents
        indexdir_path: location where index will be saved to
        stoplist: DataFrame with column 'words' containing words which will be removed when parsing a text body
    '''

    # parse stoplist from DataFrame to list  
    stoplist = stopwords['words'].values.tolist()  

    # define analyzer
    custom_analyzer = RegexTokenizer() | LowercaseFilter() | StopFilter(stoplist=stoplist) | StemFilter(lang="de")

    # create Schema for indexing documents
    schema = Schema(
        id=ID(stored=True),
        content=TEXT(analyzer=custom_analyzer), # indexed content
    )

    # create dir for storing indexing results
    Path(indexdir_path).mkdir(parents=True, exist_ok=True)
    
    # Creating a index writer to add document as per schema
    ix = create_in(indexdir_path, schema)
    writer = ix.writer()

    # add every document to index
    for _, row in documents.iterrows():
        id = row['hash']
        text = row['context']
        writer.add_document(id=id, content=text)

    # save index back to file
    writer.commit()
