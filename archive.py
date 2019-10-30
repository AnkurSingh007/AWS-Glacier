#! /usr/bin/env python3
import os
import sys
import logging
import tarfile
import hashlib
import argparse
import subprocess
from functools import lru_cache
import boto3
import csv
from datetime import datetime


logging.basicConfig(filename='log.txt',
                    level=logging.DEBUG,
                    format='%(asctime)s    %(levelname)s    %(message)s')
parser = argparse.ArgumentParser(description='Archive files and directories.')
glacier = boto3.resource('glacier')
default_file_name = 'sample.tar.gz'
buffer_size = 4096
split_size = '2M'
default_suffix = 'multipart_upload'
vault_name = 'glacier_vault'
account_id = '-'
archive_db_file_path = ''


@lru_cache(maxsize=1)
def get_commandline_args():
    parser.add_argument('file_list', nargs = '+', action = 'store', help = 'A list of path of files and/or directories')
    parser.add_argument('--archive_name', action = 'store', help = 'Name to be used for the archieved file')
    args = parser.parse_args()
    return args


def get_archive_candidate_list():
    commandline_args = get_commandline_args()
    candidate_list = commandline_args.list
    if len(candidate_list) == 0:
      logging.error('No filename or directory name is provided in the argument list.')
      sys.exit()
    return candidate_list


def filter_archive_candidate_list(candidate_list):
    filtered_list = []
    for candidate in candidate_list:
      if not os.path.exists(candidate):
        logging.warning('{} not found'.format(candidate))
      else:
        filtered_list.append(candidate)
    return filtered_list


def create_archive(candidate_list, file_name):
    # Create a tar file in the same directory of this script.
    filtered_list = filter_archive_candidate_list(candidate_list)
    with tarfile.open(file_name, 'w:gz') as tar:
      for candidate in filtered_list:
        tar.add(candidate)
        logging.debug("{} archive success".format(candidate))
    return file_name


def upload_archive(file_list):
    responses = []
    vault = glacier.Vault(account_id, vault_name)
    for f in file_list:
        with open(f, mode='rb') as upload_file:
            response = vault.upload_archive(body=upload_file)
            if not response:
                logging.warning("Could not upload the file {}.", f)
            else:
                logging.info("Upload success for file {}".format(f))
                responses.append(response)
    return responses


def store_archive_info(id, timestamp):
    with open('archive_db.csv', mode='w') as archive:
        db_writer = csv.writer(archive, delimiter=',')
        db_writer.writerow([id, timestamp])


# def split_file(path_to_file):
#     subprocess.Popen('split -db ' + split_size + ' ' + path_to_file + ' ' + default_suffix, shell=True)
#     files_list = os.listdir(path_to_file)
#     if not files_list:
#         logging.error("could not split the file  in {}".format(path_to_file))
#     return [file for file in files_list if default_suffix in file]


if __name__ == '__main__':
    file_name = create_archive(get_archive_candidate_list(), default_file_name)
    responses = upload_archive([file_name])
    for response in responses:
        print(response)
        id = response.id
        timestamp = datetime.now()
        store_archive_info(id, timestamp)
