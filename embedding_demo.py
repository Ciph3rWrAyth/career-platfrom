from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

phrases = [
    "ищу pyhton разработчика",
    "нужен бэкендер со знанием FastAPI",
    "требуется бариста в кофейне",
]

vectors = model.encode(phrases)
print("Размер", vectors.shape)

similarity = model.similarity(vectors, vectors)
print(similarity)
