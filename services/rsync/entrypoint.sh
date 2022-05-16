#!/bin/bash

if [ -e /${BUILD_NAME}/.owncloud.flaski  ] ; 

    then

        echo "*/15 * * * * /${BUILD_NAME}/utils/owncloud.client.py --config /${BUILD_NAME}/.owncloud.flaski > /owncloud.log 2>&1" > /${BUILD_NAME}_data/owncloud.cron
        crontab /${BUILD_NAME}_data/owncloud.cron
        rm /${BUILD_NAME}_data/owncloud.cron

    else

        echo "*/15 * * * * /${BUILD_NAME}/utils/owncloud.client.py > /owncloud.log 2>&1" > /${BUILD_NAME}_data/owncloud.cron
        crontab /${BUILD_NAME}_data/owncloud.cron
        rm /${BUILD_NAME}_data/owncloud.cron

fi

tail -f /dev/null


