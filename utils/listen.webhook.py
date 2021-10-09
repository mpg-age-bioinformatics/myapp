from flask import Flask, request
from OpenSSL import SSL
import os
import json

filename = 'C:\\temp\\webhookPayloads.txt' #file that webhook payloads will be written

if os.path.exists(filename):
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
	if request.method == 'GET':
            return '<h1>Hello from Webhook Listener!</h1>'
	if request.method == 'POST':
            f = open(filename,append_write)
            req_data = request.get_json()
            str_obj = json.dumps(req_data)
            f.write(str_obj+'\n')
            f.close()
            return '{"success":"true"}'

if __name__ == "__main__":   
    context = ('ssl.cert', 'ssl.key') # certificate and key file. Cannot be self signed certs    
    app.run(host='0.0.0.0', port=5000, ssl_context=context, threaded=True, debug=True) # will listen on port 5000