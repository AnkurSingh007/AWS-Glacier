#! /usr/bin/env python3
import os
import sys
import logging
import tarfile
import argparse
from functools import lru_cache
import boto3

logging.basicConfig(filename='log.txt',
                    level=logging.DEBUG,
                    format='%(asctime)s    %(levelname)s    %(message)s')
parser = argparse.ArgumentParser(description='Archive files and directories.')
glacier = boto3.resource('glacier')


@lru_cache(maxsize=1)
def get_commandline_args():
  parser.add_argument('list', nargs = '+', action = 'store', help = 'A list of path of files and/or directories')
  parser.add_argument('--name', action = 'store', help = 'Name to be used for the archieve file')
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


def create_archive(candidate_list):
  # Create a tar file in the same directory of this script.
  file_name = 'sample.tar.gz'
  filtered_list = filter_archive_candidate_list(candidate_list)
  with tarfile.open(file_name, 'w:gz') as tar:
    for candidate in filtered_list:
      tar.add(candidate)
      logging.debug("{} archive success".format(candidate))
  return file_name


if __name__ == "__main__":
  file_name = create_archive(get_archive_candidate_list())
  
