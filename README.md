# dota-assistant

## How to run

Due to several dependency version issues, it is strongly recommended to build this using the included Dockerfile.

In order to run in a container, an environment variable PORT must be provided at startup. See `docker-compose.yml` for more details.

### Running manually

If you want to edit the source code, you should have Pipenv installed.

If you have it, you'd start out by using

```bash
pipenv install -d
```

to install the dev-dependencies `pylint` and `autopep8` (optional), as well as creating your virtual environment for Python 3.8.

Then, if you are using Pipenv, you should run

```bash
pipenv shell
```

so you are using the correct Python and PIP executables.

Before advancing, you should ensure your PIP and setuptools versions work:

```bash
pip install -U pip==20.0.2
pip install -U setuptools==51.0.0
```

And the next step would be to install the dependencies in `requirements.txt`:

```
pip install -r requirements.txt
```

> The reasons we use this instead of the Pipfile are
>
> 1. Apparently our dependencies have some inconsistency that makes the Pipfile impossible to lock, which is quite annoying;
> 2. It makes it much easier for people that don't use Pipenv to install the dependencies.

> If you are going to manually create a virtualenv for this project, it would be convenient to name the directory `venv`, as it is already ignored by both Git and Docker.

After that, however, you will probably also have to overwrite some dependency versions, otherwise stuff might not work:

```bash
pip install -U sanic==20.9.1
pip install -U numpy==1.19.5
```

Then, it is very important that we download the Spacy language model we are going to use: `pt_core_news_md`.

```bash
python -m spacy download pt_core_news_md
```

> You could use another model as well, but then you would need to update `config.yml`

The bot must be trained:

```bash
rasa train
```

> If the `rasa` command isn't available in your PATH, you may use `python -m rasa` instead

And, providing the necessary environment variables, you should be able to start talking with:

```bash
rasa run actions
```

and

```bash
rasa shell
```

> See the `docker-compose.yml` file for the necessary environment variables. If you do not need them, you may edit the `credentials.yml` and `endpoints.yml` files.

However, it is very possible that the delay caused by OpenDota will be enough to sometimes trigger a timeout by default; so, you will probably want to set the `RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS` environment variable to a numeric value bigger than 20.

How to set an environment variable will vary according to your shell. In Bash, it would be:

```bash
RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS=30 rasa shell
```
