#!/bin/sh

DIR="$(dirname "$0")"

$DIR/makeconfig.sh && python -m rasa run