#!/usr/bin/env python
"""Adds web socket functionality to API

Usage:
    add_web_socket [-h|--help] api_name
      NOTE: Run this in the folder above the API project folder

Examples:
    add_web_socket my-api

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
import sys
import argparse
from distutils.dir_util import copy_tree

import eve_utils

def add_web_socket():
    print(f'Adding web socket to API')

    skel = os.path.join(os.path.dirname(eve_utils.__file__), 'skel/web_socket')

    copy_tree(skel, '.')
    
    eve_utils.install_packages(['Flask-SocketIO'], 'add_web_socket')
    


def main():
    parser = argparse.ArgumentParser('add_web_socket', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    args = parser.parse_args()
    
    if not os.path.exists('./requirements.txt'):
        print('requirements.txt missing - must be run in the API folder')
        quit(1)
        
    if not os.path.exists('./domain'):
        print('domain folder missing - must be run in the API folder')
        quit(2)
        
    if os.path.exists('./web_socket'):
        print('web_socket folder already exists')
        quit(3)

    
    add_web_socket()


if __name__ == '__main__':
    main()
