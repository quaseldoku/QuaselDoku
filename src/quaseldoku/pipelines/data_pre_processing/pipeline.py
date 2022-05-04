"""
This is a boilerplate pipeline 'data_pre_processing'
generated using Kedro 0.18.0
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import filter_doku, parse_html_and_combine


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
            node(
                func=filter_doku,
                inputs=["ecu_test_doku", "params:preprocessing"],
                outputs="ecu_test_doku_flat_only_html",
                name="filter_and_flatten_doku_node",
            ),
            node(
                func=parse_html_and_combine,
                inputs=["ecu_test_doku_flat_only_html", "params:preprocessing"],
                outputs="ecu_test_doku_parsed",
                name="parse_html_doku_to_csv"
            )
    ])
