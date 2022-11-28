import ast
import glob
import hashlib
import os
import datetime
from functools import lru_cache
from typing import Set
import time

# from click_odoo_contrib.initdb import _walk


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


# def module_graph(odoo_version, modules):
#     pass
#
# def modules_cache(module_paths, modules, timestamp):
#     pass


def create_database(name, modules):
    month_cache = modules_cache(modules_paths, modules, timestamp)

