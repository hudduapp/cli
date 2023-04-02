from setuptools import setup

setup(
    name="huddu-cli",
    version="1.0.0",
    packages=["huddu-cli"],
    url="https://github.com/hudduapp/cli",
    requires=["typer", "rich", "huddu"],
    license="MIT",
    author="Joshua3212",
    author_email="hello@huddu.io",
    description="Official CLI for huddu.io",
)
