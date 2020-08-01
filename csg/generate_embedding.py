import numpy as np


class CSGEmbeddingGenerator:
    def __init__(self, input_csg: str, one_hot: bool = True):
        self.input_csg = input_csg.lower()
        self.one_hot = one_hot
        self.embedding = []

    def generate(self):
        keywords_embedding = get_keywords_one_hot() if self.one_hot else get_keywords_embedding()
        parts = self.input_csg.split(' ')
        parts = [p for p in parts if len(p) > 0]
        print(parts)
        for part in parts:
            try:
                emb = float(part)
                self.embedding.append(emb)
            except ValueError:
                emb = keywords_embedding[part]
                self.embedding.extend(emb)
        return self.embedding


def get_keywords_embedding():
    keywords = get_keywords()
    for i, keyword in enumerate(keywords):
        keywords[keyword].append(i + 1)
    return keywords


def get_keywords():
    keywords = {
        'cube': [],
        'cylinder': [],
        'sphere': [],
        'cone': [],
        'difference': [],
        'union': [],
        'intersection': [],
    }
    return keywords


def get_keywords_one_hot():
    keywords = get_keywords()
    for i, keyword in enumerate(keywords):
        embedding = np.zeros(len(keywords))
        embedding[i] = 1
        keywords[keyword].extend(embedding)
    return keywords


def main():
    input_csg = 'DIFFERENCE CYLINDER 0.0 0.0 -28.2458 0.0 1.5707963267948966 0.0 6.30111 6.30111 56.4916 ' \
                'DIFFERENCE CYLINDER 0.0 0.0 -28.2458 1.5707963267948963 0.0 0.0 6.30111 6.30111 56.4916 ' \
                'UNION CONE 0 0 0 0 0 0 28.2458 28.2458 53.8882 CYLINDER 0 0 0 0 0 0 12.2988 12.2988 117.848'
    generator = CSGEmbeddingGenerator(input_csg)
    embedding = generator.generate()
    print(embedding)


if __name__ == '__main__':
    main()
