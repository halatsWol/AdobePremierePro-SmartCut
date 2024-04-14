@echo off

CALL "C:\ProgramData\Adobe\CEP\extensions\SmartCut\py\SmartCut_Venv\Scripts\activate.bat"

python "C:\ProgramData\Adobe\CEP\extensions\SmartCut\py\analyze.py"

CALL "C:\ProgramData\Adobe\CEP\extensions\SmartCut\pySmartCut_Venv\Scripts\deactivate.bat"

