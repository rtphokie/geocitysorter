#! /bin/zsh -x
pip install --force-reinstall  build
rm -rf dist
python3 -m build --wheel
pip install --force-reinstall dist/*whl
python3 -m twine upload --verbose --repository testpypi dist/*
#python3 -m twine upload --verbose --repository pypi dist/*
