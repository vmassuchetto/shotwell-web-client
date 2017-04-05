import os, sys, subprocess
try:
    from setuptools import setup
    from setuptools.command.install import install as _install
except ImportError:
    from distutils.core import setup
    from distutils.command.install import install as _install

basepath = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(basepath, 'README.md')) as f:
    long_description = f.read()

with open(os.path.join(basepath, 'requirements.txt')) as f:
    install_requires = f.read().splitlines()

class install(_install):
    def run(self):
        subprocess.check_call(['npm install --prefix shotwell_web_client'], shell=True)
        _install.run(self)

setup(
    name = 'shotwell-web-client',
    version = '0.1',
    license = 'GPLv3',
    description = 'A web client for Shotwell photo manager',
    long_description = long_description,
    author = 'Vinicius Massuchetto',
    url = 'http://github.com/vmassuchetto/shotwell-web-client',
    keywords = 'shotwell web client',
    install_requires = install_requires,
    setup_requires = install_requires,
    packages = ['shotwell_web_client'],
    include_package_data = True,
    cmdclass = {
        'install': install
    },
    entry_points = {
        'console_scripts': ['shotwell-web-client=shotwell_web_client.run:main']
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Multimedia :: Video :: Display'
    ]
)
