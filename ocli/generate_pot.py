import fnmatch
import os
import pathlib

from odoo.tools import PoFile
from babel.messages import extract


def babel_extract_terms_v11(fname, path, root, extract_method="python", trans_type='code',
                        extra_comments=None, extract_keywords={'_': None}):
    module, fabsolutepath, _, display_path = verified_module_filepaths(fname, path, root)
    extra_comments = extra_comments or []
    if not module: return
    src_file = open(fabsolutepath, 'rb')
    options = {}
    if extract_method == 'python':
        options['encoding'] = 'UTF-8'
    try:
        for extracted in extract.extract(extract_method, src_file, keywords=extract_keywords, options=options):
            # Babel 0.9.6 yields lineno, message, comments
            # Babel 1.3 yields lineno, message, comments, context
            lineno, message, comments = extracted[:3]
            push_translation(module, trans_type, display_path, lineno, encode(message), comments + extra_comments)
    except Exception:
        _logger.exception("Failed to extract terms from %s", fabsolutepath)
    finally:
        src_file.close()

def extract_t(path, extract_method='python', trans_type='code', extra_keywords={'_': None}, options=options,
              extra_comments=None):

    if extract_method == 'python':
        options['encoding'] = 'UTF-8'

    src_file = open(file_abs_path, 'rb')
    result = []
    for lineno, message, comments, context in extract.extract(extract_method, src_file, keywords=extract_keywords, options=options):
        # empty and one-letter terms are ignored, they probably are not meant to be
        # translated, and would be very hard to translate anyway.
        source = encode(message)
        sanitized_term = (source or '').strip()
        # remove non-alphanumeric chars
        sanitized_term = re.sub(r'\W+', '', sanitized_term)
        if not sanitized_term or len(sanitized_term) <= 1:
            continue
        result.append((module, trans_type, display_path, lineno, source, comments + extra_comments))

    return result


def extract_terms(module_path):
    terms = []
    module_path = pathlib.Path(module_path)

    terms.extend(extract_t())
    for root, _, file_names in module_path.glob('**/*.py'):

        for file_name in fnmatch.filter(file_names, '*.py'):
            terms.append(babel_extract_terms(file_name, path, root))

        # mako provides a babel extractor: http://docs.makotemplates.org/en/latest/usage.html#babel
        for file_name in fnmatch.filter(file_names, '*.mako'):
            babel_extract_terms(file_name, path, root, 'mako', trans_type='report')

        # Javascript source files in the static/src/js directory, rest is ignored (libs)
        if fnmatch.fnmatch(root, '*/static/src/js*'):
            for file_name in fnmatch.filter(file_names, '*.js'):
                babel_extract_terms(file_name, path, root, 'javascript',
                                    extra_comments=[WEB_TRANSLATION_COMMENT],
                                    extract_keywords={'_t': None, '_lt': None})
        # QWeb template files
        if fnmatch.fnmatch(root, '*/static/src/xml*'):
            for file_name in fnmatch.filter(file_names, '*.xml'):
                babel_extract_terms(file_name, path, root, 'odoo.tools.translate:babel_extract_qweb',
                                    extra_comments=[WEB_TRANSLATION_COMMENT])

    return terms

    # we now group the translations by source. That means one translation per source.
    grouped_rows = {}
    for module, type, name, res_id, src, comments in sorted(terms):
        row = grouped_rows.setdefault(src, {})
        row.setdefault('modules', set()).add(module)
        # if not row.get('translation') and trad != src:
        #     row['translation'] = trad
        row.setdefault('tnrs', []).append((type, name, res_id))
        row.setdefault('comments', set()).update(comments)

    pot_file_path = os.path.join(module_path, f'i18n/{module_name}.pot')
    with open(pot_file_path, 'wb') as buffer:
        writer = PoFile(buffer)
        writer.write_infos(modules)

        for src, row in sorted(grouped_rows.items()):
            if not lang:
                # translation template, so no translation value
                row['translation'] = ''
            elif not row.get('translation'):
                row['translation'] = src
            writer.write(row['modules'], row['tnrs'], src, row['translation'], row['comments'])
