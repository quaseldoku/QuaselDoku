"""
This is a boilerplate pipeline 'method_testing'
generated using Kedro 0.18.0
"""

from typing import Dict
import numpy as np
import pandas as pd
from tqdm import tqdm
from quaseldoku.qa_methods import keyword_search, word_embeddings, bert
from sentence_transformers import SentenceTransformer


def prepare_questions(dataset: pd.DataFrame) -> list:
    '''
    Extracts only the questions from a test set containing question, context and answers

    Args: 
        dataset: the test dataset containing the question

    Returns
        DataFrame containing questions only
    '''
    return dataset['Question'].to_list()


def use_keyword_search(
        queries: list, index_dir: str, search_by: str = 'any') -> pd.DataFrame:
    '''
    Apply keyword search for all queries provided on documents using the previously created search index of that specific document base. 

    Args:
        queries: list of questions
        stopwords: need to be provided in order to instantiate the keyword analyzer 
        index_dir: path where search index for document base to query is stored
        search_by: 'all' if all keywords of query must be found inside paragraph, 'any' if only one of the keywords need to be found

    Returns
        DataFrame containing list of hashes of best n documents for every query (list of hashes for on query per row),
        also returns the original question as well es the parsed query (parsed by analyzer).
    '''

    res = []

    # apply keyword search for very query
    print(f'applying keyword search on {len(queries)} questions ...')
    for question in tqdm(queries):
        res.append(keyword_search.query(question, index_dir, search_by))

    # convert to DataFrame and return
    results_df = pd.DataFrame(res)
    results_df.columns = ['Results', 'Question', 'Query']
    return results_df


def use_semantic_search(queries: list, embeddings: pd.DataFrame, model: SentenceTransformer) -> pd.DataFrame:

    print(f'applying semantic search on {len(queries)} questions ...')
    search_results = word_embeddings.semantic_search(queries, embeddings, model)
    
    # re-assemble questions with answers (hashes)
    results = []
    for question, res in zip(queries, search_results):
        resulting_hashes = []
        for context in res:
            idx = context['corpus_id']
            # get hash by index
            resulting_hashes.append(embeddings.iloc[idx]['Hash'])
        results.append([resulting_hashes, question])

    # convert to DataFrame and return
    results_df = pd.DataFrame(results)
    results_df.columns = ['Results', 'Question']
    return results_df


def use_bert(pre_selection_results: pd.DataFrame, dataset: pd.DataFrame, top_k_pre_selection: int = 20, top_k_bert: int = 3):

    print("init pipeline")
    pipeline = bert.init_model_and_tokenizer() 

    final_bert_res = []

    # basically re sort answers from pre selection method (keyword search) with BERT
    for idx, row in pre_selection_results.iterrows():
        print(f'processing row {idx+1} of {len(pre_selection_results)}')
        question = row['Question']
        
        # take first k documents from preselection and their hashes
        result_hashes = row['Results'][:top_k_pre_selection]
        bert_res = []
        
        # for every document get k best answers from bert
        for _hash in result_hashes:
            # get context by hash from original dataset
            context = dataset.loc[dataset['Hash'] == _hash]['Body'].values[0]            
            
            # query bert
            query_res = bert.query(question, context, pipeline, top_k_bert)
            
            # append hash of context to every bert answer
            for br in query_res:
                bert_res.append({'Hash': _hash, **br})

        # sort answers by bert score
        bert_res = sorted(bert_res, key=lambda x: x['score'], reverse=True)

        # append all answers to list for this question resulting in k * k answers
        final_bert_res.append([[res['Hash'] for res in bert_res], question])

    results_df = pd.DataFrame(final_bert_res)
    results_df.columns = ['Results', 'Question']
    return results_df


def calc_top_n_score(results: pd.DataFrame, dataset: pd.DataFrame) -> Dict:

    # calc top n score for following n's
    # ns = [100, 50, 20, 10, 5, 1] 
    max_n = len(dataset)
    ns = np.linspace(1, max_n, num=max_n, dtype=np.uint)

    # init accuracy scores
    accuracies = {n: 0 for n in ns}

    # get question
    for _, row in results.iterrows():
        question = row['Question']
        res = row['Results']
        if len(res) < 1:
            continue

        # get context to question from documents csv
        context_hash = dataset.loc[dataset['Question']==question]['Hash'].to_list()[0]

        # check wether hash of context is within n first results
        for n in ns:
            first_n_res = res[:n]
            if context_hash in first_n_res:
                accuracies[n] += 1

    # calc accuracy for every n
    for n in accuracies.keys():
        accuracies[n] = accuracies[n] / len(results)

    print(accuracies)

    return accuracies


def log_bert(top_n_bert: Dict) -> pd.DataFrame:

    # round values
    for n in top_n_bert.keys():
        top_n_bert[n] = round(top_n_bert[n], 3)

    # convert to DataFrame
    df = pd.DataFrame([top_n_bert])
    return df


def log_metrics(top_n_ecu: Dict, top_n_germanquad: Dict, top_n_ecu_semantic: Dict, top_n_germanquad_semantic) -> pd.DataFrame:

    # round values
    for metric in [top_n_ecu, top_n_germanquad, top_n_ecu_semantic, top_n_germanquad_semantic]:
        for n in metric.keys():
            metric[n] = round(metric[n], 3)

    # append name of dataset
    top_n_ecu['dataset'] = 'keyword:ecu_test_doku'
    top_n_germanquad['dataset'] = 'keyword:germanquad'    
    top_n_ecu_semantic['dataset'] = 'semantic:ecu_test_doku'
    top_n_germanquad_semantic['dataset'] = 'semantic:germanquad'

    # convert to DataFrame and reverse column order
    df = pd.DataFrame([top_n_ecu, top_n_germanquad, top_n_ecu_semantic, top_n_germanquad_semantic])
    return df[df.columns[::-1]]

