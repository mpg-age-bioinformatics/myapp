#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="Send data to a Slack webhook.")
parser.add_argument('-w', metavar="webhook", type=str, nargs='?', help="Webhook URL", required=True)
parser.add_argument('-s', metavar="subject", type=str, nargs='*', help="Message subject (required)", required=True)
parser.add_argument('-f', metavar="file", type=str, nargs='?', help="txt file to be sent as text.")
args = parser.parse_args()

import json
import requests

slack_data={'text': "### "+" ".join(args.s) }
if args.f :
    f = open( args.f , 'r')
    f = f.readlines()
    f = "".join(f)
    slack_data["attachments"] = [ {"text": f } ]

response = requests.post(
    args.w , data=json.dumps(slack_data),
    headers={'Content-Type': 'application/json'}
)
if response.status_code != 200:
    raise ValueError(
        'Request to slack returned an error %s, the response is:\n%s'
        % (response.status_code, response.text)
    )