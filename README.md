Studentfastreg
===

Программа для ускорения регистрации в общежитиях Беларуси.

## Установка зависимостей для сборки

Для сборки проекта нужна программа `pyenv` (или же `pyenv-win` для Windows). Когда вы установите `pyenv`,
запустите следующие команды:

```sh
pyenv install 3.8.10
pyenv shell 3.8.10

python -m pip install pipenv
python -m pipenv install
python -m pipenv install --dev

python -m pipenv shell
inv build
```

Для запуска без сборки используйте команду `inv start`.

## Сборка .exe с нуля на Windows

Клонируйте репозиторий, перейдите в папку с ним и запустите следующую команду:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; .\build.ps1
```
