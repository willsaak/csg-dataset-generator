from enum import Enum


class NodeType(Enum):
    OPERATION = 1
    PRIMITIVE = 2
    TRANSFORMATION = 3


class CSGTreeParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.node_id = 0
        self.tree = {}

    def parse(self):
        self.extract_tree()

        print('Extracting and printing tree...')
        self.extract_tree_with_primitive_specs()
        print_simple_tree(self.tree)

        print('Transforming primitives and printing tree...')
        self.extract_tree_with_transformed_primitives()
        print_simple_tree(self.tree)

        print('Flattening and printing tree...')
        self.flatten_tree()
        print_simple_tree(self.tree)

        print('Formatting and printing result...')
        formatted_tree = self.format_tree()
        print(formatted_tree)
        return formatted_tree

    def append_new_node(self, node_type: NodeType, keyword, last_node, source):
        new_node = {
            'node_id': self.node_id,
            'type': node_type,
            'keyword': keyword,
            'children': [],
            'parent': last_node,
            'additional_info': source,
        }
        self.node_id += 1
        last_node['children'].append(new_node)
        return new_node

    def extract_tree(self):
        csg_tree = {
            'type': NodeType.OPERATION,
            'keyword': 'group',
            'children': [],
            'parent': None
        }
        last_node = csg_tree
        with open(self.file_path) as f:
            content = f.readlines()
        content = content[1:-1]
        # content = [c.replace('group', 'union') for c in content]

        for line in content:
            line = clear_line(line)
            bracket_index = line.find('(')
            if bracket_index == -1:
                last_node = last_node['parent']
                continue
            keyword = line[:bracket_index]
            if is_operation(keyword):
                self.append_new_node(NodeType.OPERATION, keyword, last_node, line)
                last_node = last_node['children'][-1]
            elif is_primitive(keyword):
                if keyword == 'cylinder':
                    spec = get_spec_from_primitive_line(line)
                    r1 = float(get_value_from_spec(spec, 'r1'))
                    r2 = float(get_value_from_spec(spec, 'r2'))
                    if r1 == r2:
                        self.append_new_node(NodeType.PRIMITIVE, keyword, last_node, line)
                    elif r2 == 0:
                        self.append_new_node(NodeType.PRIMITIVE, 'cone', last_node, line.replace('cylinder', 'cone'))
                    # elif r1 == 0:
                    #     pass  # rotate and then append
                else:
                    self.append_new_node(NodeType.PRIMITIVE, keyword, last_node, line)
            else:
                assert keyword == 'multmatrix'
                self.append_new_node(NodeType.TRANSFORMATION, keyword, last_node, line)
                last_node = last_node['children'][-1]
        self.tree = csg_tree

    def extract_tree_with_primitive_specs(self):
        def extract_primitive_spec(tree):
            for child in tree['children']:
                if child['type'] == NodeType.PRIMITIVE:
                    extractor = get_extractor_for_primitive(child["keyword"])
                    x, y, z, sx, sy, sz = extractor(child['additional_info'])
                    primitive_spec = {
                        'primitive': child["keyword"],
                        'x': x,
                        'y': y,
                        'z': z,
                        'r0': 0,
                        'r1': 0,
                        'r2': 0,
                        'sx': sx,
                        'sy': sy,
                        'sz': sz,
                    }
                    child['additional_info'] = primitive_spec
                else:
                    extract_primitive_spec(child)

        extract_primitive_spec(self.tree)

    def extract_tree_with_transformed_primitives(self):
        from transformations import decompose_matrix

        def transform_primitives(tree, spec):
            for child in tree:
                if child['type'] == NodeType.PRIMITIVE:
                    child['additional_info']['x'] += spec['x']
                    child['additional_info']['y'] += spec['y']
                    child['additional_info']['z'] += spec['z']
                    child['additional_info']['r0'] += spec['r0']
                    child['additional_info']['r1'] += spec['r1']
                    child['additional_info']['r2'] += spec['r2']
                    child['additional_info']['sx'] *= spec['sx']
                    child['additional_info']['sy'] *= spec['sy']
                    child['additional_info']['sz'] *= spec['sz']
                else:
                    transform_primitives(child['children'], spec)

        def get_transformation(transformation):
            transformation_matrix_str = transformation[transformation.find('(') + 1:transformation.rfind(')')]
            transformation_matrix = extract_matrix_from_str(transformation_matrix_str)
            decomposed_matrix = decompose_matrix(transformation_matrix)
            scale = decomposed_matrix[0]
            rotation = decomposed_matrix[2]
            translation = decomposed_matrix[3]
            transformation_spec = {
                'x': translation[0],
                'y': translation[1],
                'z': translation[2],
                'r0': rotation[0],
                'r1': rotation[1],
                'r2': rotation[2],
                'sx': scale[0],
                'sy': scale[1],
                'sz': scale[2],
            }
            return transformation_spec

        def extract_transformed_tree(tree):
            for child in tree:
                if child['type'] == NodeType.TRANSFORMATION:
                    spec = get_transformation(child['additional_info'])
                    transform_primitives(child['children'], spec)

                    parent = child['parent']
                    parent['children'].remove(child)
                    for node in child['children']:
                        node['parent'] = parent
                        parent['children'].append(node)
                else:
                    extract_transformed_tree(child['children'])

        def has_transformations(tree):
            result = False
            for child in tree:
                if child['type'] == NodeType.TRANSFORMATION:
                    result = True
                elif child['type'] == NodeType.OPERATION:
                    result = True if result else has_transformations(child['children'])
            return result

        while has_transformations(self.tree['children']):
            extract_transformed_tree(self.tree['children'])

    def flatten_tree(self):
        def flatten_children(children):
            if len(children) > 2:
                assert children[-1]['type'] == NodeType.PRIMITIVE, 'Whoops, did not expect this'
                parent = children[0]['parent']
                new_node = {
                    'type': parent['type'],
                    'keyword': parent['keyword'],
                    'children': children[:-1],
                    'parent': parent,
                    'additional_info': parent['additional_info'],
                }
                for c in new_node['children']:
                    c['parent'] = new_node
                parent['children'] = [new_node, children[-1]]
                children = parent['children']
            for child in children:
                if child['type'] == NodeType.OPERATION:
                    flatten_children(child['children'])

        def delete_group(tree):
            for child in tree:
                if child['keyword'] == 'group':
                    child['parent']['children'].remove(child)
                    child['parent']['children'].extend(child['children'])
                    for c in child['children']:
                        c['parent'] = child['parent']
                delete_group(child['children'])

        delete_group(self.tree['children'])

        flatten_children(self.tree['children'])

    def format_tree(self):
        assert len(self.tree['children']) == 1
        first_op = self.tree['children'][0]
        formated_tree = f'{first_op["keyword"].upper()} '

        def format_child(children, formated_tree):
            if not children:
                return formated_tree
            primitives = [c for c in children if c['type'] == NodeType.PRIMITIVE]
            operations = [c for c in children if c['type'] == NodeType.OPERATION]
            to_format = []
            assert len(operations) < 2, 'Tree is not flat'
            assert len(operations) + len(primitives) == 2, 'Tree is not flat'

            for primitive in primitives:
                formated_tree += f'{primitive["keyword"].upper()} ' \
                                 f'{primitive["additional_info"]["x"]} {primitive["additional_info"]["y"]} ' \
                                 f'{primitive["additional_info"]["z"]} {primitive["additional_info"]["r0"]} ' \
                                 f'{primitive["additional_info"]["r1"]} {primitive["additional_info"]["r2"]} ' \
                                 f'{primitive["additional_info"]["sx"]} {primitive["additional_info"]["sy"]} ' \
                                 f'{primitive["additional_info"]["sz"]} '
            for operation in operations:
                formated_tree += f'{operation["keyword"].upper()} '
                to_format.extend(operation['children'])
            # print(formated_tree)
            formated_tree = format_child(to_format, formated_tree)
            return formated_tree

        formated_tree = format_child(first_op['children'], formated_tree)
        return formated_tree


