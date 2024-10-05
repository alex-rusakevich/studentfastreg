$command = "pyenv"

if (Get-Command $command -ErrorAction SilentlyContinue) {
    Write-Host "$command exists in the shell"
} else {
    Write-Host "$command does not exist in the shell"
    Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
}

pyenv install "3.8.20"
pyenv shell "3.8.20"

python -m pip install pipenv
pipenv install
pipenv install --dev

inv build
