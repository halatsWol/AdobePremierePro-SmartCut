@echo off
CALL "C:\ProgramData\Marflow Software\SmartCut\py\SmartCut_Venv\Scripts\activate.bat"
python "C:\ProgramData\Marflow Software\SmartCut\py\analyze.py"
CALL "C:\ProgramData\Marflow Software\SmartCut\pySmartCut_Venv\Scripts\deactivate.bat"