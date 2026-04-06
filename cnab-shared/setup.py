"""Installation configuration for the cnab-shared package."""

from setuptools import find_packages, setup

setup(
    name="cnab-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.9",
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
        "cryptography>=42.0.0",
    ],
)
