Odoo Commands
=============
[![PyPI](https://img.shields.io/pypi/pyversions/odoo-commands.svg)](https://pypi.org/project/odoo-commands/ "Latest version on PyPI")
[![Docs](https://readthedocs.org/projects/odoo-commands/badge/?version=stable)](https://odoo-commands.readthedocs.io/en/latest/ "Read the docs")

Project description

Install
-------
```commandline
pip install odoo-commands
```

Development
-----------
We need installed `pyenv` and `pipenv`.
```console
git clone git@github.com:odoo-ru/odoo-commands.git

cd odoo-commands
pipenv install --dev
```

Run tests:
```console
pipenv run fulltest
```

# After `import odoo` local time zone changes to UTC
# We want to find out OS time zone
# echo $TZ - empty
# date +%Z - UTC
# cat /etc/timezone - Local
