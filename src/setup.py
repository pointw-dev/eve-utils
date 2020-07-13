from glob import glob
from setuptools import setup

# TODO: pull PyInstaller out of packages, make it a command (mkwin32?)
# TODO: remove python 2.7 compatibilities (six, .format(), etc.)
# TODO: doco CORS
# TODO: SMTP_HOST/recipients

bin = glob('bin/*')

setup(
    name='eve-utils',
    version='0.6.6',
    description='Templates and scripts to rapidly spin up an Eve-based API.',
    long_description=open('README.rst').read(),
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Utilities'
    ],
    url='http://www.pointw.com',
    author='Michael Ottoson',
    author_email='michael@pointw.com',
    packages=['eve_utils'],
    include_package_data=True,
    install_requires=[
        'libcst',
        'inflect'
    ],
    scripts=bin,
    zip_safe=False
)

