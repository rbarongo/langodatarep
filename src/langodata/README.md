#running these files: pip install -r requirements.txt
cryptography==39.0.1
python-dotenv==0.21.0
pandas==1.5.3
oracledb==2.0.0  # Adjust according to the version you're using for Oracle DB


#how to run your code
#Step 1: Activate your venv
cd C:\_rwey\python\LangoData\langodatarep
langodataenv\Scripts\activate 

#Step 2: Run your app
(langodataenv) PS C:\_rwey\python\LangoData\langodatarep> python -m langodata.main

#Install Pytest
(langodataenv) PS C:\_rwey\python\LangoData\langodatarep> pip install pytest
python -m pytest




PS C:\_rwey\python\LangoData\langodatarep> & C:/_rwey/python/LangoData/langodatarep/langodataenv/Scripts/Activate.ps1     
(langodataenv) PS C:\_rwey\python\LangoData\langodatarep> & C:/_rwey/python/LangoData/langodatarep/langodataenv/Scripts/python.exe c:/_rwey/python/LangoData/langodatarep/scripts/msp_user.py
Manual test output:
{'id': 1, 'value': 'alpha'}
{'id': 2, 'value': 'beta'}
{'id': 3, 'value': 'gamma'}
(langodataenv) PS C:\_rwey\python\LangoData\langodatarep> 