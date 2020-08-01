import os
import click
import pickle
import numpy as np

from csg.generate_embedding import CSGEmbeddingGenerator
from csg.generate_models import CSGModelGenerator
from csg.parse_tree import CSGTreeParser


@click.command()
@click.option('--models_path', type=str, default='../scad_models',
              show_default=True, help='Models directory path')
@click.option('--output_dir', type=str, default='../dataset',
              show_default=True, help='Output directory')
@click.option('--samples_per_class', type=int, default=1, show_default=True, help='Generated samples size per class')
def main(models_path, output_dir, samples_per_class):
    model_generator = CSGModelGenerator(models_path, output_dir, samples_per_class)
    model_generator.generate()

    classes = os.listdir(output_dir)
    classes = [os.path.join(output_dir, cls) for cls in classes]
    for cls in sorted(classes):
        csg_files = os.listdir(cls)
        csg_files = [os.path.join(cls, f) for f in csg_files if f.endswith('csg')]
        for file in csg_files:
            parser = CSGTreeParser(file)
            tree = parser.parse()
            emb_generator = CSGEmbeddingGenerator(tree)
            embedding = emb_generator.generate()
            zeros_shape = 108 - len(embedding)  # 108 if one_hot else 54
            embedding.extend(np.zeros(zeros_shape))
            embedding = np.array(embedding)
            embedding_file_name = f'{file[:-4]}_embedding.pkl'
            with open(embedding_file_name, "wb") as f:
                pickle.dump(embedding, f)


if __name__ == "__main__":
    main()
