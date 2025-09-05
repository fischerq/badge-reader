#!/usr/bin/with-contenv bashio

bashio::log.info "NFC Badge Reader Addon starting..."

find . | bashio::log.info

# Start the Python HTTP server
bashio::log.info "Starting Python HTTP server for badge messages..."
python3 server.py

# If server.py exits, log it and keep container alive for debugging if needed,
# though ideally server.py runs forever.
bashio::log.warning "Python HTTP server exited."
bashio::log.info "Container will sleep indefinitely to allow inspection if server exited unexpectedly."

# Loop forever to keep the container running if the python script exits
while true; do
  sleep 3600 # Sleep for an hour
done
