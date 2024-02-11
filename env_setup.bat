@echo off

set VENV_NAME=fit
set ENV_FILE=environment.yml

if not exist %VENV_NAME% (
    conda env create --name %VENV_NAME% --file %ENV_FILE%
)

call conda activate %VENV_NAME%

echo Environment setup complete.