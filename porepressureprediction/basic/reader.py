# -*- coding: utf-8 -*-
"""
class for reading test file and writing into sqlite db
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import time
import sqlite3
from functools import wraps
from math import ceil

from segpy.reader import create_reader


class Reader(object):
    """class to create sqlite database with text file
    """
    def __init__(self, db_name=None):
        self.db_file = str(db_name) + ".db" if db_name is not None \
            else "new_db.db"

    def _add_attribute(self, data, attr):
        at = [(da,) for da in data]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS {} ( ".format(attr) +\
                "id INTEGER PRIMARY KEY, " +\
                "attribute REAL) ")
            cur.executemany(
                "INSERT INTO {} ({}) ".format(attr, 'attribute') +\
                "VALUES (?)", at)

    def _add_position(self, data):
        n = len(data)
        po = [tuple([i, data[i][0], data[i][1], data[i][2]])
              for i in range(n)]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute("BEGIN TRANSACTION")
            cur.execute('''CREATE TABLE position(
                id INTEGER PRIMARY KEY,
                inline INTEGER,
                crline INTEGER,
                twt REAL
            )''')
            cur.executemany("INSERT INTO position VALUES (?, ?, ?, ?)",
                            po)

            cur.execute("CREATE INDEX IF NOT EXISTS idx_twt ON \
                         position(twt)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_inl ON \
                         position(inline)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_crl ON \
                         position(crline)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cdp ON \
                         position(inline, crline)")
            cur.execute("COMMIT")

    def _read_hrs(self, textfile):
        velocity = list()
        with open(textfile, 'r') as textVel:
            for line in textVel:
                temp = line.split()
                temp = [float(t) for t in temp]
                del temp[2]
                del temp[2]
                velocity.append(temp)
        return velocity

    def _read_od(self, textfile):
        velocity = list()
        with open(textfile, 'r') as textVel:
            info = textVel.readline()
            fileInfo = info.split()
            startTwt = float(fileInfo[0])
            stepTwt = float(fileInfo[1])
            nTwt = int(fileInfo[-1])
            for line in textVel:
                data = line.split()
                inline = int(data[0])
                crline = int(data[1])
                for i in range(2, nTwt + 2):
                    velocity.append([
                        inline, crline, startTwt + (i-2) * stepTwt,
                        float(data[i])])
        return velocity

    def _read_segy(self, bfile, attr):
        with open(bfile, 'rb') as textVel:
            segy_reader = create_reader(
                textVel, progress=make_progress_indicator('Scanning'))
            print("Creating database...")
            nCDP = segy_reader.num_traces()
            n_per_trace = segy_reader.num_trace_samples(0)
            n_trace_per_transaction = MAX_SAMPLES_PER_TRANSACTION // n_per_trace
            n_transactions = ceil(nCDP / n_trace_per_transaction)

            niter = 0
            for traces_transact in split_sequence(list(range(nCDP)), n_trace_per_transaction):
                niter += 1
                data = []
                for trace_index in traces_transact:
                    tr_data = segy_reader.trace_samples(trace_index)
                    tr_data = [float(da) for da in tr_data]
                    data += tr_data
                self._add_attribute(data, attr)
                print("------ {}%".format(int(niter / n_transactions * 100)))
            print("-"*6 + "{}%".format(100))

    def read(self, textfile, attr, filetype="od"):
        """
        Parameters
        ----------
        textfile : str
            input file path
        attr : str
            attribute name
        filetype: str
            ["od", "hrs"]

        Notes
        -----
        For filetype, the format should be
        "Output a position for every trace  Yes"
        "Position in file will be   Inl Crl"
        "Put sampling info in file start    Yes"
        """
        if filetype == "od":
            velocity = self._read_od(textfile)
        elif filetype == "hrs":
            velocity = self._read_hrs(textfile)
        elif filetype == "segy":
            measure(self._read_segy)(textfile, attr)
        else:
            raise Exception("Unkown filetype. (>_<)")
        # measure(self._add_position)(velocity)
        # measure(self._add_attribute)(velocity, attr)

    def add(self, textfile, attr, filetype="od"):
        """
        Add new attribute to seismic database without changing its position
        information.
        """
        if filetype == "od":
            velocity = self._read_od(textfile)
        elif filetype == "hrs":
            velocity = self._read_hrs(textfile)
        else:
            raise Exception("Unkown filetype. (>_<)")
        self._add_attribute(velocity, attr)


def make_progress_indicator(name):
    previous_integer_progress = -1

    def progress(p):
        nonlocal previous_integer_progress
        percent = p * 100
        current_integer_progress = int(percent)
        if current_integer_progress != previous_integer_progress:
            print('{}: {}%'.format(name, current_integer_progress))
        previous_integer_progress = current_integer_progress

    return progress

def measure(func):
    @wraps(func)
    def measured(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        name = func.__name__
        print("[{}] {}".format(elapsed, name))
        return result
    return measured

# MAX_SAMPLES_PER_TRANSACTION = 9990000
MAX_SAMPLES_PER_TRANSACTION = 990000
