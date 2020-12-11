#!/usr/bin/env python3

import os
import sys

import yaml


contents = {
    'action_endpoint': {
        'url': os.environ.get('ACTION_ENDPOINT_URL', 'http://localhost:5055/webhook')
    }
}

destination_path = os.path.join(
    os.path.dirname(__file__), '..', 'endpoints.yml')


def main():
    skip_check = '-y' in sys.argv

    if not skip_check and os.path.exists(destination_path):
        res = input(
            'There is a file called endpoints.yml already, override? (Yn) ')

        if res.strip().upper() != 'Y':
            print('Exiting')
            return

    with open(destination_path, 'w') as destination:
        yaml.dump(contents, destination)


if __name__ == '__main__':
    main()
