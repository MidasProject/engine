@echo off
setlocal enabledelayedexpansion

REM Check if python3.13 is in PATH
for /f "delims=" %%p in ('where python3.13 2^>nul') do set PYTHON=%%p

REM If not found, manually set the path
if not defined PYTHON if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe" (
    set PYTHON=%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe
)

REM If still not found, try the general "python" command
if not defined PYTHON for /f "delims=" %%p in ('where python 2^>nul') do set PYTHON=%%p

REM Exit if Python is not found
if not defined PYTHON (
    echo [ERROR] Python 3.13 or any Python is not found.
    timeout /t 5 /nobreak >nul
    exit /b 1
)

echo Using Python: %PYTHON%
echo.
%PYTHON% --version

REM Move to the directory of this script
cd /d %~dp0

REM ---------------------------------------------------------------
set VENV_NAME=.venv

REM Check if virtual environment already exists
if exist %VENV_NAME% (
    echo [WARNING] Virtual environment %VENV_NAME% already exists.
    set /p "choice=Do you want to recreate it? (y/N): "
    if /i "!choice!"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q %VENV_NAME%
    ) else (
        echo Keeping existing virtual environment.
        goto ACTIVATE
    )
)

REM Create and set up venv
echo Setting up %VENV_NAME%...
%PYTHON% -m venv %VENV_NAME%
if errorlevel 1 (
    echo [ERROR] Failed to create %VENV_NAME%. Ensure Python 3.13 is installed and accessible.
    timeout /t 5 /nobreak >nul
    exit /b 1
)

:ACTIVATE
REM Activate venv
call %VENV_NAME%\Scripts\activate
if errorlevel 1 (
    echo [ERROR] Failed to activate %VENV_NAME%. Check if the venv was created properly.
    timeout /t 5 /nobreak >nul
    exit /b 1
)

REM Upgrade pip, setuptools, wheel
echo Upgrading pip setuptools wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip setuptools wheel.
    timeout /t 5 /nobreak >nul
    exit /b 1
)

@REM REM Install PyTorch
@REM echo Checking CUDA installation...
@REM if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8" (
@REM     set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8
@REM     set CUDA_VERSION=11.8
@REM )
@REM else (
@REM     echo [WARNING] CUDA not found. Skipping Pytorch installation.
@REM     goto ACTIVATE2
@REM )

@REM echo Installing PyTorch dependencies...
@REM pip install torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/cu118
@REM if errorlevel 1 (
@REM     echo [ERROR] Failed to install PyTorch and its dependencies. Ensure the correct CUDA version and internet connection.
@REM     timeout /t 5 /nobreak >nul
@REM     exit /b 1
@REM )

@REM REM Set up CUDA environment variables if CUDA is installed
@REM echo Setting up CUDA environment variables...

@REM REM Append CUDA environment variables to activate.bat
@REM echo Adding CUDA environment variables to activate.bat...
@REM (
@REM     echo set CUDA_HOME=%CUDA_PATH%
@REM     echo set PATH=%%CUDA_HOME%%\bin;%%PATH%%
@REM     echo set LD_LIBRARY_PATH=%%CUDA_HOME%%\lib64;%%LD_LIBRARY_PATH%%
@REM ) >> %VENV_NAME%\Scripts\activate.bat

@REM REM Append CUDA environment variables to Activate.ps1
@REM echo Adding CUDA environment variables to Activate.ps1...

@REM REM Define the file paths
@REM set "ps1File=%VENV_NAME%\Scripts\Activate.ps1"
@REM set "tempFile=%VENV_NAME%\Scripts\Activate_temp.ps1"
@REM set "backupFile=%VENV_NAME%\Scripts\Activate_original.ps1"

@REM REM Backup the original Activate.ps1 file
@REM copy /Y "%ps1File%" "%backupFile%" >nul

@REM REM Process the original Activate.ps1 line by line
@REM (
@REM     for /f "usebackq delims=" %%A in ("%ps1File%") do (
@REM         set "line=%%A"
@REM         echo !line! | findstr /b /c:"# SIG # Begin signature block" >nul
@REM         if !errorlevel! == 0 (
@REM             echo $env:CUDA_HOME = "%CUDA_PATH%"
@REM             echo $env:PATH = "$env:CUDA_HOME\bin;$env:PATH"
@REM             echo $env:LD_LIBRARY_PATH = "$env:CUDA_HOME\lib64;$env:LD_LIBRARY_PATH"
@REM         )
@REM         echo !line!
@REM     )
@REM ) > "%tempFile%"

@REM REM Replace the original Activate.ps1 with the modified file
@REM move /y "%tempFile%" "%ps1File%" >nul
@REM echo Finished adding CUDA environment variables to Activate.ps1

@REM :ACTIVATE2
REM Install remaining dependencies
echo Installing remaining dependencies from pyproject.toml...
echo.
pip install -e . --no-cache-dir
if errorlevel 1 (
    echo [ERROR] Failed to install some dependencies. Check pyproject.toml and your internet connection.
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo All dependencies installed successfully!
echo .
timeout /t 5 /nobreak

REM Deactivate .venv
echo Deactivating %VENV_NAME%...
echo.
timeout /t 3 /nobreak
call deactivate
if errorlevel 1 (
    echo [ERROR] Failed to deactivate %VENV_NAME%.
    timeout /t 5 /nobreak >nul
    exit /b 1
)

echo %VENV_NAME% has been successfully set up!
timeout /t 5 /nobreak >nul

REM Only pause if the script is executed by double-clicking
if "%cmdcmdline%"=="%~0" pause

exit /b 0
