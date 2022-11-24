
import tomlkit


def read_config(file_path):
    with open(file_path) as config_file:
        return tomlkit.loads(config_file.read())


def odoo_project_config(file_path):
    return read_config(file_path)['tool']['odoo']

# pyproject = read_config('pyproject.toml')
