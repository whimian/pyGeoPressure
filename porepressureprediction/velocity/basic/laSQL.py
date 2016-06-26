# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
from las import LASReader
import json
import sqlite3
import os
import copy


class Well(object):
    """class for storing well log data with database file

    This Well class stores the well log data in associated database files,
    stores the well information in associated json files, and provides methods
    for accessing these external data.

    Attributes
    ----------
    db_file : string
        the address of database file storing the log data
    sellSetting : string
        the address of json file storing well information

    Methods
    -------
    add_log(log, name)
        Add an array of log data to the Well object
    drop_log(name)
        delete the log named 'name'
    logs()
        display existing logs in the database
    get_log(name)
        retrieve specific log
    Notes
    -----

    Raises
    ------

    """
    def __init__(self, js=None, db=None):
        self.db_file = 'new_db.db' if db is None else db
        self.json_file = 'new_json.json' if js is None else js
        self._check_file()
        self.las_file = None
        self.existing_logs = None
        self._parse_existing_logs()
        self.name = None
        self.loc = None
        self.start = None
        self.stop = None
        self.step = None
        self._read_setting()

    def _info(self):
        return "Well Name: {}\n".format(self.name) +\
               "Position: {}\n".format(self.loc) +\
               "Depth range: {} - {} - {}\n".format(
                self.start, self.stop, self.step)

    def __str__(self):
        return self._info()

    def __repr__(self):
        return self._info()

    def __len__(self):
        return (float(self.stop) - float(self.start)) / float(self.step) + 1

    def _parse_existing_logs(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()
            cur.execute("SELECT name FROM curves")
            temp = cur.fetchall()
            conn.close()
            self.existing_logs = [curv[0].lower() for curv in temp]
        except:
            print("Problem happened.")
            pass

    def _check_file(self):
        if not self.db_file.endswith('.db'):
            raise Exception("`db` should be .db file, " +
                            "or use None instead")
        if not os.path.exists(self.db_file):
            try:
                fDB = open(self.db_file, 'w')
                fDB.close()
            except:
                print("Error: Database file cannot be created!")

        if not self.json_file.endswith('.json'):
            raise Exception("`json` should be .josn file, " +
                            "or use None instead")
        if not os.path.exists(self.json_file):
            try:
                fJSON = open(self.json_file, 'w')
                fJSON.close()
            except:
                print("Error: JSON file cannot be created!")

    def _feet_2_meter(self, item_in_feet):
        """converts feet to meters
        """
        # vfunc_model = np.vectorize(spherical)
        try:
            return item_in_feet / 3.28084
        except TypeError:
            return float(item_in_feet) / 3.28084

    def _rolling_window(self, a, window):
        a = np.array(a)
        shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
        strides = a.strides + (a.strides[-1],)
        rolled = np.lib.stride_tricks.as_strided(
                                            a, shape=shape, strides=strides)
        return rolled

    def _despike(self, curve, curve_sm, max_clip):
        spikes = np.where(curve - curve_sm > max_clip)[0]
        spukes = np.where(curve_sm - curve > max_clip)[0]
        out = np.copy(curve)
        out[spikes] = curve_sm[spikes] + max_clip
        out[spukes] = curve_sm[spukes] - max_clip
        return out

    def _read_setting(self):
        try:
            with open(self.json_file, 'r') as fin:
                jsStruct = json.load(fin)
                location = jsStruct['LOC']['data'].split()
                if len(location) == 0:
                    raise ValueError
                self.loc = (float(location[2]), float(location[5]))
                self.start = jsStruct['STRT']['data']
                self.stop = jsStruct['STOP']['data']
                self.step = jsStruct['STEP']['data']
                self.name = jsStruct['WELL']['data']
                if self.step == 0:
                    self.step = 0.1
        except ValueError:
            print("No valid coordination found.")
        except:
            print("cannot open json file")
            pass

    # def get_log(self, name, window=None):
    #     if name not in self.existing_logs:
    #         raise Exception("no log named {}!".format(name))
    #     conn = sqlite3.connect(self.db_file)
    #     cur = conn.cursor()
    #     cur.execute("SELECT {} FROM data".format(name))
    #     log = cur.fetchall()
    #     conn.close()
    #     log = [d[0] for d in log]
    #     if window is None:
    #         return log
    #     else:
    #         log_sm = np.median(self._rolling_window(log, window), -1)
    #         log_sm = np.pad(log_sm, window / 2, mode='edge')

    def get_log(self, name):
        if name not in self.existing_logs:
            raise Exception("no log named {}!".format(name))
        depth = None
        data = None
        info = None
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute("SELECT {} FROM data".format(name))
            data = cur.fetchall()
            cur.execute("SELECT dept FROM data")
            depth = cur.fetchall()
            cur.execute("SELECT * FROM curves WHERE name = \"{}\"".format(
                                                                name.upper()))
            info = cur.fetchall()
        data = [d[0] for d in data]
        depth = [d[0] for d in depth]
        for idx, d in enumerate(data):
            if d is None:
                data[idx] = np.nan
        log = Log()
        log.name = info[0][1].lower()
        log.units = info[0][2].lower()
        log.descr = info[0][3]
        log.depth = depth
        log.data = data
        return log

    def update_log(self, log):
        try:
            if name not in self.existing_logs:
                raise Exception("no log named {}!".format(log.name))
            with sqlite3.connect(self.db_file) as conn:
                cur = conn.cursor()
                dTuple = [(d,) for d in log.data]
                for dep, dat in zip(log.depth, dTuple):
                    cur.execute("UPDATE data SET {} = ? WHERE \
                                dept = {}".format(log.name, dep), dat)
                conn.commit()
        except Exception as inst:
            print(inst.args[0])

    def add_log(self, log):
        """save log data into the database
        """
        try:
            if len(log) == 0:
                raise Exception("No valid data in log")
            if self.__len__() < len(log):
                raise Exception("length does not match")
            with sqlite3.connect(self.db_file) as conn:
                cur = conn.cursor()

                cur.execute("SELECT COUNT(*) FROM curves")
                index = cur.fetchone()[0] + 1
                curvesTuple = (index, log.name, log.units, log.descr)
                cur.execute("INSERT INTO curves VALUES (?, ?, ?, ?)",
                            curvesTuple)
                cur.execute("ALTER TABLE data \
                             ADD COLUMN {} REAL".format(log.name.lower()))
                dataList = [(a,) for a in log.data]

                for de, da in zip(log.depth, dataList):
                    cur.execute("UPDATE data \
                                   SET {} = ?\
                                   WHERE dept = {}".format(
                                   log.name.lower(), de), da)
                conn.commit()
        except Exception as inst:
            print(inst.args[0])
            pass

    def drop_log(self, name):
        """remove log from the database
        """
        pass

    def logs(self):
        """display all existing logs in the database"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("SELECT * FROM curves")
        dataTuples = cur.fetchall()
        conn.close()
        return [{"id": a[0], "name": a[1], "units": a[2],
                 "descr": a[3]} for a in dataTuples]

    def _change_file_name(self):
        project_folder = os.getcwd()

        json_name = os.path.basename(self.json_file)
        json_folder = os.path.abspath(os.path.dirname(self.json_file))
        json_name_new = self.well_name + os.path.extsep +\
            self.json_file.split('.')[1]

        os.chdir(json_folder)
        os.rename(json_name, json_name_new)
        os.chdir(project_folder)

        self.json_file = os.path.join(json_folder, json_name_new)

        db_name = os.path.basename(self.db_file)
        db_folder = os.path.abspath(os.path.dirname(self.db_file))
        db_name_new = self.well_name + os.path.extsep +\
            self.db_file.split('.')[1]

        os.chdir(db_folder)
        os.rename(db_name, db_name_new)
        os.chdir(project_folder)

        self.db_file = os.path.join(db_folder, db_name_new)

    def read_las(self, las_file=None):
        self.las_file = las_file
        if self.las_file is None:
            self.las_file = '../data/wells/TWT1.las'
        las = LASReader(self.las_file, null_subs=np.nan)
        self.well_name = las.well.items['WELL'].data

        self._change_file_name()
        self.existing_logs = []
        jsonDict = las.well.items.copy()
        for key in jsonDict.keys():
            jsonDict[key] = {}
            jsonDict[key]['units'] = las.well.items[key].units
            jsonDict[key]['data'] = las.well.items[key].data
            jsonDict[key]['descr'] = las.well.items[key].descr

        with open(self.json_file, 'w') as fout:
            json.dump(jsonDict, fout, indent=4, sort_keys=False)

        sqlList = []
        for litem in las.curves.items.values():
            sqlTuple = []
            # tempList = litem.descr.split('=')
            # sqlTuple.append(tempList[0].split()[0])
            sqlTuple.append(las.data.dtype.names.index(litem.name) + 1)
            # giving each entry the right index to match the order of log data.
            sqlTuple.append(litem.name)
            self.existing_logs.append(litem.name.lower())
            sqlTuple.append(litem.units)
            # sqlTuple.append(tempList[-1][1:])
            sqlTuple.append(litem.descr)
            sqlTuple = tuple(sqlTuple)
            sqlList.append(sqlTuple)

        sqlList.sort(key=lambda x: x[0])

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE curves (
                 id INTEGER,
                 name TEXT,
                 units TEXT,
                 decr TEXT
            )""")

        cur.executemany("INSERT INTO curves VALUES (?, ?, ?, ?)",
                        sqlList)
        template = ""
        nameList = [a[1].lower() + " REAL" for a in sqlList]
        nameList.insert(0, "id INTEGER PRIMARY KEY")
        template = (',\n\t\t').join(nameList)
        cur.execute("CREATE TABLE data (\n\t\t{}\n\t)".format(template))
        for i in xrange(int(las.data2d.shape[0])):
            temp = list(las.data2d[i])
            temp.insert(0, i+1)
            temp = tuple(temp)
            cur.execute("INSERT INTO data \
                        VALUES (" + ','.join(['?'] * len(temp)) + ")",
                        temp)
        conn.commit()
        conn.close()
        self._read_setting()
        self._parse_existing_logs()


