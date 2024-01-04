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
Clone
```console
git clone git@github.com:odoo-ru/odoo-commands.git
cd odoo-commands
```
Download and unpack all supported Odoos
```commandline
./download-odoo.sh
```
Install [nox](https://github.com/wntrblm/nox)
```commandline
pipx install now
```
Create environments for all presented Python interpreters and run tests
```commandline
nox
```
Run tests using existing environment
```commandline
nox -R -s 
```



