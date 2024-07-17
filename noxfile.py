import glob

import nox


def find_odoo_dir(odoo_version):
    dirs = glob.glob(f'.cache/odoo-{odoo_version}.post*')
    if not dirs:
        raise LookupError('Odoo dir not found')
    if len(dirs) > 1:
        raise LookupError(f'Can not choose Odoo dir: {dirs!r}')
    return dirs[0]


nox_session = nox.session(venv_backend='venv', reuse_venv=True)
nox_parametrize = nox.parametrize(
    'odoo,python',
    [
        ('15.0', '3.10'),
        ('16.0', '3.10'),
        ('17.0', '3.10'),
    ],
    ids=['15-310', '16-310', '17-310'],
)

nox.session(name='test', venv_backend='venv', reuse_venv=True)
@nox_parametrize
def install_odoo(session, odoo):
    print(f'install {odoo}')
    return

    odoo_dir = find_odoo_dir(odoo)
    session.install('-r', f'{odoo_dir}/requirements.txt')
    session.install('-e', odoo_dir, '--no-deps')

@nox_session
@nox_parametrize
def test(session, odoo):
    odoo_dir = find_odoo_dir(odoo)
    session.install('-r', f'{odoo_dir}/requirements.txt')
    session.install('-e', odoo_dir, '--no-deps')

    session.install('-r', 'requirements.txt', '--no-deps')

    session.run('pytest', 'tests', *session.posargs)
