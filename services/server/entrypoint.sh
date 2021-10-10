#!/bin/bash

while ! mysql --user=${MYSQL_USER} --password="${MYSQL_PASSWORD}" --host=${MYSQL_HOST} -e "use ${BUILD_NAME}"; 
  do 
    echo "Waiting for mysql.. " && sleep 4
done
echo "Found ${BUILD_NAME} db."


if [[ "$FLASK_ENV" == "production" ]] ; 
  then
    gunicorn -b 0.0.0.0:8000 --timeout 60000 -w 4 ${BUILD_NAME}:app
  elif [[ "$FLASK_ENV" == "development" ]] ; 
  then
    /myapp/utils/getenv.sh
    tail -f /dev/null
fi


# ## needs to be finished, this is for the managment containter
# if [[ "$FLASK_ENV" == "mngt" ]]

#   echo "0 0 1,15 * * python3 /myapp/myapp.py > /clean.cycshare.out 2>&1" > /cron.job && crontab /cron.job

# fi

