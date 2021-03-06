"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline
from quaseldoku.pipelines import data_pre_processing, method_testing

def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """

    data_pre_processing_pipeline = data_pre_processing.create_pipeline()
    method_testing_pipeline = method_testing.create_pipeline()

    return {
        "__default__": data_pre_processing_pipeline,
        "dp": data_pre_processing_pipeline,
        "validation": method_testing_pipeline
    }
