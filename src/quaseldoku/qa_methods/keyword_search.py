from typing import Dict
from whoosh.index import open_dir
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemFilter, RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.qparser import QueryParser, OrGroup
from whoosh import scoring
from pathlib import Path
from quaseldoku.helper import find_project_root
import pandas as pd
import os

# list of german stopwords taken from sphinx documentation and used for filtering paragraphs during indexing as well as queries
stopwords = ["aber", "alle", "allem", "allen", "aller", "alles", "als", "also", "am", "an", "ander", "andere", "anderem", "anderen", "anderer", "anderes", "anderm", "andern", "anderr", "anders", "auch", "auf", "aus", "bei", "bin", "bis", "bist", "da", "damit", "dann", "das", "dasselbe", "dazu", "da\\u00df", "dein", "deine", "deinem", "deinen", "deiner", "deines", "dem", "demselben", "den", "denn", "denselben", "der", "derer", "derselbe", "derselben", "des", "desselben", "dessen", "dich", "die", "dies", "diese", "dieselbe", "dieselben", "diesem", "diesen", "dieser", "dieses", "dir", "doch", "dort", "du", "durch", "ein", "eine", "einem", "einen", "einer", "eines", "einig", "einige", "einigem", "einigen", "einiger", "einiges", "einmal", "er", "es", "etwas", "euch", "euer", "eure", "eurem", "euren", "eurer", "eures", "f\\u00fcr", "gegen", "gewesen", "hab", "habe", "haben", "hat", "hatte", "hatten", "hier", "hin", "hinter", "ich", "ihm", "ihn", "ihnen", "ihr", "ihre", "ihrem", "ihren", "ihrer", "ihres", "im", "in", "indem", "ins", "ist",
             "jede", "jedem", "jeden", "jeder", "jedes", "jene", "jenem", "jenen", "jener", "jenes", "jetzt", "kann", "kein", "keine", "keinem", "keinen", "keiner", "keines", "k\\u00f6nnen", "k\\u00f6nnte", "machen", "man", "manche", "manchem", "manchen", "mancher", "manches", "mein", "meine", "meinem", "meinen", "meiner", "meines", "mich", "mir", "mit", "muss", "musste", "nach", "nicht", "nichts", "noch", "nun", "nur", "ob", "oder", "ohne", "sehr", "sein", "seine", "seinem", "seinen", "seiner", "seines", "selbst", "sich", "sie", "sind", "so", "solche", "solchem", "solchen", "solcher", "solches", "soll", "sollte", "sondern", "sonst", "um", "und", "uns", "unse", "unsem", "unsen", "unser", "unses", "unter", "viel", "vom", "von", "vor", "war", "waren", "warst", "was", "weg", "weil", "weiter", "welche", "welchem", "welchen", "welcher", "welches", "wenn", "werde", "werden", "wie", "wieder", "will", "wir", "wird", "wirst", "wo", "wollen", "wollte", "w\\u00e4hrend", "w\\u00fcrde", "w\\u00fcrden", "zu", "zum", "zur", "zwar", "zwischen", "\\u00fcber"]


def get_analyzer():

    # prepare analyzer for query string (same that has been used when documents were indexed)
    return RegexTokenizer() | LowercaseFilter() | StopFilter(
        stoplist=stopwords) | StemFilter(lang="de")


def create_document_index(documents: pd.DataFrame, indexdir_path: str):
    '''
    Creates a searchable index for a bunch of documents that need too be rows of a pandas DataFrame. 
    The DataFrame also needs at least on column containing a document identifier (hash) called 'Hash',
    as well as a column named 'Body' containing the text body of the document.
    It uses the library woosh to do so that provides handy functions for formatting the documents text bodies before indexing them;
    namely removing punctuation, stop words, lower case conversion as well as stemming.
    It saves the index back to disk at a given location. This location needs to be referenced later when querying the index.

    Args:
        documents: pd.DataFrame containing text documents
        indexdir_path: location where index will be saved to
        stoplist: DataFrame with column 'words' containing words which will be removed when parsing a text body
    '''

    custom_analyzer = get_analyzer()

    # create Schema for indexing documents
    schema = Schema(
        id=ID(stored=True),
        content=TEXT(analyzer=custom_analyzer),  # indexed content
        body=TEXT(stored=True),  # indexed content
    )

    project_root = find_project_root(os.getcwd())
    indexdir_path_abs = project_root + '/' + indexdir_path
    print(f'document index will be strored to: {indexdir_path_abs}')
    Path(indexdir_path_abs).mkdir(parents=True, exist_ok=True)

    # Creating a index writer to add document as per schema
    ix = create_in(indexdir_path_abs, schema)
    writer = ix.writer()

    # only index same documents once (identified by hash)
    indexed_hashes = []

    # add every document to index
    for _, row in documents.iterrows():
        id = row['Hash']
        if id in indexed_hashes:
            continue
        indexed_hashes.append(id)
        content = row['Body']
        writer.add_document(id=id, content=content, body=content)

    # save index back to file
    writer.commit()


def query(query: str, index_dir: str, search_by: str = 'any', return_context: bool = False, verbose: bool = False) -> Dict:

    # open index directory containing index document base
    ix = open_dir(index_dir)

    # prepare query string by applying analyzer
    query_str = " ".join([token.text for token in get_analyzer()(query)])
    if verbose:
        print(f'the query is: "{query_str}"')

    # search in index and use Okapi BM25F for ranking results
    with ix.searcher(weighting=scoring.BM25F) as searcher:
        if search_by == 'all':
            _q = QueryParser("content", ix.schema).parse(query_str)
        elif search_by == 'any':
            _q = QueryParser("content", ix.schema,
                             group=OrGroup).parse(query_str)

        # only return best 100 results
        results = searcher.search(_q, limit=100)

        if len(results) > 0:
            if verbose:
                print(f'\nsearch yielded {len(results)} results in total')

            if not return_context:
                matching_docs = [r['id'] for r in results]
            # look up context by hash and return alongside hash if needed
            else:
                matching_docs = [[r['id'], r['body']] for r in results]
                
        else:
            if verbose:
                print('search yielded no hits')
            matching_docs = []


    return {'hits': matching_docs, 'query': query, 'parsed_query': query_str}
