## UTILS
___
### deploy.sh

An utility for managing restarts and backups in production.
___

### slack.webhook.sh

Send data to a Slack webhook.
___
### Notes

**Local nightly build crons:** 

`sudo crontab -u ${USER} -e`

- amd64

```
* 0 * * * export PATH=/usr/local/bin:/usr/bin:${PATH} && cd ~/myapp && git pull && cd ./services/server && ~/myapp/services/server/hooks/build nightly > ~/myapp/build.log 2>&1 ; ~/myapp/utils/slack.webhook.py -s "myapp nightly build - amd64 & arm64" -f ~/myapp/build.log -w <slack webhook address>
```
- aarch64

```
* 0 * * * export PATH=/usr/local/bin:/usr/bin:${PATH} && cd ~/myapp && git pull && cd ./services/server && ~/myapp/services/server/hooks/build aarch64 > ~/myapp/build.log 2>&1 ; ~/myapp/utils/slack.webhook.py -s "myapp nightly build - aarch64" -f ~/myapp/build.log --short  -w <slack webhook address>
```
___