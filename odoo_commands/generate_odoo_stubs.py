import pathlib

import astroid





def is_odoo_module(path):
    if isinstance(path, str):
        path = pathlib.Path(path)
    return path.is_dir() and (path / '__manifest__.py').is_file()


def generate(modules_path):
    for path in pathlib.Path(modules_path).iterdir():
        if is_odoo_module(path):
            for model_file in find_model_files(path)



