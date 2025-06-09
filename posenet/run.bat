@echo off
cd /d %~dp0
call conda activate posenet
python src\main.py
pause
