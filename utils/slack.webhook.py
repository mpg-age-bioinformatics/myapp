#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="Send data to a Slack webhook.")
parser.add_argument('-w', metavar="webhook", type=str, nargs='?', help="Webhook URL", required=True)
parser.add_argument('-s', metavar="subject", type=str, nargs='*', help="Message subject (required)", required=True)
parser.add_argument('-f', metavar="file", type=str, nargs='?', help="txt file to be sent as text.")
parser.add_argument("--short", metavar="type", type=str, nargs='?', choices=["nightly"] , default="nightly")
args = parser.parse_args()

import json
import requests

msg=" ".join(args.s)

slack_data_long={
    "text":  msg,
    "blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*"+msg+"*"
			}
		},
		{
			"type": "divider"
		}
    ]
}

if args.f :
    f = open( args.f , 'r')
    f = f.readlines()

    slack_data_long_file={
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": "".join(f)
        }
    }

    if args.short == "nightly" :
        summary=[ f[4], f[6] ]
        f = "".join(f)
        list_of_checks=[
            ":: build linux/amd64 myapp:nightly",
            ":: push linux/amd64 myapp:nightly" , 
            ":: build & push linux/arm64 myapp:nightly" ,
            ":: build linux/amd64 myapp-dockerize:nightly", 
            ":: push linux/amd64 myapp-dockerize:nightly",
            ":: build & push linux/arm64 myapp-dockerize:nightly"
        ]

        success=True
        for c in list_of_checks :
            if  c in f :
                summary.append(c+"\n")
            else:
                summary.append(c.replace(":: ", ":: !FAILED! ")+"\n")
                success=False

        summary="".join(summary)

        if success :
            msg=msg+" (success)"
        else:
            msg=msg+" (FAILED)"

        slack_data_long={
            "text":  msg,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*"+msg+"*"
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }
        
        slack_data_long_file={
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": summary
                }
            }
    slack_data_long["blocks"]=slack_data_long["blocks"]+[slack_data_long_file]

response = requests.post(
    args.w , data=json.dumps(slack_data_long),
    headers={'Content-Type': 'application/json'}
)

if response.status_code != 200:
    raise ValueError(
        'Request to slack returned an error %s, the response is:\n%s'
        % (response.status_code, response.text)
    )
