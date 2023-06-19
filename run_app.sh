#!/bin/bash

set -euo pipefail
set -x

docker run --rm -p 8999:8999 --gpus all comvis
