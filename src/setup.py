from glob import glob
from setuptools import setup

setup(
    name='eve-utils',
    version='0.9.5',
    description='Templates and scripts to rapidly spin up a production-ready Eve-based API.',
    long_description=open('../README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Utilities'
    ],
    url='https://github.com/pointw-dev/eve-utils',
    author='Michael Ottoson',
    author_email='michael@pointw.com',
    packages=['eve_utils'],
    include_package_data=True,
    install_requires=[
        'libcst',
        'inflect'
    ],
    scripts=glob('bin/*'),
    zip_safe=False
)
