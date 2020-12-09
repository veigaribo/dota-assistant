# dota-assistant

## How to run

To run this, it would be convenient to have Pipenv installed.

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

> If your installation fails, it is possible that you will need to update your setuptools:
>
> ```bash
> pip install -U setuptools
> ```

The next step would be to install the dependencies in `requirements.txt`:

```
pip install -r requirements.txt
```

> The reasons we use this instead of the Pipfile are
>
> 1. Apparently our dependencies have some inconsistency that makes the Pipfile impossible to lock, which is quite annoying;
> 2. It makes it much easier for people that don't use Pipenv to install the dependencies.

Then, it is very important that we download the Spacy language model we are going to use: `pt_core_news_md`.

```bash
python -m spacy download pt_core_news_md
```

> You could use another model as well, but then you would need to update `config.yml`

At some point, we will also need to create a `credentials.yml` file at the root of the project, containing the credentials for our bot. If you just want to try it out in the console, all you'll need will be something like:

```yaml
rest:
#  # you don't need to provide anything here - this channel doesn't
#  # require any credentials

# This entry is needed if you are using Rasa X. The entry represents credentials
# for the Rasa X "channel", i.e. Talk to your bot and Share with guest testers.
rasa:
  url: "http://localhost:5002/api"
```

Also, you will need Duckling running and accessible at `localhost:8000` (probably the easiest option to do that would be to run it using Docker)

Then, the bot must be trained:

```bash
rasa train
```

> If the `rasa` command isn't available in your PATH, you may use `python -m rasa` instead

And you should be able to start talking with:

```bash
rasa shell
```

However, it is very possible that the delay caused by OpenDota will be enough to sometimes trigger a timeout by default; so, you will probably want to set the `RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS` environment variable to a numeric value bigger than 20.

How to do it depends on your shell. In Bash, it would be:

```bash
RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS=30 rasa shell
```
