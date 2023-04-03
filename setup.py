from setuptools import setup

setup(
    name="hcli",
    version="1.0.7",
    packages=["hcli", "hcli.commands", "hcli.api", "hcli.utils"],
    url="https://github.com/hudduapp/cli",
    install_requires=["typer", "rich", "huddu"],
    license="MIT",
    author="Joshua3212",
    author_email="hello@huddu.io",
    description="Official CLI for huddu.io",
    entry_points={
        'console_scripts': ['hcli=hcli.main:app']
    },
)
