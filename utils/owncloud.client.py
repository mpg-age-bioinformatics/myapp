#!/usr/bin/env python3

import argparse
parser = argparse.ArgumentParser(description="Add users and domains to private routes.")
parser.add_argument('-v', '--verbose', action="store_true")
parser.add_argument('--upload', metavar="<local_folders>", type=str, nargs='*', help="Upload files from folders.", default=["/mpcdf", "/submissions"])
parser.add_argument('--download', metavar="<local_folders>", type=str, nargs='*', help="Local folders to download files to.")
parser.add_argument('--target', metavar="<remote_folder>", type=str, nargs='*', help="Owncloud target folder.", default=["mpcdf_submissions", "age_submissions"] )
parser.add_argument('--config', metavar="<config_file>", type=str, nargs='?', help="Config file." )
args = parser.parse_args()

import owncloud
import os
import sys
from datetime import datetime
import traceback

if args.verbose :
    print( datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", "Started.")
    sys.stdout.flush()

if args.config:
    with open(args.config , "r") as fin:
        line=fin.readlines()[0].split("\n")[0].split(",")
    ADDRESS=line[0]
    USER=line[1]
    PASS=line[2]
else:
    ADDRESS=os.environ.get('OWNCLOUD_ADDRESS')
    USER=os.environ.get('OWNCLOUD_USER')
    PASS=os.environ.get('OWNCLOUD_PASS')


# upload
loggedin=False
if not args.download :
    dic=dict(zip( args.upload, args.target ))
    for folder in args.upload: 
        TARGET=dic[folder]
        files=os.listdir(folder)
        if ( files ) and ( not loggedin ):
            oc = owncloud.Client(ADDRESS)
            oc.login( USER, PASS )
            loggedin=True
        for f in files :
            try:     
                response=oc.put_file( os.path.join( TARGET, f ), os.path.join( folder, f ) )
                if response:
                    os.remove(os.path.join( folder, f ))
                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"Uploaded {f}")
                    sys.stdout.flush()
                else:
                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"Could not upload {f}")
                    sys.stdout.flush()
            except Exception as e :
                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", "-- ! EXCEPTION ! --", f, "|", e, traceback.format_exc())
            
    if loggedin:
        oc.logout()

# download
if args.download :
    oc = owncloud.Client(ADDRESS)
    oc.login( USER, PASS )
    dic=dict( zip( args.download, args.target ) )
    for folder in args.download: 
        TARGET=dic[folder]
        contents=oc.list( f'{TARGET}/' )
        for c in contents:
            c_name=c.get_name()
            if not os.path.isfile(os.path.join( folder, c_name )):
                try:
                    download=oc.get_file( os.path.join( TARGET, c_name ), local_file=os.path.join( folder, c_name ))
                    if download:
                        # print(c.get_path())
                        oc.delete( os.path.join( TARGET, c_name ) )
                        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"Downloaded {c_name}")
                        sys.stdout.flush()
                    else:
                        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"Could not download {c_name}")
                        sys.stdout.flush()
                except Exception as e :
                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", "-- ! EXCEPTION ! --", "|", e, traceback.format_exc())
            else:
                oc.delete( os.path.join( TARGET, c_name ) )
                print( datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"File already exists. Removed from source: {c_name}.")          
                sys.stdout.flush()
    oc.logout()
# print( datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", "Finished.")          
# sys.stdout.flush()
