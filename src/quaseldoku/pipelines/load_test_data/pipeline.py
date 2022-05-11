"""
This is a boilerplate pipeline 'load_test_data'
generated using Kedro 0.18.0
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import download_germanquad


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=download_germanquad,
            inputs=["params:germanquad_load_script"],
            outputs="germanquad_validation",
            name="download_germanquad",
        ),
    ])
