# Omnicrobe Web interfaces

[![Python](https://img.shields.io/badge/python-3.7.6-brightgreen.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-1.1.2-brightgreen.svg)](https://flask.palletsprojects.com/en/2.0.x/quickstart/)
[![Flask_restx](https://img.shields.io/badge/flask_restx-0.2.0-brightgreen.svg)](https://flask-restx.readthedocs.io/en/latest/)
[![Psycopg2](https://img.shields.io/badge/psycopg2-2.8.6-brightgreen.svg)](https://pypi.org/project/psycopg2/)

## Source code

```bash
$ git clone git@forgemia.inra.fr:omnicrobe/omnicrobe_web.git
```

## How to run Omnicrobe?

### Configuration file

Before running the Omnicrobe application, it is necessary to modify the `config.yaml` configuration file with database connection information.

### Execution environment

```bash
$ python3 -m venv venv

$ . venv/bin/activate

$ pip install Flask
$ pip install psycopg2
$ pip install flask-restx

$ export FLASK_APP=__init__.py
$ export FLASK_ENV=development
```

### Workflow execution

```bash
$ flask run
```
