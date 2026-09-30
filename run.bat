@echo off
echo Checking for pygame and installing if necessary...
python -m pip install pygame
echo.
echo Starting the game...
python gui_main.py
pause