#!/bin/zsh

python src/main.py 10 1.0 1.0 2 < ./kakaku_filtered.txt | sed -e 's/_.*-* / /'
