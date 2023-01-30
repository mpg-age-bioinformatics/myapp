#!/bin/bash
[ -z "${MYSQL_USER}" ] && { echo "=> MYSQL_USER cannot be empty" && exit 1; }
[ -z "${MYSQL_PASSWORD}" ] && { echo "=> MYSQL_PASS cannot be empty" && exit 1; }

[ -z "${BACKUP_PATH}" ] && BACKUP_PATH=/backup
[ -z "${LOGS_PATH_PREFIX}" ] && LOGS_PATH=/backup/


mkdir -p ${BACKUP_PATH}/users_data ${BACKUP_PATH}/mariadb

#### MYSQL

while ! mysql --user=${MYSQL_USER} --password="${MYSQL_PASSWORD}" --host=${MYSQL_HOST} -e "use ${DB_NAME}"; 
do echo "Waiting for mysql.. " && sleep 4
done
echo "Found ${DB_NAME} db."

DATE=$(date +%Y%m%d%H%M)
echo "=> Backup started at $(date "+%Y-%m-%d %H:%M:%S")"
DATABASES=${MYSQL_DATABASE:-${MYSQL_DB:-$(mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SHOW DATABASES;" | tr -d "| " | grep -v Database)}}
DB_COUNTER=0
for db in ${DATABASES}
do
  if [[ "$db" != "information_schema" ]] && [[ "$db" != "performance_schema" ]] && [[ "$db" != "mysql" ]] && [[ "$db" != _* ]]
  then
    echo "==> Dumping database: $db"
    FILENAME=${BACKUP_PATH}/mariadb/$DATE.$db.sql
    LATEST=${BACKUP_PATH}/mariadb/latest.$db.sql.gz
    if mysqldump -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --databases "$db" $MYSQLDUMP_OPTS > "$FILENAME"
    then
      gzip -f "$FILENAME"
      echo "==> Creating symlink to latest backup: $(basename "$FILENAME".gz)"
      rm "$LATEST" 2> /dev/null
      cd ${BACKUP_PATH}/mariadb && ln -s $(basename "$FILENAME".gz) $(basename "$LATEST") && cd - && \
      echo "${db}_backup_job $(date +%s)" > ${LOGS_PATH_PREFIX}${db}_backup_job.prom.$$ && \
      mv ${LOGS_PATH_PREFIX}${db}_backup_job.prom.$$ ${LOGS_PATH_PREFIX}${db}_backup_job.prom
      DB_COUNTER=$(( DB_COUNTER + 1 ))  
      ## generate prometheus report file
    else
      rm -rf "$FILENAME"
    fi
  fi
done

if [ -n "$MAX_BACKUPS" ]
then
  MAX_FILES=$(( MAX_BACKUPS * DB_COUNTER ))
  while [ "$(find ${BACKUP_PATH}/mariadb -maxdepth 1 -name "*.sql.gz" -type f | wc -l)" -gt "$MAX_FILES" ]
  do
    TARGET=$(find ${BACKUP_PATH}/mariadb -maxdepth 1 -name "*.sql.gz" -type f | sort | head -n 1)
    echo "==> Max number of backups ($MAX_BACKUPS) reached. Deleting ${TARGET} ..."
    rm -rf "${TARGET}"
    echo "==> Backup ${TARGET} deleted"
  done
fi


#### USERS DATA

#rsync -rtvh --delete /${BUILD_NAME}_data/users/ /backup/users_data/ >> /backup/rsync.log 2>&1

#chown -R ${BUILD_NAME}:${BUILD_NAME} /backup/users_data

set -o errexit
set -o nounset
set -o pipefail

readonly SOURCE_DIR="/${BUILD_NAME}_data/users/"
readonly BACKUP_DIR="${BACKUP_PATH}/users_data"
readonly DATETIME="$(date '+%Y%m%d_%H%M%S')"
readonly BACKUP_STAMP="${BACKUP_DIR}/${DATETIME}/"
readonly LATEST_LINK="${BACKUP_DIR}/latest"

mkdir -p "${BACKUP_DIR}"

if [ "$(find -L ${BACKUP_DIR} -name latest)" != "${LATEST_LINK}"  ] 
  then
    rsync -av --delete "${SOURCE_DIR}/" --exclude=".cache" "${BACKUP_STAMP}" && \
    echo "users_data_backup_job $(date +%s)" > ${LOGS_PATH_PREFIX}users_data_backup_job.prom.$$ && \
    mv ${LOGS_PATH_PREFIX}users_data_backup_job.prom.$$ ${LOGS_PATH_PREFIX}users_data_backup_job.prom
else
  rsync -av --delete \
    "${SOURCE_DIR}/" \
    --link-dest "${LATEST_LINK}" \
    --exclude=".cache" \
    "${BACKUP_STAMP}" && \
    echo "users_data_backup_job $(date +%s)" > ${LOGS_PATH_PREFIX}users_data_backup_job.prom.$$ && \
    mv ${LOGS_PATH_PREFIX}users_data_backup_job.prom.$$ ${LOGS_PATH_PREFIX}users_data_backup_job.prom
fi

rm -rf "${LATEST_LINK}"
ln -s "${BACKUP_STAMP}" "${LATEST_LINK}"

MAX_FOLDERS=30
while [ "$(find ${BACKUP_PATH}/users_data -maxdepth 1 -type d | wc -l)" -gt "$MAX_FOLDERS" ]
do
  TARGET=$(find ${BACKUP_PATH}/users_data -maxdepth 1 -type d | sort | head -n 1)
  echo "==> Max number of backups ($MAX_FOLDERS) reached. Deleting ${TARGET} ..."
  rm -rf "${TARGET}"
  echo "==> Backup ${TARGET} deleted"
done

echo "=> Backup process finished at $(date "+%Y-%m-%d %H:%M:%S")"
