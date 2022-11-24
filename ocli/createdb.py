import ast
import glob
import hashlib
import os
import datetime
from functools import lru_cache
from typing import Set
import time

from click_odoo_contrib.initdb import _walk


def test_time():
    # now = time.time()
    # SECONDS_IN_HOUR = 60 * 60
    # SECONDS_IN_DAY = SECONDS_IN_HOUR * 24
    # SECONDS_IN_WEEK = SECONDS_IN_DAY * 7
    # SECONDS_IN_4_WEEKS = SECONDS_IN_WEEK * 4
    # SECONDS_IN_YEAR = SECONDS_IN_4_WEEKS
    #
    # hour_time = now - now % SECONDS_IN_HOUR
    # day_time = now - now % SECONDS_IN_HOUR + time.timezone
    # week_time = now - now % SECONDS_IN_WEEK - SECONDS_IN_DAY * 4 + time.timezone

    year, month, day, hour, *_ = time.localtime()

    today = datetime.date.today()
    # isoweekday is in range 1-7, starts with Monday
    last_sunday = today - datetime.timedelta(days=today.isoweekday() % 7)

    week_number = last_sunday.isocalendar()[1]  # 1-53

    fourth_week_offset = 4 if week_number == 53 else (week_number - 1) % 4
    four_weeks_date = last_sunday - datetime.timedelta(days=7 * fourth_week_offset)

    twenty_one_week_offset = 26 if week_number == 53 else (week_number - 1) % 26
    twenty_six_weeks_date = last_sunday - datetime.timedelta(days=7 * twenty_one_week_offset)

    return [
        time.mktime((year, month, day, hour, 0, 0, 0, 0, 0)),
        time.mktime((year, month, day, 0, 0, 0, 0, 0, 0)),
        time.mktime(last_sunday.timetuple()),
        time.mktime(four_weeks_date.timetuple()),
        time.mktime(twenty_six_weeks_date.timetuple()),
    ]


def read_manifest(module_dir):
    manifest_path = os.path.join(module_dir, '__manifest__.py')
    # if not os.path.isfile(manifest_path):
    #     raise FileNotFoundError("No Odoo manifest found in %s" % addon_dir)
    with open(manifest_path) as manifest_file:
        return ast.literal_eval(manifest_file.read())


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


class OdooModule:
    def __init__(self):
        pass


class OdooProject:
    def __init__(self, modules_paths):
        self.modules_paths = modules_paths
        # self.cache = {}

    def init_database(self, module_names: Set[str]):
        timestamps = test_time()
        self.install_modules(modules, timestamps)

    def install_modules(self, modules, timestamps=None):
        timestamp = timestamps[0]
        timestamp_modules, hash = sub(modules, timestamp)
        # hash = hash(timestamp_modules)
        if db(hash):
            return db(hash)
        else:
            d = self.install_modules(timestamp_modules, timestamps[1:])
            return init(d, modules - timestamp_modules)


    # Copy of click_odoo_contrib/initdb.py:addons_hash
    def addons_hash(self, module_names, with_demo):
        h = hashlib.sha1()
        h.update("!demo={}!".format(int(bool(with_demo))).encode("utf8"))
        for module_name in sorted(module_names):
            module_path = self.module_path(module_name)
            h.update(module_name.encode("utf8"))
            for filepath in _walk(module_path):
                h.update(filepath.encode("utf8"))
                with open(os.path.join(module_path, filepath), "rb") as f:
                    h.update(f.read())
        return h.hexdigest()

    @lru_cache(maxsize=1024)
    def module_path(self, module_name):
        for modules_path in self.modules_paths:
            module_path = os.path.join(modules_path, module_name)
            if not os.path.isdir(modules_path):
                raise ValueError(f'No module found: {module_name}')
            return module_path

    @lru_cache(maxsize=1024)
    def module_mtime(self, module_name):
        module_path = self.module_path(module_name)
        return max(os.path.getmtime(file_path) for file_path in _walk(module_path))





    def read_dependencies(self, module_names: set):
        for module_name in module_names:

    def cache_key(self, module_names, timestamp):
        module_mtime = {}
        for module_name in module_names:
            module_path = self.path(module_name)




    def modules_cache(self, timestamp):
        # to_install + their deps - their unwanted deps - old modules - their deps


# def module_graph(odoo_version, modules):
#     pass
#
# def modules_cache(module_paths, modules, timestamp):
#     pass


def create_database(name, modules):
    month_cache = modules_cache(modules_paths, modules, timestamp)

