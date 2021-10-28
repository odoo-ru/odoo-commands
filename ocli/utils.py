

# Update

def _save_installed_checksums(cr, ignore_addons=None):
    checksums = {}
    cr.execute("SELECT name FROM ir_module_module WHERE state='installed'")
    for (module_name,) in cr.fetchall():
        if ignore_addons and module_name in ignore_addons:
            continue
        checksums[module_name] = _get_checksum_dir(cr, module_name)
    _set_param(cr, PARAM_INSTALLED_CHECKSUMS, json.dumps(checksums))
    _logger.info("Database updated, new checksums stored")


def _get_checksum_dir(cr, module_name):
    exclude_patterns = _get_param(cr, PARAM_EXCLUDE_PATTERNS, DEFAULT_EXCLUDE_PATTERNS)
    exclude_patterns = [p.strip() for p in exclude_patterns.split(",")]
    cr.execute("SELECT code FROM res_lang WHERE active")
    keep_langs = [r[0] for r in cr.fetchall()]

    module_path = odoo.modules.module.get_module_path(module_name)
    if module_path and os.path.isdir(module_path):
        checksum_dir = addon_hash(module_path, exclude_patterns, keep_langs)
    else:
        checksum_dir = False

    return checksum_dir

# _addon_hash.py
def addon_hash(top, exclude_patterns, keep_langs):
    """Compute a sha1 digest of file contents."""
    m = hashlib.sha1()
    for filepath in _walk(top, exclude_patterns, keep_langs):
        # hash filename so empty files influence the hash
        m.update(filepath.encode("utf-8"))
        # hash file content
        with open(os.path.join(top, filepath), "rb") as f:
            m.update(f.read())
    return m.hexdigest()



def _walk(top, exclude_patterns, keep_langs):
    keep_langs = {lang.split("_")[0] for lang in keep_langs}
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames.sort()
        reldir = os.path.relpath(dirpath, top)
        if reldir == ".":
            reldir = ""
        for filename in sorted(filenames):
            filepath = os.path.join(reldir, filename)
            if _fnmatch(filepath, exclude_patterns):
                continue
            if keep_langs and reldir in {"i18n", "i18n_extra"}:
                basename, ext = os.path.splitext(filename)
                if ext == ".po":
                    if basename.split("_")[0] not in keep_langs:
                        continue
            yield filepath


def _fnmatch(filename, patterns):
    for pattern in patterns:
        if fnmatch(filename, pattern):
            return True
    return False
