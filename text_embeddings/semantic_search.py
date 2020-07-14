print("importing sentence_transformers")
from sentence_transformers import SentenceTransformer
print("importing gensim")
from gensim.models import KeyedVectors
from gensim.test.utils import datapath

print("loading model")
model = SentenceTransformer("bert-base-nli-cls-token")

print("loading embeddings")
software_embeddings = KeyedVectors.load_word2vec_format("software_wordvec.txt", binary=False)

while True:
    query = input("What is your query?: ")
    embedding = model.encode([query])[0]
        print(software_embeddings.similar_by_vector(embedding, topn=10))