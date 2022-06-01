from typing import Dict
from sentence_transformers import SentenceTransformer, util
from ast import literal_eval

import pandas as pd
import numpy as np
import pickle
import torch


def load_model_from_hub(model: str):
    '''
    download specific model from hugginface hub if ran the first time,
    otherwise loads model from cache.
    '''
    return SentenceTransformer(model)


def load_model_from_disk(path: str):
    '''
    loads saved model.pkl. Useful if model is loaded outside kedro e.g. in the webapp.
    '''
    
    with open(path, "rb") as model_pkl:
        model = pickle.load(model_pkl)
    return model


def create_query_embedding(query: str, model: SentenceTransformer) -> np.array:

    return model.encode(query)


def create_document_embeddings(docs: pd.DataFrame, model: SentenceTransformer, embed: str = 'paragraph') -> pd.DataFrame:

    # embed either single sentences or a paragraph at once
    context_with_hash = docs[['Hash', 'Body']]
    if embed == 'sentence':
        sentences_with_hash = []
        for _, row in context_with_hash.iterrows():
            for sentence in row['Body'].split('. '):
                sentences_with_hash.append([row['HashDict'], sentence])

        sentences_with_hash = pd.DataFrame(sentences_with_hash)
        sentences_with_hash.columns = ['Hash', 'Body']
        sentences = sentences_with_hash['Body'].values
        embeddings = model.encode(sentences)
        sentences_with_hash['Embedding'] = embeddings.tolist()
        return sentences_with_hash
        
    elif embed == 'paragraph':
        bodies = context_with_hash['Body'].values
        embeddings = model.encode(bodies)
        context_with_hash['Embedding'] = embeddings.tolist()
        return context_with_hash


def query(query: str, context_with_embedding: pd.DataFrame, model: SentenceTransformer, query_type: str ='raw', score='cos_sim') -> pd.DataFrame:

    embeddings = context_with_embedding['Embedding'].apply(literal_eval)
    if query_type == 'raw':
        query_embedding = create_query_embedding(query, model)
    elif query_type == 'embedding':
        query_embedding = query
    if score == 'cos_sim':
        scored_embeddings = context_with_embedding.copy()
        scored_embeddings['Score'] = util.cos_sim(query_embedding, embeddings).tolist()[0]

    #Sort by decreasing score
    return scored_embeddings.sort_values(['Score'], ascending=False)


def semantic_search(queries: list, context_with_embedding: pd.DataFrame, model: SentenceTransformer) -> list:

    print("embedding the queries ...")
    queries_embeddings = model.encode(queries)

    print("converting context embeddings to tensors ...")
    context_embeddings = torch.FloatTensor(context_with_embedding['Embedding'].apply(literal_eval))

    print("running semantic search for every query on context embeddings ...")
    res = util.semantic_search(queries_embeddings, context_embeddings, top_k=100, score_function=util.cos_sim)
    return res