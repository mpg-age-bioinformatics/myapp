## UTILS
___
### deploys.sh

An utility for managing restarts and backups in production.
___

### slack.webhook.sh

Send data to a Slack webhook.
___
### Notes

`crontab -e`

```
* 0 * * * cd ~/myapp && git pull && cd ./services/server && ~/myapp/services/server/hooks/build nightly > ~/myapp/build.log 2>&1 ; ~/myapp/utils/slack.webhook.py -s "myapp nightly build" -f ~/myapp/build.log -w <slack webhook address>
```
___