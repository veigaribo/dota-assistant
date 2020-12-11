#!/usr/bin/env python3

import os
import sys

import yaml


contents = {
    'rest': {},

    # This entry is needed if you are using Rasa X. The entry represents credentials
    # for the Rasa X "channel", i.e. Talk to your bot and Share with guest testers.
    'rasa': {
        'url': os.environ.get('RASA_X_URL', 'http://localhost:5002/api'),
    },

    'telegram': {
        'access_token': os.environ.get('TELEGRAM_ACCESS_TOKEN', ''),
        'verify': os.environ.get('TELEGRAM_VERIFY', ''),
        'webhook_url': os.environ.get('TELEGRAM_WEBHOOK_URL', ''),
    }
}

destination_path = os.path.join(
    os.path.dirname(__file__), '..', 'credentials.yml')


def main():
    skip_check = '-y' in sys.argv

    if not skip_check and os.path.exists(destination_path):
        res = input(
            'There is a file called credentials.yml already, override? (Yn) ')

        if res.strip().upper() != 'Y':
            print('Exiting')
            return

    with open(destination_path, 'w') as destination:
        yaml.dump(contents, destination)


if __name__ == '__main__':
    main()
