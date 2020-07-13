from glob import glob
from setuptools import setup

bin = glob('bin/*')

setup(
    name='eve_utils',
    version='0.5.9',
    description='Utilities to create and manage eve APIs',
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

