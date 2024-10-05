# Set-ExecutionPolicy Bypass -Scope Process -Force; .\build.ps1

function refreshenv {
	$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") 
}

$command = "pyenv"

if (Get-Command $command -ErrorAction SilentlyContinue) {
    Write-Host "$command exists in the shell"
} else {
    Write-Host "$command does not exist in the shell"
    Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
	Remove-Item "./install-pyenv-win.ps1" -Force -Confirm:$false
}

refreshenv

pyenv install "3.8.10"
pyenv shell "3.8.10"

python -m pip install pipenv
python -m pipenv install
python -m pipenv install --dev

pipenv run inv build
explorer .\dist
