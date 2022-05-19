"""
This is a boilerplate pipeline 'data_pre_processing'
generated using Kedro 0.18.0
"""

from unittest import skip
import pandas as pd
import re
import itertools
import hashlib
import base64

from typing import Any, Callable, Dict
from bs4 import BeautifulSoup


def filter_doku(partitioned_input: Dict[str, Callable[[], Any]], params: Dict) -> Dict[str, Callable[[], Any]]:
    """
    flatten input where html files can occur on multiple levels, as well as filter out files that match certain string.
    Return new Dictionary with filenames and load functions from which a PartioniedDataset can be created and persisted.
    Since output is flattened the individual paths to files within doku file structure will get lost, 
    there encode '/' as '_' to be able to re assamble correct path later.

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

    all_unter = []
    for unterkap in soup_elem.find_all(headline):
        sauber = re.sub('\uf0c1', '', unterkap.get_text())
        string = sauber.replace("(", " ").replace(")", "")
        string = string.replace("„", " ").replace("“", "")
        sauber = string.replace("?", "")
        sauber = sauber.replace("_", " ")
        sauber = re.sub('\W+', ' ', sauber)
        sauber = re.sub('ü', 'u', sauber)
        sauber = re.sub('ä', 'a', sauber)
        sauber = re.sub('ö', 'o', sauber)
        sauber = re.sub('Ü', 'U', sauber)
        sauber = re.sub('Ä', 'A', sauber)
        sauber = re.sub('Ö', 'O', sauber)
        sauber = re.sub('ß', 'sz', sauber)
        sauber = re.sub('  ', ' ', sauber)
        sauber = sauber.replace("ECU TEST", "Produktname")

        # some headlines are too inconsistent to be changes by ordinary filters
        # therefore they get cleaned here
        sauber = sauber.replace("Job einreihen ", "job-einreihen-tsanalysisjob")
        sauber = sauber.replace("Traceschrittergebnis ubernehmen ",
                                "traceschrittergebnis-ubernehmen-tstracestepresult")
        sauber = sauber.replace("Analyse anfordern ",
                                "analyse-anfordern-tsrequestanalysis")

        # irregular naming of a div block
        sauber = sauber.replace("Statusleiste", "id1")
        sauber = sauber.replace("cTestBed", "id1")
        sauber = sauber.replace("IDN", "labcar-pincontrol-failuresim-fiu-idn")

        # remove empty div block
        sauber = sauber.replace('Produktname drive', '')
        sauber = sauber.replace("Nachtragliche Ausfuhrung von Analyse-Jobs", "")
        sauber = sauber.replace("Mehr zur Entstehung von Analyse-Jobs", "")

        # remove these two as they lead to tables or nothing _build/Tools/Software_Schnittstellen/...
        sauber = sauber.replace("Eigenschaften ", "")
        sauber = sauber.replace("Jobs ", "")

        sauber = re.sub(' ', '-', sauber)

        sauber = sauber.replace("Port-IMAGE-Appium-", "")
        sauber = sauber.replace("Dokumentation-der-Analyse-im-Report",
                                "dokumentation-der-analyse-jobs-im-report")
        sauber = sauber.replace("-Structure-With-Time", "structure-with-time")
        sauber = sauber.replace("Voraussetzungen-zur-Verwendung-von-MATLAB-mit-Produktname",
                                "voraussetzungen-zur-verwendung-von-matlab-mit-ecu-test")

        all_unter.append(sauber)

    return all_unter


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

        if child_tags != None:

            for child in (block.findChildren(("p", "ul", "table"), recursive=False)):

                text = re.sub(" \n ", " ", child.get_text().strip(), flags=re.M)
                text = re.sub("\n ", " ", text.strip(), flags=re.M)
                text = re.sub(" \n", " ", text.strip(), flags=re.M)
                text = re.sub("\n", " ", text.strip(), flags=re.M)

                text_elements.append(text)

        if len(text_elements) > 0:
            # concat all text elements to generate hash
            _text_concat = " ".join(text_elements)
            signature = generate_hash_from_text(_text_concat)

            # re assemble filepath within doku folder structure
            file_path = filename.replace('_', '/')
        
            paragraphs.append([signature, h, file_path, text_elements])

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

    if name.find('_build_Tools_Software_Schnittstellen_') != -1:
        skip
    else:
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

    for partition_key, partition_load_func in sorted(partitioned_input.items()):

        print(f'parsing file: {partition_key}')

        # parse doc
        data = parse_html(partition_load_func(), partition_key)

        # append to list of results
        results = [*results, *data]

    # convert to DataFrame
    df = pd.DataFrame(results, columns=["Hash", "Title", "Filename", "Body"])

    return df
