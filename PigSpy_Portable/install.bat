@echo off
echo Installing PigSpy dependencies...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Error installing dependencies. Please check your Python installation.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.
echo To run PigSpy:
echo python main.py
echo.
pause