#!/bin/python3
import os
import sys
import functools as ft
import csv
import argparse
import re
import json, pickle
from session import *

# -------------------- Configurable --------------------
T_min = 15
TIMESTAMP_INDEX = 0
# ----------------------------------------

# sessionFiles: (Listof (and String PathToSomeFile)) -> (Listof Session)
def sessionFiles(file_list):
    client_file_pattern = "/cb(_[^/]+.csv)$"
    # is_client_file: String -> Boolean
    def is_client_file(path):
        return True if re.search(client_file_pattern, path) else False
    def client_file_to_session(client_path):
        chunk_path = re.sub(client_file_pattern, "/vid\\1", client_path)
        return Session(client_path, chunk_path)
    client_files = filter(is_client_file, file_list)
    return map(client_file_to_session, client_files)

# sessionLengthAbove: Real -> (Session -> Boolean)
def sessionLengthAbove(minutes):
    def is_above(session):
        csv_path = session.client
        data = list(readCSV(csv_path))
        # get_time: (Listof String) -> Natural
        def get_time(row):
            return int(row[TIMESTAMP_INDEX])
        min_time = get_time(min(data, key=get_time, default=0))
        max_time = get_time(max(data, key=get_time, default=0))
        duration_seconds = max_time - min_time
        duration_minutes = duration_seconds/60
        return duration_minutes >= minutes

    return is_above

# readCSV: PathToSomeFile -> (Listof (Listof String))
def readCSV(path):
    with open(path) as f:
        for row in csv.reader(f):
            yield row

# dumpSessions: (Listof Session) [out OutputStream] [binary Boolean] -> None
def dumpSessions(sessions, out = sys.stdout, binary=False):
    if binary:
        binary = pickle.dumps(list(sessions))
        out.buffer.write(binary)
    else:
        encoded = map(encodeSession, sessions)
        json.dump(list(encoded), out)
        print()
    return None

# listDir: (and String PathToSomeDirectory) -> (Listof (and String PathToSomething))
def listDir(path):
    def add_path(name):
        return os.path.join(path, name)
    files = os.listdir(path)
    return map(add_path, files)

class BadArgs(BaseException):
    pass

# main: -> Natural
def main():
    try:
        args = checkArgs(parseArgs())
    except BadArgs:
        return 1

    all_files = listDir(args.directory)
    sessions = sessionFiles(all_files)
    sessions_above_T = filter(sessionLengthAbove(T_min), sessions)
    if args.json:
        dumpSessions(sessions_above_T)
    else:
        dumpSessions(sessions_above_T, binary=True)

    return 0

# checkArgs: Args -> Args
# THROWS: BadArgs
def checkArgs(args):
    if not os.path.isdir(args.directory):
        raise BadArgs
    return args

# parseArgs: -> Args
def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="The directory containing session data."
                        "*This is a mandatory argument.*")
    parser.add_argument("-j", "--json", action="store_true",
                        help="Output json instead of binary pickle data. "
                        "Default is to output binary.")
    # parser.add_argument("-d", "--depth", type=int, default="2",
    #                     help="The page depth to search. "
    #                     "Default: 2.")
    # parser.add_argument("-n", "--negate", action="store_true",
    #                     help="Negate content regexp: "
    #                     "Print only page urls that do *not* contain "
    #                     "the content pattern.")
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
