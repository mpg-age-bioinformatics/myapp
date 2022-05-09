#!/bin/bash

echo "*/15 * * * * /${BUILD_NAME}/utils/owncloud.client.py > /owncloud.log 2>&1" > /${BUILD_NAME}_data/owncloud.cron
crontab /${BUILD_NAME}_data/owncloud.cron
rm /${BUILD_NAME}_data/owncloud.cron

tail -f /dev/null


