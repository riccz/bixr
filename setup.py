import io
import os
import re

from setuptools import find_packages, setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    name="bixr",
    version="0.0.1",
    url="https://github.com/riccz/bixr",
    license="MIT",
    author="Riccardo Zanol",
    author_email="ricc@zanl.eu",
    description="Exchange rate API from Banca d'Italia",
    long_description=read("README.rst"),
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "requests",
        "requests-cache",
    ],
    extras_require={
        "pandas": ["pandas"],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
