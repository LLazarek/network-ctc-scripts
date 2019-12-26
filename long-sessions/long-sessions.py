#!/bin/python3
import os
import sys
import functools as ft
import argparse
import json, pickle
from session import *

# -------------------- Configurable --------------------
T_min = 15
TIMESTAMP_INDEX = 0
# ----------------------------------------

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


# dumpSessions: (Listof Session) [out OutputStream] [binary Boolean] -> None
def dumpSessions(sessions, out = sys.stdout, binary=False):
    if binary:
        binary = pickle.dumps(list(sessions))
        out.buffer.write(binary)
    else:
        encoded = map(encodeSession, sessions)
        json.dump(list(encoded), out, indent=4)
        print()
    return None


class BadArgs(BaseException):
    pass

# main: -> Natural
def main():
    try:
        args = checkArgs(parseArgs())
    except BadArgs:
        return 1

    sessions_above_T = filterSessionsIn(sessionLengthAbove(T_min),
                                        args.directory)
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
                        "Default: current directory")
    parser.add_argument("-j", "--json", action="store_true",
                        help="Output json instead of binary pickle data. "
                        "Default is to output binary.")
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
