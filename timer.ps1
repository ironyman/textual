pushd $psscriptroot

if (-not (Test-Path .\env)) {
python -m venv env
. env/scripts/activate.ps1
pip install .
} else {
. env/scripts/activate.ps1
}

$env:PYTHONPATH = "$psscriptroot\src\"

python $psscriptroot/docs/examples/tutorial/stopwatch.py
