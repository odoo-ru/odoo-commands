import re
import codecs
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

def quote(s):
    """Returns quoted PO term string, with special PO characters escaped"""
    assert r"\n" not in s, "Translation terms may not include escaped newlines ('\\n'), please use only literal newlines! (in '%s')" % s
    return '"%s"' % s.replace('\\','\\\\') \
                     .replace('"','\\"') \
                     .replace('\n', '\\n"\n"')

re_escaped_char = re.compile(r"(\\.)")
re_escaped_replacements = {'n': '\n', 't': '\t',}

def _sub_replacement(match_obj):
    return re_escaped_replacements.get(match_obj.group(1)[1], match_obj.group(1)[1])

def unquote(str):
    """Returns unquoted PO term string, with special PO characters unescaped"""
    return re_escaped_char.sub(_sub_replacement, str[1:-1])


class PoFile(object):
    def __init__(self, buffer):
        # TextIOWrapper closes its underlying buffer on close *and* can't
        # handle actual file objects (on python 2)
        self.buffer = codecs.StreamReaderWriter(
            stream=buffer,
            Reader=codecs.getreader('utf-8'),
            Writer=codecs.getwriter('utf-8')
        )

    def __iter__(self):
        self.buffer.seek(0)
        self.lines = self._get_lines()
        self.lines_count = len(self.lines)

        self.first = True
        self.extra_lines= []
        return self

    def _get_lines(self):
        lines = self.buffer.readlines()
        # remove the BOM (Byte Order Mark):
        if len(lines):
            lines[0] = lines[0].lstrip(u"\ufeff")

        lines.append('') # ensure that the file ends with at least an empty line
        return lines

    def cur_line(self):
        return self.lines_count - len(self.lines)

    def next(self):
        trans_type = name = res_id = source = trad = None
        if self.extra_lines:
            trans_type, name, res_id, source, trad, comments = self.extra_lines.pop(0)
            if not res_id:
                res_id = '0'
        else:
            comments = []
            targets = []
            line = None
            fuzzy = False
            while not line:
                if 0 == len(self.lines):
                    raise StopIteration()
                line = self.lines.pop(0).strip()
            while line.startswith('#'):
                if line.startswith('#~ '):
                    break
                if line.startswith('#.'):
                    line = line[2:].strip()
                    if not line.startswith('module:'):
                        comments.append(line)
                elif line.startswith('#:'):
                    # Process the `reference` comments. Each line can specify
                    # multiple targets (e.g. model, view, code, selection,
                    # ...). For each target, we will return an additional
                    # entry.
                    for lpart in line[2:].strip().split(' '):
                        trans_info = lpart.strip().split(':',2)
                        if trans_info and len(trans_info) == 2:
                            # looks like the translation trans_type is missing, which is not
                            # unexpected because it is not a GetText standard. Default: 'code'
                            trans_info[:0] = ['code']
                        if trans_info and len(trans_info) == 3:
                            # this is a ref line holding the destination info (model, field, record)
                            targets.append(trans_info)
                elif line.startswith('#,') and (line[2:].strip() == 'fuzzy'):
                    fuzzy = True
                line = self.lines.pop(0).strip()
            if not self.lines:
                raise StopIteration()
            while not line:
                # allow empty lines between comments and msgid
                line = self.lines.pop(0).strip()
            if line.startswith('#~ '):
                while line.startswith('#~ ') or not line.strip():
                    if 0 == len(self.lines):
                        raise StopIteration()
                    line = self.lines.pop(0)
                # This has been a deprecated entry, don't return anything
                return next(self)

            if not line.startswith('msgid'):
                raise Exception("malformed file: bad line: %s" % line)
            source = unquote(line[6:])
            line = self.lines.pop(0).strip()
            if not source and self.first:
                self.first = False
                # if the source is "" and it's the first msgid, it's the special
                # msgstr with the informations about the traduction and the
                # traductor; we skip it
                self.extra_lines = []
                while line:
                    line = self.lines.pop(0).strip()
                return next(self)

            while not line.startswith('msgstr'):
                if not line:
                    raise Exception('malformed file at %d'% self.cur_line())
                source += unquote(line)
                line = self.lines.pop(0).strip()

            trad = unquote(line[7:])
            line = self.lines.pop(0).strip()
            while line:
                trad += unquote(line)
                line = self.lines.pop(0).strip()

            if targets and not fuzzy:
                # Use the first target for the current entry (returned at the
                # end of this next() call), and keep the others to generate
                # additional entries (returned the next next() calls).
                trans_type, name, res_id = targets.pop(0)
                code = trans_type == 'code'
                for t, n, r in targets:
                    if t == 'code' and code: continue
                    if t == 'code':
                        code = True
                    self.extra_lines.append((t, n, r, source, trad, comments))

        if name is None:
            if not fuzzy:
                _logger.warning('Missing "#:" formated comment at line %d for the following source:\n\t%s',
                                self.cur_line(), source[:30])
            return next(self)
        return trans_type, name, res_id, source, trad, '\n'.join(comments)
    __next__ = next

    def write_infos(self, modules):
        # import odoo.release as release
        self.buffer.write(u"# Translation of %(project)s.\n" \
                          "# This file contains the translation of the following modules:\n" \
                          "%(modules)s" \
                          "#\n" \
                          "msgid \"\"\n" \
                          "msgstr \"\"\n" \
                          '''"Project-Id-Version: %(project)s %(version)s\\n"\n''' \
                          '''"Report-Msgid-Bugs-To: \\n"\n''' \
                          '''"POT-Creation-Date: %(now)s\\n"\n'''        \
                          '''"PO-Revision-Date: %(now)s\\n"\n'''         \
                          '''"Last-Translator: <>\\n"\n''' \
                          '''"Language-Team: \\n"\n'''   \
                          '''"MIME-Version: 1.0\\n"\n''' \
                          '''"Content-Type: text/plain; charset=UTF-8\\n"\n'''   \
                          '''"Content-Transfer-Encoding: \\n"\n'''       \
                          '''"Plural-Forms: \\n"\n'''    \
                          "\n"

                          # % { 'project': release.description,
                          % { 'project': 'proj',
                              # 'version': release.version,
                              'version': '11',
                              'modules': ''.join("#\t* %s\n" % m for m in modules),
                              'now': datetime.utcnow().strftime('%Y-%m-%d %H:%M')+"+0000",
                            }
                          )

    def write(self, modules, tnrs, source, trad, comments=None):

        plurial = len(modules) > 1 and 's' or ''
        self.buffer.write(u"#. module%s: %s\n" % (plurial, ', '.join(modules)))

        if comments:
            self.buffer.write(u''.join(('#. %s\n' % c for c in comments)))

        code = False
        for typy, name, res_id in tnrs:
            self.buffer.write(u"#: %s:%s:%s\n" % (typy, name, res_id))
            if typy == 'code':
                code = True

        if code:
            # only strings in python code are python formated
            self.buffer.write(u"#, python-format\n")

        msg = (
            u"msgid %s\n"
            u"msgstr %s\n\n"
        ) % (
            quote(str(source)),
            quote(str(trad))
        )
        self.buffer.write(msg)
