"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline, pipeline
from quaseldoku.pipelines import data_pre_processing #, load_test_data


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """

    data_pre_processing_pipeline = data_pre_processing.create_pipeline()

    return {
         "__default__": data_pre_processing_pipeline,
        "dp": data_pre_processing_pipeline,
        #"test_data": load_test_data_pipeline 
    }
