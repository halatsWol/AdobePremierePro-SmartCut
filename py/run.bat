@echo off

CALL "SmartCut_Venv\Scripts\activate.bat"

python "analyze.py"

CALL "SmartCut_Venv\Scripts\deactivate.bat"

