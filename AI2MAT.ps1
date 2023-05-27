# Activate the virtual environment
$envPath = Join-Path $PSScriptRoot "env\Scripts\activate.ps1"
& $envPath

# Run the Python script
$scriptPath = Join-Path $PSScriptRoot "interface.py"
& python $scriptPath