class Log(object):
    """
    class for well log
    """
    def __init__(self):
        self.name = ""
        self.units = ""
        self.decr = ""
        self.data = list()
        self.depth = list()
        self.log_start = None
        self.log_stop = None
        self.depth_start = None
        self.depth_stop = None

    def __len__(self):
        return len(self.data)

    def _info(self):
        return "Log Name: {}\n".format(self.name) +\
               "Log Units: {}\n".format(self.units) +\
               "Depth range: {} - {} - {}\n".format(
                self.depth[0], self.depth[-1], 0.1)

    def __str__(self):
        return self._info()

    def __repr__(self):
        return self._info()

    @property
    def start(self):
        if self.log_start is None:
            for dep, dat in zip(self.depth, self.data):
                if dat is not np.nan:
                    self.log_start = dep
                    break
        return self.log_start

    @property
    def stop(self):
        if self.log_stop is None:
            for dep, dat in zip(reversed(self.depth), reversed(self.data)):
                if dat is not np.nan:
                    self.log_stop = dep
                    break
        return self.log_stop

    @property
    def top(self):
        return self.depth[0]

    @property
    def bottom(self):
        return self.depth[-1]

    def read_od(self, file_name):
        try:
            with open(file_name, "r") as fin:
                fin.readline()
                for line in fin:
                    tempList = line.split()
                    self.depth.append(round(float(tempList[0]), 1))
                    if tempList[1] == "1e30":
                        self.data.append(np.nan)
                    else:
                        self.data.append(float(tempList[1]))
        except Exception as inst:
            print(inst.args)


