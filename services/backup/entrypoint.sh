#!/bin/bash

# CRON_TIME="0 3 * * *"
# MYSQL_HOST="mariadb"
# MYSQL_PORT="3306"
TIMEOUT="30s"

mkdir -p /backup/users_data /backup/mariadb

touch /backup/mysql_backup.log
touch /backup/rsync.log
tail -F /backup/mysql_backup.log /backup/rsync.log &

while ! mysql --user=${MYSQL_USER} --password="${MYSQL_PASSWORD}" --host=${MYSQL_HOST} -e "use ${DB_NAME}"; 
do echo "Waiting for mysql.. " && sleep 4
done
echo "Found ${DB_NAME} db."

# RESTORES NO LONGER TAKE PLACE FROM THE BACKUP CONTAINER
# if [ "${INIT_BACKUP}" == "1" ] ; 
# then
#     echo "=> Create a backup on the startup"
#     /${BUILD_NAME}/services/backup/backup.sh
# elif [ -n "${INIT_RESTORE_LATEST}" ] ; 
# then
#     echo "=> Restore latest backup"
#     until nc -z "$MYSQL_HOST" "$MYSQL_PORT"
#         do
#             echo "waiting database container..."
#             sleep 1
#     done
#     find /backup/mariadb -maxdepth 1 -name 'latest.${DB_NAME}.sql.gz' | tail -1 | xargs /${BUILD_NAME}/services/backup/restore.sh
# fi

echo "${CRON_TIME} /${BUILD_NAME}/services/backup/backup.sh >> /backup/mysql_backup.log 2>&1" > /crontab.conf
# echo "${CRON_TIME} rsync -rtvh --delete /myapp_data/users/ /backup/users_data/ >> /backup/rsync.log 2>&1" >> /crontab.conf
crontab /crontab.conf
echo "=> Running cron task manager"
# exec crond -f
service cron restart
tail -f /dev/null