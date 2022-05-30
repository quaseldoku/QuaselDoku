"""
This is a boilerplate pipeline 'data_pre_processing'
generated using Kedro 0.18.0
"""

from gettext import find
from unittest import skip
import pandas as pd
import re
import datasets
import itertools
import hashlib
import base64
import os

from typing import Any, Callable, Dict
from bs4 import BeautifulSoup
from tqdm import tqdm
from quaseldoku.helper import find_project_root


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

    print("filtering out relevant html files from doku ...")
    for partition_key, partition_load_func in tqdm(sorted(partitioned_input.items())):
        
        exclude = False
        for string in params['exclude_docs']:
            
            if string in partition_key:
                
                exclude = True
                break

        if exclude:
            continue

        filename = partition_key.replace('/', ' ')
        filename += 'html'

        # append new filename with load function to results dictionary
        result[filename] = partition_load_func

    return result


def get_para_name(soup_elem: BeautifulSoup, headline: list) -> list:
    """
    get the names of all sections (with h-Element provided by headline) in html element.
    Clean the string and handle edge cases. 

    Args:
        soup_elem: parsed html document as BeautifulSoup object
        headlines: list of h-Elements to look for in document.

    Returns:
        list of cleaned strings describing the titles of the sections of the provided html document.
    """

    all_chap = []
    for head in soup_elem.find_all(headline):
        clean_text = re.sub('\uf0c1', '', head.get_text())
        clean_text = clean_text.replace("(", " ").replace(")", "")
        clean_text = clean_text.replace("„", " ").replace("“", "")
        clean_text = clean_text.replace("?", "")
        clean_text = clean_text.replace("_", " ")
        clean_text = re.sub('\W+', ' ', clean_text)
        clean_text = re.sub('ü', 'u', clean_text)
        clean_text = re.sub('ä', 'a', clean_text)
        clean_text = re.sub('ö', 'o', clean_text)
        clean_text = re.sub('Ü', 'U', clean_text)
        clean_text = re.sub('Ä', 'A', clean_text)
        clean_text = re.sub('Ö', 'O', clean_text)
        clean_text = re.sub('ß', 'sz', clean_text)
        clean_text = re.sub('  ', ' ', clean_text)
        clean_text = clean_text.replace("ECU TEST", "Produktname")

        # some headlines are too inconsistent to be changes by ordinary filters
        # therefore they get cleaned here
        clean_text = clean_text.replace("Job einreihen ", "job-einreihen-tsanalysisjob")
        clean_text = clean_text.replace("Traceschrittergebnis ubernehmen ",
                               "traceschrittergebnis-ubernehmen-tstracestepresult")
        clean_text = clean_text.replace("Analyse anfordern ",
                                "analyse-anfordern-tsrequestanalysis")

        # irregular naming of a div block
        clean_text = clean_text.replace("Statusleiste", "id1")
        clean_text = clean_text.replace("cTestBed", "id1")
        clean_text = clean_text.replace("IDN", "labcar-pincontrol-failuresim-fiu-idn")

        # remove empty div block
        clean_text = clean_text.replace('Produktname drive', '')

        clean_text = re.sub(' ', '-', clean_text)

        clean_text = clean_text.replace("Dokumentation-der-Analyse-im-Report",
                                "dokumentation-der-analyse-jobs-im-report")
        clean_text = clean_text.replace("-Structure-With-Time", "structure-with-time")

        all_chap.append(clean_text)

    return all_chap


def generate_hash_from_text(text: str) -> str:
    """
    generate a alpha-numerical hash from a given text str. Uses md5 algorithm.

    Args:
        text: string to be hashed

    Return:
        hash of fixed length of text input

    """
    return base64.b64encode(hashlib.md5(text.encode('utf-8')).digest()).decode()


