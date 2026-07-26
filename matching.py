import os

os.environ["HF_HUB_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer


model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def find_matches(skills, vacancies, top_n=10):
    descriptions = [v.description or "" for v in vacancies]

    vacancy_vectors = model.encode(descriptions)
    skills_vector = model.encode([skills])

    scores = model.similarity(skills_vector, vacancy_vectors)[0]
    pairs = list(zip(vacancies, scores))
    pairs.sort(key=lambda pair: float(pair[1]), reverse=True)
    return pairs[:top_n]
