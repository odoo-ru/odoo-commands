import nox

# @nox.session(python='3.6')
@nox.session(python='3.6', venv_backend='venv', reuse_venv=True)
# @nox.session(python='3.6', venv_backend='venv', reuse_venv=False)
def odoo11(session):
    # session.install('-e', 'odoo-11.0.post20201201/', '--no-deps')
    # session.install('-r', 'odoo11-requirements.txt')
    session.install('-r', 'odoo11-requirements.txt', '--no-deps')
    session.install('-r', 'req.txt', '--no-deps')

    session.run('pytest', 'tests')
