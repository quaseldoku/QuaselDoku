"""
This is a boilerplate pipeline 'data_pre_processing'
generated using Kedro 0.18.0
"""

import pandas as pd
import re
import csv
import itertools

from typing import Any, Callable, Dict
from bs4 import BeautifulSoup
from requests import head


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

# New: seperate function to collect body, headlines, ...
def get_body(soup_elem,liste_headlines,name):
    ordnen = []
    for h in liste_headlines:
        block = soup_elem.find("div",{"id":h.lower()})
        childTag = block.find(("p","ul","table"),recursive = False)
        if childTag:
            elems = (block.findChildren(("p","ul","table"),recursive =False))
            for elem in elems:
                text = re.sub(" \n ", " ", elem.get_text().strip(), flags=re.M)
                text = re.sub("\n ", " ", text.strip(), flags=re.M)
                text = re.sub(" \n", " ", text.strip(), flags=re.M)
                text =re.sub("\n", " ", text.strip(), flags=re.M)
                ordnen.append((text, h, name, hash(h+name)))
    text_frame = pd.DataFrame(ordnen, columns = ["Text","Head","Link","Hash"])
    text_merge = text_frame.groupby(['Head',"Link","Hash"],sort=False)['Text'].apply(list)
    
    final = text_merge.reset_index().values.tolist()
    return final

def get_paraName(soup_elem, headline):
    all_unter = []
    for unterkap in soup_elem.find_all(headline):
        sauber = re.sub('\uf0c1','', unterkap.get_text())
        string = sauber.replace("("," ").replace(")","")
        string = string.replace("„"," ").replace("“","")
        sauber = string.replace("?","")
        sauber = sauber.replace("_"," ")
        sauber = re.sub('\W+',' ',sauber)
        sauber = re.sub('ü','u',sauber)
        sauber = re.sub('ä','a',sauber)
        sauber = re.sub('ö','o',sauber)
        sauber = re.sub('Ü','U',sauber)
        sauber = re.sub('Ä','A',sauber)
        sauber = re.sub('Ö','O',sauber)
        sauber = re.sub('ß','sz',sauber)
        sauber = re.sub('  ',' ',sauber)
        sauber = sauber.replace("ECU TEST","Produktname")

        # some headlines are to inconsistent to be changes by ordinary filters
        # therefore they get cleaned here
        sauber = sauber.replace("Job einreihen ", "job-einreihen-tsanalysisjob")
        sauber = sauber.replace("Traceschrittergebnis ubernehmen ", "traceschrittergebnis-ubernehmen-tstracestepresult")
        sauber = sauber.replace("Analyse anfordern ", "analyse-anfordern-tsrequestanalysis")
        
        # irregular naming of a div block
        sauber = sauber.replace("Statusleiste", "id1")
        sauber= sauber.replace("cTestBed","id1")
        sauber =sauber.replace("IDN","labcar-pincontrol-failuresim-fiu-idn")
        # remove empty div block
        sauber = sauber.replace('Produktname drive','')
        sauber = sauber.replace("Nachtragliche Ausfuhrung von Analyse-Jobs","")
        sauber = sauber.replace("Mehr zur Entstehung von Analyse-Jobs","")
        # remove these two as they lead to tables or nothing _build/Tools/Software_Schnittstellen/...
        sauber = sauber.replace("Eigenschaften ","")
        sauber = sauber.replace("Jobs ","")

        sauber = re.sub(' ','-', sauber)

        sauber = sauber.replace("Port-IMAGE-Appium-","")
        sauber = sauber.replace("Dokumentation-der-Analyse-im-Report","dokumentation-der-analyse-jobs-im-report")
        sauber = sauber.replace("-Structure-With-Time","structure-with-time")
        sauber = sauber.replace("Voraussetzungen-zur-Verwendung-von-MATLAB-mit-Produktname","voraussetzungen-zur-verwendung-von-matlab-mit-ecu-test")
        
        all_unter.append(sauber)
    
    return all_unter

# Changes: 
#       - h1 and h2 headlines now get their own row
#       - body is a List of String elements corresponding to html-Elements
def parse_html(doc: str,key) -> list:
    # TODO : DOKU

    # parse html
    parsed = BeautifulSoup(doc, 'html.parser')
    
    # get title
    name=key   
    all_data = []
    sub_top = get_paraName(parsed, ["h2","h3"])
    
    if name.find('_build_Tools_Software_Schnittstellen_')!=-1:
        
        if sub_top != None:
            
            h2 = get_body(parsed, sub_top, name)
            all_data.append(h2)
    else:
        head_top = get_paraName(parsed, "h1")
        
        if head_top !=None:
            h1 = get_body(parsed, head_top, name)
            all_data.append(h1)
        if sub_top != None:
            h2 = get_body(parsed, sub_top, name)
            all_data.append(h2)
    flat_list = list(itertools.chain(*all_data))
    # gather subtopics
    #sub_topics = []
    #for sub_topic in parsed.find_all('h2'):
    #    sub_topics.append(sub_topic.get_text())

    # gather main text body
    #body = parsed.get_text()

    # use regex to strip new line marker
    #body_clean = re.sub(r'\n\s*\n', r'\n\n', parsed.get_text().strip(), flags=re.M)

    # gather all links from document
    #links = []
    #for link in parsed.find_all('a'):
    #    links.append(link.get('href'))

    # # gather all paragraphs
    # ps = []
    # for text in parsed.find_all('p'):
    #     ps.append(text.get_text())

    # gather images
    #imgs = []
    #for img in parsed.find_all('img'):
    #    imgs.append(img.get('src'))

    return flat_list


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

        # append filename to beginning of list
        #filename = partition_key # + 'html'
        #data.insert(0, filename)

        # append to list of results
        results = [*results, *data]
    # convert into DataFrame
    df = pd.DataFrame(results,columns=["Title","Filename","Hash","Body"])
   
    return df