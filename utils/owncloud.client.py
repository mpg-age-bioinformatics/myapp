#!/usr/bin/env python3

import argparse
import os
import sys
import traceback
from datetime import datetime
from nc_py_api import Nextcloud

# --- Argument parsing ---
parser = argparse.ArgumentParser(description="Add users and domains to private routes.")
parser.add_argument('-v', '--verbose', action="store_true")
parser.add_argument('--upload', metavar="<local_folders>", type=str, nargs='*', help="Upload files from folders.", default=["/mpcdf", "/submissions"])
parser.add_argument('--download', metavar="<local_folders>", type=str, nargs='*', help="Local folders to download files to.")
parser.add_argument('--target', metavar="<remote_folder>", type=str, nargs='*', help="Owncloud/Nextcloud target folder.", default=["mpcdf_submissions", "age_submissions"])
parser.add_argument('--config', metavar="<config_file>", type=str, nargs='?', help="Config file.")
args = parser.parse_args()

# --- Config ---
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

nc = Nextcloud(nextcloud_url=ADDRESS, nc_auth_user=USER, nc_auth_pass=PASS)

# --- Upload ---
if not args.download:
    mapping = dict(zip(args.upload, args.target))
    for local_folder in args.upload:
        remote_folder = mapping[local_folder]
        if not os.path.isdir(local_folder):
            continue
        for filename in os.listdir(local_folder):
            local_path = os.path.join(local_folder, filename)
            remote_path = f"/{remote_folder}/{filename}"

            try:
                with open(local_path, "rb") as fp:
                    nc.files.upload_stream(remote_path, fp, chunk_size=50*1024*1024)
                os.remove(local_path)
                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"Uploaded {filename}")
                sys.stdout.flush()
            except Exception as e:
                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", "-- ! EXCEPTION ! --", filename, "|", e)
                traceback.print_exc()

# --- Download ---
if args.download:
    mapping = dict(zip(args.download, args.target))
    for local_folder in args.download:
        remote_folder = mapping[local_folder]
        os.makedirs(local_folder, exist_ok=True)

        try:
            entries = nc.files.listdir(f"/{remote_folder}")
        except Exception as e:
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"Failed to list /{remote_folder}", "|", e)
            continue

        for entry in entries:
            filename = entry.name
            local_path = os.path.join(local_folder, filename)
            remote_path = f"/{remote_folder}/{filename}"

            try:
                if not os.path.isfile(local_path):
                    with open(local_path, "wb") as f_out:
                        nc.files.download2stream(remote_path, f_out)
                    nc.files.delete(remote_path)
                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"Downloaded {filename}")
                else:
                    nc.files.delete(remote_path)
                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", f"File already exists. Removed from source: {filename}")
                sys.stdout.flush()
            except Exception as e:
                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "|", "-- ! EXCEPTION ! --", "|", e)
                traceback.print_exc()
                sys.stdout.flush()
