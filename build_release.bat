@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=C:\Users\Hadi Karimi\AppData\Local\Programs\Python\Python314\python.exe"
set "OUT=%~dp0Release"

echo ==========================================
echo        Ping Monitor - Release Build
echo ==========================================
echo.

if not exist "%PYTHON%" (
    echo Python executable not found:
    echo %PYTHON%
    pause
    exit /b 1
)

"%PYTHON%" -m pip install --upgrade pyinstaller customtkinter
if errorlevel 1 goto :error

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "%OUT%\Ping Monitor.exe" del /q "%OUT%\Ping Monitor.exe"
if exist "Ping Monitor.spec" del /q "Ping Monitor.spec"

"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "Ping Monitor" ^
   --icon "%~dp0PingMonitor.ico" ^
   --add-data "%~dp0PingMonitor.ico;." ^
  --distpath "%OUT%" ^
  main.py

if errorlevel 1 goto :error

echo.
echo ==========================================
echo BUILD COMPLETE!
echo.
echo Release folder:
echo %OUT%
echo ==========================================
pause
exit /b 0

:error
echo.
echo BUILD FAILED.
pause
exit /b 1
