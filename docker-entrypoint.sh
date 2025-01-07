#!/bin/sh
set -e  # Exit on any error

# This script starts the `main.py` application

PROGNAME=$(basename $0)  # Get the script name
USER="astragateway"      # Default user
GROUP="astragateway"     # Default group
PYTHON="/opt/venv/bin/python"  # Path to Python executable in the virtual environment
WORKDIR="src/astragateway"     # Application working directory
STARTUP="$PYTHON main.py $@"   # Command to start the application

# Log the startup command
echo "$PROGNAME: Starting $STARTUP"

# Check if the script is running as root
if [ "$(id -u)" = '0' ]; then
    # If running as root, change ownership of files and step down to the specified user
    find . ! -type l ! -user ${USER} -exec chown ${USER}:${GROUP} '{}' +
    find ../astracommon ! -type l ! -user ${USER} -exec chown ${USER}:${GROUP} '{}' +

    # Change to the working directory
    cd ${WORKDIR}

    # Enable core dump collection if the environment variable is set
    if [ "${BLXR_COLLECT_CORE_DUMP}" = "1" ] || [ "${BLXR_COLLECT_CORE_DUMP}" = "true" ]; then
        echo "Enabling core dump collection..."
        ulimit -c unlimited  # Remove core file size limit
        mkdir -p /var/crash
        echo /var/crash/core.%e.%p.%h.%t > /proc/sys/kernel/core_pattern
    fi

    # Run the application as the specified user
    exec su-exec ${USER} ${STARTUP}
else
    # If not running as root, allow the container to start with a non-root user
    cd ${WORKDIR}
    exec ${STARTUP}
fi
