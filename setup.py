from setuptools import setup, find_packages

setup(
    name="bixr",
    version="0.0.1",
    packages=find_packages(include=["bixr"]),
    install_requires=[
        "requests",
        "requests-cache",
    ],
    extras_require={
        "pandas": ["pandas"],
    },
)
