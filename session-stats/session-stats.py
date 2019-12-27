#!/bin/python3
import os
import sys
import functools as ft
import argparse
import json, pickle
sys.path.append(os.path.split(os.path.dirname(__file__))[0])
from common.session import *
import common.util as util
import re

REBUF_ROW_INDEX = 4
FORMAT_ROW_INDEX = 5

# rebufferingCount: Session -> Natural
def rebufferingCount(session):
    def is_rebuffer_event(row):
        return row[REBUF_ROW_INDEX] == "rebuffer"
    return util.count(is_rebuffer_event,
                      readCSV(session.client))

# qualitySwitches: Session -> Natural
def qualitySwitches(session):
    def accumulate_if_switch(acc, row):
        this_quality = formatToQuality(row[FORMAT_ROW_INDEX])
        last_quality = acc["quality"]
        count = acc["count"] + (1 if this_quality != last_quality else 0)
        return {"quality": this_quality,
                "count": count}
    last_switch = ft.reduce(accumulate_if_switch,
                            readCSV(session.chunk),
                            {"quality": False,
                             "count": -1})
    return last_switch["count"]

def formatToQuality(format_str):
    m = re.match("([^-]+)-", format_str)
    return m.group(1)

# summarize: Session -> Summary
def summarize(session):
    return {"id": session.client,
            "rebuffers": rebufferingCount(session),
            "quality_switches": qualitySwitches(session)}

# dumpSessionSummaries: (SequenceOf Summary) -> None
def dumpSessionSummaries(summaries):
    json.dump(list(summaries), sys.stdout,
              indent = 2)
    print()

class BadArgs(BaseException):
    pass

# main: -> Natural
def main():
    try:
        args = checkArgs(parseArgs())
    except BadArgs:
        return 1

    summaries = mapSessionsIn(summarize, args.directory)
    dumpSessionSummaries(summaries)

    return 0

# checkArgs: Args -> Args
# THROWS: BadArgs
def checkArgs(args):
    if not os.path.isdir(args.directory):
        print(f'{args.directory} is not a directory')
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

