import fnmatch
import os
import pathlib

# from odoo.tools import PoFile
from babel.messages import extract

# from odoo_commands.config import read_config, odoo_project_config
# from .createdb import OdooProject
from odoo_commands.createdb import OdooProject
from odoo_commands.odoo_translate import PoFile


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

# def extract_t(path, extract_method='python', trans_type='code', extra_keywords={'_': None}, options=options, extra_comments=None):
#
#     if extract_method == 'python':
#         options['encoding'] = 'UTF-8'
#
#     src_file = open(file_abs_path, 'rb')
#     result = []
#     for lineno, message, comments, context in extract.extract(extract_method, src_file, keywords=extract_keywords, options=options):
#         # empty and one-letter terms are ignored, they probably are not meant to be
#         # translated, and would be very hard to translate anyway.
#         source = encode(message)
#         sanitized_term = (source or '').strip()
#         # remove non-alphanumeric chars
#         sanitized_term = re.sub(r'\W+', '', sanitized_term)
#         if not sanitized_term or len(sanitized_term) <= 1:
#             continue
#         result.append((module, trans_type, display_path, lineno, source, comments + extra_comments))
#
#     return result


def extract_terms_1(module_path):
    terms = []
    module_path = pathlib.Path(module_path)

    terms.extend(extract_t())
    for root, _, file_names in module_path.glob('**/*.py'):
        for file_name in fnmatch.filter(file_names, '*.py'):
            babel_extract_terms(file_name, path, root, 'python', trans_type='code', extra_comments=[], extract_keywords={'_': None})
        # mako provides a babel extractor: http://docs.makotemplates.org/en/latest/usage.html#babel
        for file_name in fnmatch.filter(file_names, '*.mako'):
            babel_extract_terms(file_name, path, root, 'mako', trans_type='report', extra_comments=[], extract_keywords={'_': None})
        # Javascript source files in the static/src/js directory, rest is ignored (libs)
        if fnmatch.fnmatch(root, '*/static/src/js*'):
            babel_extract_terms(file_name, path, root, 'javascript', trans_type='code', extra_comments=[WEB_TRANSLATION_COMMENT], extract_keywords={'_t': None, '_lt': None})
        # QWeb template files
        if fnmatch.fnmatch(root, '*/static/src/xml*'):
            babel_extract_terms(file_name, path, root, 'odoo.tools.translate:babel_extract_qweb', trans_type='code', extra_comments=[WEB_TRANSLATION_COMMENT], extract_keywords={'_': None})

def extract_2(module_name, module_path):
    result = []
    module_path = pathlib.Path(module_path)
    for extract_method, path_template in {
        ('python', '**/*.py'),
    }:
        trans_type = 'report' if extract_method == 'mako' else 'code'
        extract_keywords = {'_t': None, '_lt': None} if extract_method == 'javascript' else {'_': None}
        extra_comments = (
            ['openerp-web']
            if extract_method in {'javascript', 'odoo.tools.translate:babel_extract_qweb'}
            else []
        )

        for file_path in module_path.glob(path_template):
            display_path = 'addons/' + str(file_path)
            with open(file_path, 'rb') as src_file:
                for extracted in extract.extract(extract_method, src_file, keywords=extract_keywords):
                    lineno, message, comments = extracted[:3]
                    # result.append((module_name,  message, display_path, lineno, trans_type, tuple(comments + extra_comments)))
                    result.append((module_name, trans_type, display_path, lineno, message, '', tuple(comments + extra_comments)))
    return result


# def push_translation(module, type, name, id, source, comments=None):
#     # empty and one-letter terms are ignored, they probably are not meant to be
#     # translated, and would be very hard to translate anyway.
#     sanitized_term = (source or '').strip()
#     # remove non-alphanumeric chars
#     sanitized_term = re.sub(r'\W+', '', sanitized_term)
#     if not sanitized_term or len(sanitized_term) <= 1:
#         return
#
#     tnx = (module, source, name, id, type, tuple(comments or ()))
#     to_translate.add(tnx)


def babel_extract_terms(fname, path, root, extract_method="python", trans_type='code',
                            extra_comments=None, extract_keywords={'_': None}):
    module, fabsolutepath, _, display_path = verified_module_filepaths(fname, path, root)
    extra_comments = extra_comments or []
    if not module:
        return
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

    # # return terms
    #
    # # we now group the translations by source. That means one translation per source.
    # grouped_rows = {}
    # for module, type, name, res_id, src, comments in sorted(terms):
    #     row = grouped_rows.setdefault(src, {})
    #     row.setdefault('modules', set()).add(module)
    #     # if not row.get('translation') and trad != src:
    #     #     row['translation'] = trad
    #     row.setdefault('tnrs', []).append((type, name, res_id))
    #     row.setdefault('comments', set()).update(comments)
    #
    # pot_file_path = os.path.join(module_path, f'i18n/{module_name}.pot')
    # with open(pot_file_path, 'wb') as buffer:
    #     writer = PoFile(buffer)
    #     writer.write_infos(modules)
    #
    #     for src, row in sorted(grouped_rows.items()):
    #         if not lang:
    #             # translation template, so no translation value
    #             row['translation'] = ''
    #         elif not row.get('translation'):
    #             row['translation'] = src
    #         writer.write(row['modules'], row['tnrs'], src, row['translation'], row['comments'])

def write_pot(modules, rows, pot_path, lang):
    buffer = open(pot_path, 'wb')
    writer = PoFile(buffer)
    writer.write_infos(modules)

    # we now group the translations by source. That means one translation per source.
    grouped_rows = {}
    for module, type, name, res_id, src, trad, comments in rows:
        row = grouped_rows.setdefault(src, {})
        row.setdefault('modules', set()).add(module)
        if not row.get('translation') and trad != src:
            row['translation'] = trad
        row.setdefault('tnrs', []).append((type, name, res_id))
        row.setdefault('comments', set()).update(comments)

    for src, row in sorted(grouped_rows.items()):
        if not lang:
            # translation template, so no translation value
            row['translation'] = ''
        elif not row.get('translation'):
            row['translation'] = src
        writer.write(row['modules'], row['tnrs'], src, row['translation'], row['comments'])


def generate_pot(module_paths, module_name):
    project = OdooProject(module_paths)
    module_path = project.module_path(module_name)
    res = extract_2(module_name, module_path)
    print(res)
    write_pot([module_name], res, 'test.pot', False)


generate_pot(['tests/addons/'], 'module_name')
