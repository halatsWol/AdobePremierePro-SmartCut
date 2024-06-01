@echo off
CALL "C:\ProgramData\Marflow Software\SmartCut\py\SmartCut_Venv\Scripts\activate.bat"
CALL "cd /d D:\OneDrive\Documents\MarflowSoftware\SmartCut"
python "wsTest.py"
CALL "C:\ProgramData\Marflow Software\SmartCut\pySmartCut_Venv\Scripts\deactivate.bat"