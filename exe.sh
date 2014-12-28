#!/bin/zsh

python src/main.py 10 1.0 1.0 20000 < ./kakaku_filtered.txt | sed -e 's/_.*-* / /'
