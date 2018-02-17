#!/bin/bash

function message() {
    echo "Watchdog: $1"
    $(dirname "$0")/pushover.sh -f "/home/max/.config/pushover.conf" "Watchdog: $1"
}

if curl --output /dev/null --silent --head --fail "http://localhost:8080"
then
    echo "Watchdog: Domoticz is running"
else
    message "Domoticz offline!!! Trying to start..."
    # doing restart is safer than start
    service domoticz.sh restart

    # wait couple secs 
    sleep 20

    if curl --output /dev/null --silent --head --fail "http://localhost:8080"
    then
        message "Domoticz is running back again!"
    fi
fi
