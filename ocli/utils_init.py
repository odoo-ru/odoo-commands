
def _fnmatch(filename, patterns):
    for pattern in patterns:
        if fnmatch(filename, pattern):
            return True
    return False


def _walk(top, exclude_patterns=EXCLUDE_PATTERNS):
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames.sort()
        reldir = os.path.relpath(dirpath, top)
        if reldir == ".":
            reldir = ""
        for filename in sorted(filenames):
            filepath = os.path.join(reldir, filename)
            if _fnmatch(filepath, exclude_patterns):
                continue
            yield filepath


def addons_hash(module_names, with_demo):
    h = hashlib.sha1()
    h.update("!demo={}!".format(int(bool(with_demo))).encode("utf8"))
    for module_name in sorted(expand_dependencies(module_names, True, True)):
        module_path = odoo.modules.get_module_path(module_name)
        h.update(module_name.encode("utf8"))
        for filepath in _walk(module_path):
            h.update(filepath.encode("utf8"))
            with open(os.path.join(module_path, filepath), "rb") as f:
                h.update(f.read())
    return h.hexdigest()


def odoo_createdb(dbname, demo, module_names, force_db_storage):
    with _patch_ir_attachment_store(force_db_storage):
        odoo.service.db._create_empty_database(dbname)
        odoo.tools.config["init"] = dict.fromkeys(module_names, 1)
        odoo.tools.config["without_demo"] = not demo
        if _odoo_version < odoo.tools.parse_version("10"):
            Registry = odoo.modules.registry.RegistryManager
        else:
            Registry = odoo.modules.registry.Registry
        Registry.new(dbname, force_demo=demo, update_module=True)
        _logger.info(
            click.style(
                "Created new Odoo database {dbname}.".format(**locals()), fg="green"
            )
        )
        with odoo.sql_db.db_connect(dbname).cursor() as cr:
            _save_installed_checksums(cr)
        odoo.sql_db.close_db(dbname)


def main():
    with DbCache(cache_prefix) as dbcache:
        if new_database:
            hashsum = addons_hash(module_names, demo)
            if dbcache.create(new_database, hashsum):
                _logger.info(
                    click.style(
                        "Found matching database template! ✨ 🍰 ✨",
                        fg="green",
                        bold=True,
                    )
                )
                refresh_module_list(new_database)
            else:
                odoo_createdb(new_database, demo, module_names, True)
                dbcache.add(new_database, hashsum)
    if cache_max_size >= 0:
        dbcache.trim_size(cache_max_size)
    if cache_max_age >= 0:
        dbcache.trim_age(timedelta(days=cache_max_age))
