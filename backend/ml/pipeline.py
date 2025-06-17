import argparse
import json
import os
import re
from typing import List

import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
import joblib

DATA_DIR = os.path.dirname(__file__)
INDEX_PATH = os.path.join(DATA_DIR, "index.faiss")
VECT_PATH = os.path.join(DATA_DIR, "vectorizer.joblib")
DOCS_PATH = os.path.join(DATA_DIR, "docs.json")


def scrape(urls: List[str]) -> List[str]:
    texts = []
    for url in urls:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ")
        text = re.sub(r"\s+", " ", text)
        texts.append(text)
    return texts


def build_index(texts: List[str]):
    vect = TfidfVectorizer(stop_words="english")
    mat = vect.fit_transform(texts)
    index = faiss.IndexFlatL2(mat.shape[1])
    index.add(mat.toarray().astype("float32"))
    faiss.write_index(index, INDEX_PATH)
    joblib.dump(vect, VECT_PATH)
    with open(DOCS_PATH, "w") as f:
        json.dump(texts, f)


def main():
    parser = argparse.ArgumentParser(description="ML pipeline utilities")
    sub = parser.add_subparsers(dest="cmd")

    sc = sub.add_parser("scrape")
    sc.add_argument("url_file")
    sc.add_argument("output")

    ic = sub.add_parser("index")
    ic.add_argument("input")

    args = parser.parse_args()

    if args.cmd == "scrape":
        with open(args.url_file) as f:
            urls = [line.strip() for line in f if line.strip()]
        texts = scrape(urls)
        with open(args.output, "w") as f:
            json.dump(texts, f)

    elif args.cmd == "index":
        with open(args.input) as f:
            texts = json.load(f)
        build_index(texts)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
