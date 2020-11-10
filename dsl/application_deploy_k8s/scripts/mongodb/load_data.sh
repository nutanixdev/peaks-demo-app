#!/bin/bash

echo '@@{insert_script}@@'

printf 'db.peaks.insert(@@{insert_script}@@)' > /tmp/rawinsert.json

/bin/bash -c 'IFS="{" read -a INSERT < /tmp/rawinsert.json; for LINE in "${INSERT[@]}"; do printf "{$LINE\n"; done | sed -e "s/{db./db./"' > /tmp/demodbinsert.json 

cat /tmp/demodbinsert.json

mongo demodb < /tmp/demodbinsert.json

