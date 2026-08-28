@ECHO OFF
pushd %~dp0

set TARGET=%1
if "%TARGET%"=="" set TARGET=html
python build_bilingual.py %TARGET%
if errorlevel 1 exit /b 1

popd
