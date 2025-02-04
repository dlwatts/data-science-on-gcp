#!/bin/bash

REGION='us-east1'
PROJECT=$(gcloud config get-value project)
BUCKET=ds-gcp-1

URL="https://${REGION}-${PROJECT}.cloudfunctions.net/ingest_flights_Dm29ClJgMKlVtfsR39E0vSSJKeFA4P3V"
TOKEN=changeme
echo {\"bucket\":\"${BUCKET}\", \"token\":\"${TOKEN}\"} > /tmp/message

gcloud pubsub topics create cron-topic
gcloud pubsub subscriptions create cron-sub --topic cron-topic

gcloud beta scheduler jobs create http monthlyupdate \
       --schedule="8 of month 10:00" \
       --uri=$URL \
       --max-backoff=7d \
       --max-retry-attempts=5 \
       --max-retry-duration=3h \
       --min-backoff=1h \
       --time-zone="US/Eastern" \
       --message-body-from-file=/tmp/message
