#!/bin/sh
set -u

INTERVAL="${SCRAPE_INTERVAL:-21600}"

while true; do
    echo "$(date -Iseconds) Starting scraper run..."
    if concert-checker; then
        echo "$(date -Iseconds) Scraper run completed successfully."
    else
        echo "$(date -Iseconds) Scraper run failed (exit $?), will retry next cycle." >&2
    fi
    echo "$(date -Iseconds) Sleeping ${INTERVAL}s until next run."
    sleep "$INTERVAL"
done
