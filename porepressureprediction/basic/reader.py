# -*- coding: utf-8 -*-
"""
class for reading test file and writing into sqlite db
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import sqlite3

from segpy.reader import create_reader


class Reader(object):
    """class to create sqlite database with text file
    """
    def __init__(self, db_name=None):
        self.db_file = str(db_name) + ".db" if db_name is not None \
            else "new_db.db"

    def _add_attribute(self, data, attr):
        n = len(data)
        at = [tuple([i, data[i][3]]) for i in range(n)]

        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE {}(
                id INTEGER PRIMARY KEY,
                attribute REAL
            )""".format(attr))
            cur.executemany("INSERT INTO {} VALUES (?, ?)".format(attr), at)

    def _add_position(self, data):
        n = len(data)
        po = [tuple([i, data[i][0], data[i][1], data[i][2]])
              for i in range(n)]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
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

    def _read_segy(self, bfile):
        velocity = []
        with open(bfile, 'rb') as textVel:
            segy_reader = create_reader(
                textVel, progress=make_progress_indicator('Importing'))
            for inline, crline in segy_reader.inline_xline_numbers():
                trace_index = segy_reader.trace_index((inline, crline))

                trace = segy_reader.trace_samples(trace_index)
                data = trace.tolist()
                tr_header = segy_reader.trace_header(trace_index)
                startTwt = tr_header.delay_recording_time
                stepTwt = tr_header.sample_interval * 10**(-3)  # in milliseconds
                nTwt = tr_header.num_samples
                for i in range(nTwt):
                    velocity.append([
                        inline, crline, startTwt + i * stepTwt,
                        float(data[i])
                    ])
        return velocity

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
            velocity = self._read_segy(textfile)
        else:
            raise Exception("Unkown filetype. (>_<)")
        self._add_position(velocity)
        self._add_attribute(velocity, attr)

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
