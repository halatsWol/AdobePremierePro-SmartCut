@echo off
call "%~dp0env_for_icons.bat" %*
rem cd/D "%WINPYWORKDIR1%"
rem "%WINPYDIR%\python.exe" -m winpython.controlpanel %*
if not "%WINPYWORKDIR%"=="%WINPYWORKDIR1%" cd/d %WINPYWORKDIR1%
cmd.exe /k "echo wppm & wppm"
