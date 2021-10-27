# -*- coding: utf-8 -*-
import re

from setuptools import setup

with open("django_dburl.py", "r") as src:
    version = re.match(r'.*__version__ = "(.*?)"', src.read(), re.S).group(1)

with open("README.md") as readme_md:
    readme = readme_md.read()

setup(
    name="django-dburl",
    version=version,
    url="https://github.com/imsweb/django-dburl",
    license="BSD",
    author="Dan Watson",
    author_email="watsond@imsweb.com",
    description="Use Database URLs in your Django Application.",
    long_description=readme,
    long_description_content_type="text/markdown",
    py_modules=["django_dburl"],
    install_requires=["Django>=2.0"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
