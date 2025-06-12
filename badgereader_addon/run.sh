#!/usr/bin/with-contenv bashio

bashio::log.info "NFC Badge Reader Addon starting..."

# The addon itself doesn't run a separate server.
# Home Assistant Core loads the custom component.
# This script just needs to keep the container running.
# Loop forever, printing a message periodically.
while true; do
  bashio::log.debug "NFC Badge Reader Addon is running..."
  sleep 3600 # Sleep for an hour
done
