import argparse
import json
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
import os

from elasticsearch import Elasticsearch
from tqdm import tqdm

from nltk import sent_tokenize
import unidecode

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname).1s %(asctime)s [ %(message)s ]",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("search_index")

load_dotenv()
ELASTIC_CLOUD_ID = os.getenv('ELASTIC_CLOUD_ID')
ELASTIC_PASSWORD = os.getenv('ELASTIC_CLOUD_PASSWORD')
INDEX_NAME = 'sampled_redpajama'

def clean_text(text):
    return unidecode.unidecode(text)


def search_index(es, query, nb_documents, index_name=None):
    try:
        results = es.search(
            index=index_name,
            size=nb_documents,
            body={"query": {"bool": {"must": {"match": {"text": query}}}}} 
        )["hits"]["hits"]
        return results
    except Exception as e:
        print(f"Elasticsearch query failed: {e}")
        return []  # Return an empty list on error


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--output_dir", type=str, default=None, help="Output directory")
    parser.add_argument("--input_file", type=str, default=None, help="input directory")
    parser.add_argument("--nb_documents", type=int, default=100, help="Number of retrieved documents")

    parser.add_argument("--index_name", type=str, default=INDEX_NAME, help="Name of your Elasticsearch index")
    parser.add_argument("--subset", type=int, default=100, help="size of example subset to run search on")

    args = parser.parse_args()
    es = Elasticsearch(cloud_id=ELASTIC_CLOUD_ID, basic_auth=("elastic", ELASTIC_PASSWORD))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    name = Path(args.input_file).stem
    output_path = output_dir / f"{name}_results.json"

    with open(args.input_file, "r") as f:
        data = json.load(f)[:args.subset]

    all_results = []

    for i, cur_data in enumerate(tqdm(data, desc="iterating through data")):
        generation = cur_data["text"]
        generation = clean_text(generation)
        sentences = sent_tokenize(generation)
        doc_details = []

        for segment in tqdm(sentences, desc="reading sentences", leave=False):
            begin = time.perf_counter()
            try:
                output = search_index(es, segment, args.nb_documents, args.index_name)
                top_documents = output
                doc_details.append({"query": segment, "top_docs": top_documents, "retrieval_runtime": begin - time.perf_counter()})

            except Exception as e:
                print(f"Elastic Search API failed: {e}", flush=True)
                continue

        cur_data["retrieval_details"] = doc_details
        all_results.append(cur_data) # Append the updated cur_data

    with open(output_path, "w") as out:
        json.dump(all_results, out, indent=4) # Save all results at once

    print(f"Results saved to: {output_path}", flush=True) # Confirm save location

if __name__ == "__main__":
    main()