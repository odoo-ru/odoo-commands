import ast
import glob
import hashlib
import os
import datetime
from functools import lru_cache
from pprint import pprint
from typing import Set
import time

# import odoo

# from click_odoo_contrib.initdb import _walk

import logging

logger = logging.getLogger(__name__)


class IndentLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        indent_level = self.extra['indent_level']
        return '    ' * indent_level + msg, kwargs



def cache_time_point_generator(dt=None):
    if dt:
        now = dt
    else:
        # now = datetime.datetime.now()
        now = datetime.datetime.utcnow()

    today = now.date()
    # weekday is in [0,6]; 0 is Monday
    last_monday = today - datetime.timedelta(days=today.weekday())

    first_monday = datetime.date(1970, 1, 5)
    days_from_first_monday = (last_monday - first_monday).days

    last_4th_sunday = last_monday - datetime.timedelta(days=days_from_first_monday % (7 * 4))
    last_24th_sunday = last_monday - datetime.timedelta(days=days_from_first_monday % (7 * 24))

    year, month, day, hour, *_ = now.timetuple()
    return [
        datetime.datetime(year, month, day, hour, 0, 0, 0),
        datetime.datetime(year, month, day, 0, 0, 0, 0),
        last_monday,
        last_4th_sunday,
        last_24th_sunday,
    ]

    return [
        time.mktime((year, month, day, hour, 0, 0, 0, 0, 0)),
        time.mktime((year, month, day, 0, 0, 0, 0, 0, 0)),
        time.mktime(last_monday.timetuple()),
        time.mktime(last_4th_sunday.timetuple()),
        time.mktime(last_24th_sunday.timetuple()),
    ]

pprint(cache_time_point_generator())


# def read_manifest(module_dir):
#     manifest_path = os.path.join(module_dir, '__manifest__.py')
#     # if not os.path.isfile(manifest_path):
#     #     raise FileNotFoundError("No Odoo manifest found in %s" % addon_dir)
#     with open(manifest_path) as manifest_file:
#         return ast.literal_eval(manifest_file.read())


contrib_module_path = '/home/voronin/.local/share/virtualenvs/sintez_addons-7QRHjYmJ/lib/python3.6/site-packages/odoo/addons'

def module_dependencies(module_dir):
    return read_manifest(module_dir).get('depends', [])


def contrib_module_deps(contrib_module_path):
    res = {}
    for module_dir in glob.iglob(contrib_module_path + '/*'):
        if module_dir.endswith('__pycache__') or module_dir.endswith('__init__.py'):
            continue
        res[module_dir] = module_dependencies(module_dir)
    return res


def install_recursively(modules, cache_time_points, level=0):
    indent_logger = IndentLogger(logger, {'indent_level': level})


def create_database(name, modules):
    month_cache = modules_cache(modules_paths, modules, timestamp)