def is_operation(keyword):
    return keyword in get_operations()


def is_primitive(keyword):
    return keyword in get_primitives()


def clear_line(line):
    line = ''.join(line.split())
    return line


def get_operations():
    operations = [
        'difference',
        'union',
        'intersection',
        'group',
    ]
    return operations


def get_primitives():
    primitives = [
        'cube',
        'sphere',
        'cylinder',
    ]
    return primitives


def get_extractor_for_primitive(primitive):
    functions = {
        'cube': extract_cube_spec,
        'cylinder': extract_cylinder_spec,
        'sphere': extract_sphere_spec,
        'cone': extract_cylinder_spec,
    }
    extractor = functions[primitive]
    return extractor


def get_spec_from_primitive_line(line):
    spec = line[line.find('(') + 1:line.find(')')]
    spec = spec.split(',')
    return spec


def get_value_from_spec(spec, value_name):
    value = [name for name in spec if name.find(value_name) == 0][0]
    value = value[len(value_name) + 1:]
    return value


def extract_cube_spec(line):
    cube_size = line[line.find('[') + 1:line.find(']')]
    cube_size = cube_size.split(',')
    sx, sy, sz = [float(s) for s in cube_size]
    x, y, z = 0, 0, 0
    spec = get_spec_from_primitive_line(line)
    if get_value_from_spec(spec, 'center') == 'true':
        x, y, z = -sx / 2, -sy / 2, -sz / 2
    return x, y, z, sx, sy, sz


def extract_cylinder_spec(line):
    spec = get_spec_from_primitive_line(line)
    h = float(get_value_from_spec(spec, 'h'))
    r1 = float(get_value_from_spec(spec, 'r1'))
    r2 = float(get_value_from_spec(spec, 'r2'))
    max_diameter = max(r1, r2)
    x, y, z = 0, 0, 0
    if get_value_from_spec(spec, 'center') == 'true':
        z = -h / 2
    return x, y, z, max_diameter, max_diameter, h


def extract_sphere_spec(line):
    spec = get_spec_from_primitive_line(line)
    r = float(get_value_from_spec(spec, 'r'))
    x, y, z = 0, 0, 0
    return x, y, z, r, r, r


def extract_matrix_from_str(matrix_str):
    matrix_str = clear_line(matrix_str)
    matrix_str = matrix_str.replace('[', '').replace(']', '')
    numbers = matrix_str.split(',')
    assert len(numbers) == 16
    numbers = [float(number) for number in numbers]
    matrix = [
        numbers[0:4],
        numbers[4:8],
        numbers[8:12],
        numbers[12:],
    ]
    return matrix


def get_rotation_angles(matrix):
    from transformations import euler_from_matrix
    return euler_from_matrix(matrix)


def print_simple_tree(tree):
    tabs_count = 0

    def print_child(tree, tabs_count):
        for child in tree['children']:
            print('-' * tabs_count + child['keyword'])
            if child['children']:
                print_child(child, tabs_count + 1)

    print_child(tree, tabs_count)


def main():
    csg_path = '../dataset/01/0.csg'
    parser = CSGTreeParser(file_path=csg_path)
    _ = parser.parse()


if __name__ == '__main__':
    main()
