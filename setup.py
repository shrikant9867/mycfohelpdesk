# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='help_desk',
    version=version,
    description='App For Managing issues related to employees',
    author='Indictrans',
    author_email='jitendra.k@indictranstech.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
