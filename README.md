gh-infra
========

1. Prepare environment

- Install `pyenv` + `direnv` first

```
> brew install pyenv
> brew install direnv
```
- Install python3.7.2 with pyenv

```
> pyenv install 3.7.2
```

- Install poetry for managing deps

```
> curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

- When u installed packages, just cd to ansible folder, direnv will autoload env
  or try to `poetry install` for getting all deps packages
