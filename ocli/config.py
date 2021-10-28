
import tomlkit


def read_config(file_path):
    with open(file_path) as config_file:
        return tomlkit.loads(config_file.read())


pyproject = read_config('pyproject.toml')
