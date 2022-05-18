#!/bin/bash

mkdir -p /backup/users_data /backup/mariadb

touch /backup/mysql_backup.log
touch /backup/rsync.log
tail -F /backup/mysql_backup.log /backup/rsync.log &

if mysql --user=${MYSQL_USER} --password="${MYSQL_PASSWORD}" --host=${MYSQL_HOST} -e "use ${DB_NAME}";
    then
        echo "Flaski database already exists."
    else

        while ! mysqladmin --user=root --password=${MYSQL_ROOT_PASSWORD} --host=${MYSQL_HOST} status ; 
            do 
                echo "Waiting for mysql.. " && sleep 4
        done

        if mysql --user=${MYSQL_USER} --password="${MYSQL_PASSWORD}" --host=${MYSQL_HOST} -e "use ${DB_NAME}";
            then
                echo "${BUILD_NAME} database already exists."
            else
                mysql --user=root --password=${MYSQL_ROOT_PASSWORD} --host=${MYSQL_HOST} << _EOF_
CREATE USER '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';
CREATE USER '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
CREATE DATABASE ${DB_NAME} /*\!40100 DEFAULT CHARACTER SET utf8 */;
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
_EOF_

                echo "mysql database created.."
        fi
    fi

if [[ "$RESTORE_DB" == "1" ]] ; 
    then
        tail -F /backup/mysql_backup.log /backup/rsync.log &
        echo "=> Restore latest backup"
        LATEST_BACKUP=$(find /backup/mariadb -maxdepth 1 -name "latest.${DB_NAME}.sql.gz" | tail -1 )
        if [ -f ${LATEST_BACKUP} ] ;
            then 
                echo "=> Restore database from ${LATEST_BACKUP}"
                set -o pipefail
                if gunzip --stdout "${LATEST_BACKUP}" | mysql -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}"
                    then
                        echo "=> Restore succeeded"
                    else
                        echo "=> Restore failed"
                fi
        else
            echo "=> No file to recover from."
        fi

fi

chown -R ${BUILD_NAME}:${BUILD_NAME} /${BUILD_NAME}_data /${BUILD_NAME}_data/users /var/log/${BUILD_NAME} /backup/mysql_backup.log /backup/rsync.log

sudo -i -u ${BUILD_NAME} bash << USER_EOF
if [[ "$RESTORE_USERS_DATA" == "1" ]] ; then
  rsync -rtvh /backup/users_data/ /${BUILD_NAME}_data/users/ >> /backup/rsync.log 2>&1
fi
USER_EOF

mysql --user=${MYSQL_USER} --password="${MYSQL_PASSWORD}" --host=${MYSQL_HOST} << _EOF_
USE ${DB_NAME}
DROP TABLE IF EXISTS alembic_version;
_EOF_

rm -rf migrations/* 
flask db init && flask db migrate -m "Initial migration." && flask db upgrade

chown -R ${BUILD_NAME}:${BUILD_NAME} /${BUILD_NAME}/migrations /var/log/${BUILD_NAME} /backup

exit