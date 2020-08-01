import os

from tqdm import tqdm


class CSGModelGenerator:
    def __init__(self, input_dir: str, output_dir: str, samples_per_class: int = 200):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.samples_per_class = samples_per_class

        self.scad_files = []
        self.seed_value = 0

    def generate(self):
        self._load_scad_models()
        self._generate_files()

    def _load_scad_models(self):
        self.scad_files = os.listdir(self.input_dir)
        self.scad_files = [os.path.join(self.input_dir, file) for file in self.scad_files]
        self.scad_files = sorted(self.scad_files)

    def _generate_files(self):
        for file in tqdm(self.scad_files):
            output_dir = self._create_output_dir(file)
            for i in range(self.samples_per_class):
                self._set_seed_value(file)
                output_stl_file_name = os.path.join(output_dir, f'{i}.stl')
                output_csg_file_name = os.path.join(output_dir, f'{i}.csg')
                os.system(f'openscad -o {output_stl_file_name} {file}')
                os.system(f'openscad -o {output_csg_file_name} {file}')

    def _set_seed_value(self, file):
        with open(file) as f:
            content = f.readlines()
        content[0] = f'seed = {self.seed_value};\n'
        with open(file, 'w') as f:
            f.writelines(content)
        self.seed_value += 1

    def _create_output_dir(self, file):
        dir_name = os.path.splitext(os.path.basename(file))[0]
        output_dir = os.path.join(self.output_dir, dir_name)
        os.makedirs(output_dir, exist_ok=True)

        return output_dir


def main():
    models_path = '../scad_models/'
    dataset_path = '../dataset'
    generator = CSGModelGenerator(models_path, dataset_path, 1)
    generator.generate()


if __name__ == '__main__':
    main()
