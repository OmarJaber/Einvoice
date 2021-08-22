# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in einvoice/__init__.py
from einvoice import __version__ as version

setup(
	name='einvoice',
	version=version,
	description='Einvoice',
	author='Omar',
	author_email='omar.ja93@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
