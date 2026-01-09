cd C:\_rwey\python\LangoData\langodatarep\
python -m compileall src 
python setup.py sdist bdist_wheel
cd .\dist\ 
pip uninstall -y .\langodata-1.0.2-py3-none-any.whl
pip install .\langodata-1.0.2-py3-none-any.whl