def get_body(soup_elem: BeautifulSoup, list_headlines: list, filename: str) -> pd.DataFrame:
    """
    for a given list of headers find corresponding div blocks in parsed html document and 
    gather text of all child elements of div block (p, ul, table).

    Args:
        soup_elem: parsed html document as BeautifulSoup object
        list_headlines: list of h-Elements in html doc
        link: path of parent document

    Returns:
        list containing rows like [signature, title, link, text]
    """

    paragraphs = []

    for h in list_headlines:

        # find div element that belongs to this h-Element
        block = soup_elem.find("div", {"id": h.lower()})

        # find all child elements of this div block
        child_tags = block.find(("p", "ul", "table"), recursive=False)

        # gather all availabe text within this div block and concatenate
        text_elements = []

        # re assemble filepath within doku folder structure
        file_path = filename.replace(' ', '/')

        _text_concat = h+file_path
        signature = generate_hash_from_text(_text_concat)
        if child_tags != None:

            for child in (block.findChildren(("p", "ul", "table"), recursive=False)):               

                # for list-elemnts check for bullet points just consisting of a link
                if child.name == "ul":
                    list_elem = child.findChildren("li")
                    for elem in list_elem:
                        link_text = elem.findChildren("a")
                        
                        if len(link_text):
                            # if bullet point just contains link skip
                            if elem.get_text() == link_text[0].get_text():
                                list_text = ""
                            # else add bullet point to text
                            else:
                                list_text = re.sub(" \n ", " ", elem.get_text().strip(), flags=re.M)
                                list_text = re.sub("\n ", " ", list_text.strip(), flags=re.M)
                                list_text = re.sub(" \n", " ", list_text.strip(), flags=re.M)
                                list_text = re.sub("\n", " ", list_text.strip(), flags=re.M)
                                text_elements.append(list_text)
                    if len(text_elements) > 0:
                        text = text_elements
                        #_text_concat = " ".join(text)
                        #signature = generate_hash_from_text(_text_concat)
                        paragraphs.append([signature, h, file_path, text])
                else: 

                    text = re.sub(" \n ", " ", child.get_text().strip(), flags=re.M)
                    text = re.sub("\n ", " ", text.strip(), flags=re.M)
                    text = re.sub(" \n", " ", text.strip(), flags=re.M)
                    text = re.sub("\n", " ", text.strip(), flags=re.M)
                    if len(text) > 0:
                    # concat all text elements to generate hash
                        paragraphs.append([signature, h, file_path, text])

    return paragraphs


def parse_html(doc: str, key: str) -> list:
    """
    retrieve all relevant paragraphs from a given html document

    Args:
        doc: the html document as string
        key: the path of the html document as string

    Returns:
        list containing rows like [Title, Filename, Hash, Body]
    """

    # parse html
    parsed = BeautifulSoup(doc, 'html.parser')

    # get title
    name = key
    all_data = []
    sub_top = get_para_name(parsed, ["h2", "h3"])

    head_top = get_para_name(parsed, "h1")
    if head_top != None:
        h1 = get_body(parsed, head_top, name)
        all_data.append(h1)
    if sub_top != None:
        h2 = get_body(parsed, sub_top, name)
        all_data.append(h2)

    return list(itertools.chain(*all_data))


def parse_html_and_combine(partitioned_input: Dict[str, Callable[[], Any]], params: Dict) -> pd.DataFrame:
    """
    parse information from a array of html documents and bundle them together in a csv.

    Args:
        partitioned_input: A dictionary with partition ids (file path) as keys and load functions as values.

    Returns:
        Pandas DataFrame.
    """

    results = []

    print('parsing html files ...')
    for partition_key, partition_load_func in tqdm(sorted(partitioned_input.items())):

        # parse doc
        data = parse_html(partition_load_func(), partition_key)

        # append to list of results
        results = [*results, *data]

    # convert into DataFrame
    df = pd.DataFrame(results, columns=["Hash", "Title", "Filename", "Body"])
    
    return df


def download_germanquad(path_to_load_script: str) -> pd.DataFrame:
    """
    loads the germanQuAD Dataset via huggingface 'datasets' module, 
    extracts only the test split and converts it to pandas DataFrame.
    Also adds a column 'Hash' where context is hashed, which is needed when creating a search index on this dataset.
    Columns are renamed to math the convention used with ecu doku.

    Args:
        path_to_load_script: path where the germanquad load script is stored which is needed for downloading the dataset

    Returns:
        germanSQuAD test set as pandas DataFrame
    """

    # load and convert dataset
    path_to_load_script_abs = find_project_root(os.getcwd()) + '/' + path_to_load_script
    germansquad = datasets.load_dataset(path_to_load_script_abs)

    # convert to dict before converting to DataFrame (made parsing easier)
    germansquad_dict = germansquad['test'].to_dict()
    germansquad_df = pd.DataFrame(germansquad_dict)

    # parse answer from json to string and only take first answer
    germansquad_df['Answer'] = germansquad_df['answers'].apply(lambda x: x['text'][0])
    germansquad_df.drop(columns=['answers', 'id'], inplace=True)

    # rename and append columns
    germansquad_df.rename(columns = {'context':'Body', 'question':'Question'}, inplace = True)
    germansquad_df['Hash'] = germansquad_df['Body'].apply(lambda x: generate_hash_from_text(x))

    return germansquad_df


def blocks_to_paragraphs(load_block_elements: pd.DataFrame) -> pd.DataFrame:
    """
    loads the ecu_test_doku_parsed Dataset, 
    merges all elements with the same Hash, Title and Filename
    body elements get joined via ' '

    Args:
        load_block_elements: call the ecu_test_doku_parsed Dataset

    Returns:
        pandas DataFrame
    """
   
    block_elements = load_block_elements
    paragraphs = block_elements.groupby(['Hash','Title','Filename'],sort=False)['Body'].apply(' '.join).reset_index()

    return paragraphs
