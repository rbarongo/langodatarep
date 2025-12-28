cd C:\_rwey\pers\PDP\MSC\UDSM\shule\Semester I\IS671_Py\mycodes\mycodes\MSPUsersDev\
python -m compileall .
python setup.py sdist bdist_wheel
cd .\dist\ 
pip uninstall -y .\utils-1.0.1-py3-none-any.whl
pip install .\utils-1.0.1-py3-none-any.whl