#!/usr/bin/env python
"""Adds windows service class to the API project.

This also installs PyInstaller and supporting libraries files.

NOTE: this is experimenatl and may not work 100%

Usage:
    add_svc [-h|--help]
      NOTE: Must be run in the project folder

Examples:
    add_svc

License:
    MIT License

    Copyright (c) 2021 Michael Ottoson

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import os
import subprocess
import sys
import argparse
import eve_utils

import subprocess
import sys


def main():
    parser = argparse.ArgumentParser('add_svc', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    args = parser.parse_args()

    if not os.path.exists('./requirements.txt'):
        print('requirements.txt missing - must be run in the API folder')
        quit(1)
        
    if not os.path.exists('./domain'):
        print('domain folder missing - must be run in the API folder')
        quit(2)
        
    if os.path.exists('./svc-tools'):
        print('svc-tools folder already exists')
        quit(3)
        
    project_name = os.path.basename(os.getcwd())
    eve_utils.copy_skel(project_name, 'win-svc', '.')

    subprocess.check_output([sys.executable, "-m", "pip", "install", 'PyInstaller>=3.6'])
    # also installs altgraph, future, pefile, pycparser, pyinstaller-hooks-contrib, pywin32-ctypes
    
    print('windows service class added')


if __name__ == '__main__':
    main()
