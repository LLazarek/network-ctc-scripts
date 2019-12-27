import csv
import os
import functools as ft

# readCSV: PathToSomeFile -> (Listof (Listof String))
# Reads the csv in `path` into a list of rows,
# less the first row if `skip_first` is True
def readCSV(path, skip_first = True):
    first = True
    with open(path) as f:
        for row in csv.reader(f):
            if skip_first and first:
                first = False
            else:
                yield row

# listDir: (and String PathToSomeDirectory) -> (Listof (and String PathToSomething))
def listDir(path):
    def add_path(name):
        return os.path.join(path, name)
    files = os.listdir(path)
    return map(add_path, files)

def identity(x):
    return x

def count(f, seq):
    # return len(list(filter(f, seq)))
    def count_f(count, b):
        return ((count + 1) if f(b) else count)
    return ft.reduce(count_f, seq, 0)
