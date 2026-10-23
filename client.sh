#!/bin/bash
PROTOCOL=$1
RUN_ID=$2
LOSS_LABEL=$3
OUTPUT_CSV=$4

FILES=("small1.jpg" "small2.jpg" "small3.jpg" "medium.js" "large.mp4")

for FILE in "${FILES[@]}"; do
    RESULT=$(docker run --rm alpine/curl-http3 curl --$PROTOCOL -k -o /dev/null -s --resolve localhost:443:172.17.0.2 -w "%{http_version},%{time_total},%{time_starttransfer},%{size_download}" https://localhost/$FILE)
    echo "$PROTOCOL,$RUN_ID,$LOSS_LABEL,$FILE,$RESULT" >> $OUTPUT_CSV
done

echo "Run $RUN_ID complete for $PROTOCOL under $LOSS_LABEL"
