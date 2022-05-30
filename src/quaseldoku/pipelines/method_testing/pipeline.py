"""
This is a boilerplate pipeline 'method_testing'
generated using Kedro 0.18.0
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import use_keyword_search, prepare_questions, calc_top_n_score, log_metrics


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=use_keyword_search,
            inputs=["germanquad_questions", "params:germanquad_search_index"],
            outputs="germanquad_keyword_search_results",
            name="keyword_search_germanquad"
        ),
        node(
            func=prepare_questions,
            inputs="germanquad_validation",
            outputs="germanquad_questions",
            name="prepare_germanquad_questions"
        ),
        node(
            func=calc_top_n_score,
            inputs=["germanquad_keyword_search_results", "germanquad_validation"],
            outputs="germanquad_accuaries",
            name="top_n_germanquad"
        ),
        node(
            func=prepare_questions,
            inputs="ecu_test_doku_validation",
            outputs="ecu_test_doku_questions",
            name="prepare_ecu_questions"
        ),
        node(
            func=use_keyword_search,
            inputs=["ecu_test_doku_questions", "params:doku_search_index"],
            outputs="ecu_keyword_search_results",
            name="keyword_search_ecu"
        ),
        node(
            func=calc_top_n_score,
            inputs=["ecu_keyword_search_results", "ecu_test_doku_validation"],
            outputs="ecu_accuaries",
            name="top_n_ecu"
        ),
        node(
            func=log_metrics,
            inputs=["ecu_accuaries", "germanquad_accuaries"],
            outputs="test_results",
            name="log_metrics"
        )
    ])
