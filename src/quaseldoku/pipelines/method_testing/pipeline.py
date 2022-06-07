"""
This is a boilerplate pipeline 'method_testing'
generated using Kedro 0.18.0
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import use_keyword_search, prepare_questions, calc_top_n_score, log_metrics, use_semantic_search


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        # GERMANQUAD
        # keyword-search
        node(
            func=prepare_questions,
            inputs="germanquad_validation",
            outputs="germanquad_questions",
            name="prepare_germanquad_questions"
        ),
        node(
            func=use_keyword_search,
            inputs=["germanquad_questions", "params:germanquad_search_index"],
            outputs="germanquad_keyword_search_results",
            name="keyword_search_germanquad"
        ),
        node(
            func=calc_top_n_score,
            inputs=["germanquad_keyword_search_results", "germanquad_validation"],
            outputs="germanquad_accuracies",
            name="top_n_germanquad"
        ),
        node(
            func=use_semantic_search,
            inputs=["germanquad_questions", "germanquad_paragraph_embeddings", "sentence_transformer_model"],
            outputs="germanquad_semantic_results",
            name="semantic_search_germanquad"
        ),
        node(
            func=calc_top_n_score,
            inputs=["germanquad_semantic_results", "germanquad_validation"],
            outputs="germanquad_semantic_accuracies",
            name="semantic_accuracy_germanquad"
        ),
        # ECU TEST
        # keyword-search
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
            outputs="ecu_accuracies",
            name="top_n_ecu"
        ),
        # semantic search
        node(
            func=use_semantic_search,
            inputs=["ecu_test_doku_questions", "ecu_test_paragraph_embeddings", "sentence_transformer_model"],
            outputs="ecu_semantic_results",
            name="semantic_search_ecu"
        ),
        node(
            func=calc_top_n_score,
            inputs=["ecu_semantic_results", "ecu_test_doku_validation"],
            outputs="ecu_semantic_accuracies",
            name="semantic_accuracy_ecu"
        ),
        # LOGGING OF METRICS
        node(
            func=log_metrics,
            inputs=["ecu_accuracies", "germanquad_accuracies", "ecu_semantic_accuracies", "germanquad_semantic_accuracies"],
            outputs="test_results",
            name="log_metrics"
        )
    ])