def rolling_window(a, window):
    a = np.array(a)
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolled = np.lib.stride_tricks.as_strided(
                                        a, shape=shape, strides=strides)
    return rolled


def despike(curve, curve_sm, max_clip):
    spikes = np.where(curve - curve_sm > max_clip)[0]
    spukes = np.where(curve_sm - curve > max_clip)[0]
    out = np.copy(curve)
    out[spikes] = curve_sm[spikes] + max_clip
    out[spukes] = curve_sm[spukes] - max_clip
    return out


def smooth_log(log, window=3003):
    """
    Parameter
    ---------
    log : Log object
        log to smooth
    window : scalar
        window size of the median filter

    Return
    ------
    smoothed log : Log object
        smoothed log
    """
    data2smooth = copy.copy(log.data)
    log_sm = np.median(rolling_window(data2smooth, window), -1)
    log_sm = np.pad(log_sm, window // 2, mode="edge")
    logSmoothed = Log()
    logSmoothed.name = log.name + "_edited"
    logSmoothed.units = log.units
    logSmoothed.descr = log.descr
    logSmoothed.depth = log.depth
    logSmoothed.data = log_sm
    return logSmoothed

if __name__ == '__main__':
    well = Well(js="../testFile/TWT1.json", db="../testFile/TWT1.db")
    print(well.loc)
    # well = Well()
    # well.read_las("../data/wells/TWT3.las")
    d1 = well.get_log("ac")
    # d2 = list(np.random.rand(len(d1)))
    # well.update_log('ac', d2)
    # print well.get_log('ac')[:10]
    print(d1[:10])
    # print(well.existing_logs)
