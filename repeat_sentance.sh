#!/bin/bash

SENT="$@"

echo "$SENT" > x
> y

while read ln; do

    echo "$ln" | tr ' ' '\n'| tee dbg | xargs -i echo randsmall,{} >> y
done < x

#./run_set.sh x
