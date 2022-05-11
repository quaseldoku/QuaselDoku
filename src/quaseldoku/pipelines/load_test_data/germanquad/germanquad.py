# coding=utf-8
# Lint as: python3
"""GermanQuAD: A German-Language Question Answering Dataset."""

import json

import datasets


logger = datasets.logging.get_logger(__name__)


_CITATION = """
@misc{möller2021germanquad,
      title={GermanQuAD and GermanDPR: Improving Non-English Question Answering and Passage Retrieval}, 
      author={Timo Möller and Julian Risch and Malte Pietsch},
      year={2021},
      eprint={2104.12741},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
"""

_DESCRIPTION = """
In order to raise the bar for non-English QA, we are releasing a high-quality, human-labeled German QA dataset consisting of 13 722 questions, incl. a three-way annotated test set.
The creation of GermanQuAD is inspired by insights from existing datasets as well as our labeling experience from several industry projects. We combine the strengths of SQuAD, such as high out-of-domain performance, with self-sufficient questions that contain all relevant information for open-domain QA as in the NaturalQuestions dataset. Our training and test datasets do not overlap like other popular datasets and include complex questions that cannot be answered with a single entity or only a few words.
"""

_URL = "https://germanquad.s3.amazonaws.com/GermanQuAD.zip"


class GermanQuADConfig(datasets.BuilderConfig):
    """BuilderConfig for GermanQuAD."""

    def __init__(self, **kwargs):
        """BuilderConfig for GermanQuAD.

        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(GermanQuADConfig, self).__init__(**kwargs)


class GermanDPR(datasets.GeneratorBasedBuilder):
    """GermanQuAD: A German-Language Question Answering Dataset."""

    BUILDER_CONFIGS = [
        GermanQuADConfig(
            name="plain_text",
            version=datasets.Version("1.0.0", ""),
            description="Plain text",
        ),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "id": datasets.Value("int32"),
                    "context": datasets.Value("string"),
                    "question": datasets.Value("string"),
                    "answers": datasets.features.Sequence(
                        {
                            "text": datasets.Value("string"),                            
                            "answer_start": datasets.Value("int32"),
                        }
                    )
                }
            ),
            # No default supervised_keys (as we have to pass both question
            # and context as input).
            supervised_keys=None,
            homepage="https://deepset.ai/germanquad",
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        downloaded_files = dl_manager.download_and_extract(_URL)

        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepath": downloaded_files+"/GermanQuAD/GermanQuAD_train.json"}),
            datasets.SplitGenerator(name=datasets.Split.TEST, gen_kwargs={"filepath": downloaded_files+"/GermanQuAD/GermanQuAD_test.json"}),
        ]

    def _generate_examples(self, filepath):
        """This function returns the examples in the raw (text) form."""
        logger.info("generating examples from = %s", filepath)
        with open(filepath, encoding="utf-8") as f:
            germanquad = json.load(f)
            for article in germanquad["data"]:
                for paragraph in article["paragraphs"]:
                    context = paragraph["context"]
                    document_id = paragraph["document_id"]
                    for qa in paragraph["qas"]:
                        question = qa["question"]
                        id_ = qa["id"]
                        answers = [{"answer_start": answer["answer_start"], "text": answer["text"]} for answer in qa["answers"]]

                        # Features currently used are "context", "question", and "answers".
                        # Others are extracted here for the ease of future expansions.
                        yield id_, {
                            "context": context,
                            "question": question,
                            "id": id_,
                            "answers": answers,
                        }
                
