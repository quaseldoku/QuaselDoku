"""
This is a boilerplate pipeline 'data_pre_processing'
generated using Kedro 0.18.0
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import filter_doku, parse_html_and_combine, download_germanquad, blocks_to_paragraphs
from quaseldoku.qa_methods import keyword_search

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
            node(
                func=filter_doku,
                inputs=["ecu_test_doku", "params:preprocessing"],
                outputs="ecu_test_doku_flat_only_html",
                name="filter_and_flatten_doku",
            ),
            node(
                func=parse_html_and_combine,
                inputs=["ecu_test_doku_flat_only_html", "params:preprocessing"],
                outputs="ecu_test_doku_parsed",
                name="parse_html_doku_to_csv"
            ),
            node(
                func=blocks_to_paragraphs,
                inputs="ecu_test_doku_parsed",
                outputs="paragraph_elements",
                name="parse_paragraphs"
            ),
            node(
                func=download_germanquad,
                inputs="params:germanquad_load_script",
                outputs="germanquad_validation",
                name="download_germanquad"
            ),
            node(
                func=keyword_search.create_document_index,
                inputs=[
                    "paragraph_elements",
                    "params:doku_search_index"],
                outputs=None,
                name="index_ecu_test_doku"
            ),
            node(
                func=keyword_search.create_document_index,
                inputs=[
                    "germanquad_validation",
                    "params:germanquad_search_index"],
                outputs=None,
                name="index_germanquad"
            ),
    ])
