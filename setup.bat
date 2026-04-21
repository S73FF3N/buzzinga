@echo off
setlocal enabledelayedexpansion

echo.
echo === Buzzinga Setup ===
echo.

:: Check for uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv is not installed. You need it for this setup.
    echo Install it from: https://docs.astral.sh/uv/getting-started/installation/
    echo.
    echo The quickest way ^(run in PowerShell^):
    echo   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    pause
    exit /b 1
)

:: Ask where to install
set "DEFAULT_DIR=%USERPROFILE%\Desktop\Buzzinga"
echo Where do you want to install Buzzinga?
set /p "INSTALL_DIR=Press Enter for default (%DEFAULT_DIR%) or type a path: "
if "%INSTALL_DIR%"=="" set "INSTALL_DIR=%DEFAULT_DIR%"

if exist "%INSTALL_DIR%" (
    echo.
    echo The folder %INSTALL_DIR% already exists.
    set /p "OVERWRITE=Overwrite? (y/N): "
    if /i not "!OVERWRITE!"=="y" (
        echo Setup cancelled.
        pause
        exit /b 0
    )
)

echo.
echo Building Buzzinga... (this may take a minute the first time)
echo.

:: Build the executable
uv run pyinstaller launcher.py --onefile --add-data "src/buzzinga/staticfiles;staticfiles" --name buzzinga --paths src --log-level WARN
if %errorlevel% neq 0 (
    echo.
    echo Build failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Setting up your game folder...

:: Create install directory and data subfolders
mkdir "%INSTALL_DIR%\data\images" 2>nul
mkdir "%INSTALL_DIR%\data\sounds" 2>nul
mkdir "%INSTALL_DIR%\data\hints" 2>nul
mkdir "%INSTALL_DIR%\data\questions" 2>nul
mkdir "%INSTALL_DIR%\data\who-knows-more" 2>nul

:: Copy executable
copy /y "dist\buzzinga.exe" "%INSTALL_DIR%\buzzinga.exe" >nul

echo.
echo === Done! ===
echo.
echo Buzzinga is installed at: %INSTALL_DIR%
echo.
echo To play, double-click 'buzzinga.exe' in that folder.
echo.
echo Don't forget to add your quiz content to the data\ folder!
echo See the README for details on game data formats.
echo.
pause
