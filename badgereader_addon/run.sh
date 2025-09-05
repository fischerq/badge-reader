#!/usr/bin/with-contenv bashio

bashio::log.info "NFC Badge Reader Addon starting..."

bashio::log.info "Workdir $PWD"

bashio::log.info "--- Start of server.py content ---"
bashio::log.info "$(cat /server.py)"
bashio::log.info "--- End of server.py content ---"

bashio::log.info "Hello1"

# Start the Python HTTP server
bashio::log.info "Starting Python HTTP server for badge messages..."
python3 /server.py
bashio::log.info "Hello2"

# If server.py exits, log it and keep container alive for debugging if needed,
# though ideally server.py runs forever.
bashio::log.warning "Python HTTP server exited."
#bashio::log.info "Container will sleep indefinitely to allow inspection if server exited unexpectedly."

# Loop forever to keep the container running if the python script exits
#while true; do
#  sleep 3600 # Sleep for an hour
#done
