#!/usr/bin/env bash
# shellcheck shell=bash

set -euo pipefail

echo "ADOP repo smoke example"
test -f pyproject.toml
test -f package.json
