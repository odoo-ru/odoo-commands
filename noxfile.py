import nox

# @nox.session(python='3.6')
@nox.session(python='3.6', venv_backend='venv', reuse_venv=True)
def odoo11(session):
    # session.install('setuptools==57.5')
    # session.run('pip', 'install', 'pip<23')
    # session.run('pip', 'install', 'setuptools==57.5')

    # session.install('-e', 'odoo-11.0.post20201201/', '--no-deps')
    # session.install('-r', 'odoo11-requirements.txt')

    # session.install('idna==3.4')
    # session.install('six')
    # session.install('urllib3==1.26.15')

    # session.run('odoo', '--help')
    session.run('pip', 'freeze')

