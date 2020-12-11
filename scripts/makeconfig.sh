#!/bin/sh

DIR="$(dirname "$0")"

$DIR/makecredentials.py -y && $DIR/makeendpoints.py -y