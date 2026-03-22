#!/bin/bash

SENT="$@"

tmpx=$(mktemp /tmp/repeat_sentance_x.XXXXXXXXX)
tmpy=$(mktemp /tmp/repeat_sentance_y.XXXXXXXXX)
trap 'rm -f "$tmpx" "$tmpy"' EXIT

echo "$SENT" > "$tmpx"

while read ln; do
    echo "$ln" | tr ' ' '\n' | xargs -I '{}' echo randsmall,{} >> "$tmpy"
done < "$tmpx"

#./run_set.sh "$tmpy"
