#!/usr/bin/env python

import os
import sys
import argparse

LOCAL_SYNC_DIR  = os.path.join(os.path.dirname(__file__), "data")
S3_BUCKET       = "rss"

parser = argparse.ArgumentParser()
parser.add_argument("--aws-profile", type=str, help="aws cli --profile variable")
parser.add_argument("--aws-endpoint-url", type=str, help="aws cli --endpoint-url variable")
parser.add_argument("--local-sync-dir",  type=str, default=LOCAL_SYNC_DIR, help="rss output dir(default: {0})".format(LOCAL_SYNC_DIR))
parser.add_argument("--s3-bucket",type=str, default=S3_BUCKET,  help="s3 bucket name(default: {})".format(S3_BUCKET))
args = parser.parse_args()

def main():
    argv = [ "aws", "s3", "sync", "--delete" ]
    if args.aws_profile:
        argv.extend([ "--profile", args.aws_profile ])
    if args.aws_endpoint_url:
        argv.extend([ "--endpoint-url", args.aws_endpoint_url ])
    argv.extend([ args.local_sync_dir, "s3://{0}/".format(args.s3_bucket) ])
    os.execvp("aws", argv)

if __name__ == "__main__":
    main()
