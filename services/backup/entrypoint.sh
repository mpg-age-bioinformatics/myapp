#!/bin/bash

ENV CRON_TIME="0 3 * * *"
MYSQL_HOST="mariadb"
MYSQL_PORT="3306"
TIMEOUT="30s"

touch /mysql_backup.log
touch /rsync.log
tail -F /mysql_backup.log /rsync.log &

while ! mysql --user=${MYSQL_USER} --password="${MYSQL_PASSWORD}" --host=${MYSQL_HOST} -e "use ${BUILD_NAME}"; 
do echo "Waiting for mysql.. " && sleep 4
done
echo "Found ${BUILD_NAME} db."

if [ "${INIT_BACKUP}" -gt "0" ]; 
then
    echo "=> Create a backup on the startup"
    /${BUILD_NAME}/services/backup/backup.sh
elif [ -n "${INIT_RESTORE_LATEST}" ]; 
then
    echo "=> Restore latest backup"
    until nc -z "$MYSQL_HOST" "$MYSQL_PORT"
        do
            echo "waiting database container..."
            sleep 1
    done
    find /backup/mariadb -maxdepth 1 -name 'latest.myapp.sql.gz' | tail -1 | xargs /${BUILD_NAME}/services/backup/restore.sh
fi

echo "${CRON_TIME} /${BUILD_NAME}/services/backup/backup.sh >> /mysql_backup.log 2>&1" > /crontab.conf
echo "${CRON_TIME} rsync -rtvh --delete /myapp_data/users/ /backup/users_data/ >> /rsync.log 2>&1" >> /crontab.conf
crontab /crontab.conf
echo "=> Running cron task manager"
# exec crond -f
service cron restart
tail -f /dev/null