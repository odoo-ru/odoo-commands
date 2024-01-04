import glob

import nox

# # @nox.session(python='3.6')
# #@nox.session(python='3.6', venv_backend='venv', reuse_venv=True)
# def odoo11(session):
#     # session.install('-e', 'odoo-11.0.post20201201/', '--no-deps')
#     # session.install('-r', 'odoo11-requirements.txt')
#     session.install('-r', 'odoo11-requirements.txt', '--no-deps')
#     session.install('-r', 'req.txt', '--no-deps')
#
#     session.run('pytest', 'tests')


def find_odoo_dir(odoo_version):
    dirs = glob.glob(f'.cache/odoo-{odoo_version}.post*')
    if not dirs:
        raise LookupError('Odoo dir not found')
    if len(dirs) > 1:
        raise LookupError(f'Can not choose Odoo dir: {dirs:!r}')
    return dirs[0]


@nox.session(venv_backend='venv', reuse_venv=True)
@nox.parametrize(
    'odoo,python',
    [
        ('11.0', '3.6'),
        ('12.0', '3.8'),
    ],
    ids=['11-36', '12-38'],
)
def test(session, odoo):
    if odoo in {'11.0', '12.0'}:
        # use_2to3 support
        session.install('setuptools==57.5')

    odoo_dir = find_odoo_dir(odoo)
    session.install('-r', f'{odoo_dir}/requirements.txt')
    session.install('-e', odoo_dir, '--no-deps')

    session.install('-r', 'requirements.txt', '--no-deps')
    # session.install('-e', , '--no-deps')

    session.run('pytest', 'tests')
