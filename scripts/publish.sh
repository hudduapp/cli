rm -r build dist

python setup.py sdist bdist_wheel --universal
twine upload dist/* -r pypi