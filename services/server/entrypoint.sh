#!/bin/bash

while ! mysql --user=${MYSQL_USER} --password="${MYSQL_PASSWORD}" --host=${MYSQL_HOST} -e "use ${DB_NAME}"; 
  do 
    echo "Waiting for mysql.. " && sleep 4
done
echo "Found ${DB_NAME} db."


if [[ "$FLASK_ENV" == "production" ]] ; 
  then
    if [[ "$SCRIPT_NAME" != "" ]] ;
      then
        echo "prefix: $SCRIPT_NAME"
        SCRIPT_NAME=/${SCRIPT_NAME} gunicorn -b 0.0.0.0:8000 --timeout 60000 -w ${N_WORKERS} ${BUILD_NAME}:app
      else
        gunicorn -b 0.0.0.0:8000 --timeout 60000 -w ${N_WORKERS} ${BUILD_NAME}:app
      fi
elif [[ "$FLASK_ENV" == "development" ]] ; 
  then
    # if [[ "${UPGRADE_REQS}" = "yes" ]] ;
      # then
        /${BUILD_NAME}/utils/getenv.sh
    # fi

    tail -f /dev/null
fi


# ## needs to be finished, this is for the managment containter
# if [[ "$FLASK_ENV" == "mngt" ]]

#   echo "0 0 1,15 * * python3 /myapp/myapp.py > /clean.cycshare.out 2>&1" > /cron.job && crontab /cron.job

# fi

