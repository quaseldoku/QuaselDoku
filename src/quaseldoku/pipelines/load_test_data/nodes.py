"""
This is a boilerplate pipeline 'load_test_data'
generated using Kedro 0.18.0
"""

import datasets
import pandas as pd

# download germanquad dataset and save as arrow
def download_germanquad(path_to_load_script: str) -> pd.DataFrame:
    """
    loads the germanQuAD Dataset via huggingface 'datasets' module, 
    extracts only the test split and converts it to pandas DataFrame

    Returns:
        germanSQuAD test set as pandas DataFrame
    """
    germansquad = datasets.load_dataset(path_to_load_script)
    return germansquad['test'].to_pandas()
