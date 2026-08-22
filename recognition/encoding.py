import numpy as np


def serialize_embedding(embedding):
    return embedding.astype(np.float32).tobytes()


def deserialize_embedding(data):
    return np.frombuffer(data, dtype=np.float32).reshape(1, -1)
