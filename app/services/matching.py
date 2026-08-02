import os

os.environ["HF_HUB_OFFLINE"] = "1"

import numpy as np 
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

_vector_cache = {}



def _get_vacancy_vectors(vacancies):
    missing = [v for v in vacancies if v.id not in _vector_cache]
    if  missing:
        new_vectors = model.encode([v.description or "" for v in missing])
        for v, vec in zip(missing, new_vectors):
            _vector_cache[v.id] = vec
    return np.array([_vector_cache[v.id] for v in vacancies])


def find_matches(skills, vacancies, top_n=10):
    vacancy_vectors = _get_vacancy_vectors(vacancies)
    skills_vector = model.encode([skills])

    scores = model.similarity(skills_vector, vacancy_vectors)[0]
    pairs = list(zip(vacancies, scores))
    pairs.sort(key=lambda pair: float(pair[1]), reverse=True)
    return pairs[:top_n]


def clear_cache():
    _vector_cache.clear()