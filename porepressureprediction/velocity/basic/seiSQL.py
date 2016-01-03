# -*- coding: utf-8 -*-
from __future__ import division, print_function
import sqlite3
import os
import json
import numpy as np


class SeisCube():
    def __init__(self, db, js):
        self.db_file = db
        self.json_file = js
        if self.json_file is not None:
            self._readJSON()
        self.attr = None
        if self.attr is None:
            self._get_existing_attr()

    def _info(self):
        return "A seismic Data Cube\n" +\
               'In-line range: {} - {} - {}\n'.format(
                self.startInline, self.endInline, self.stepInline) +\
               'Cross-line range: {} - {} - {}\n'.format(
                self.startCrline, self.endCrline, self.stepCrline) +\
               'Z range: {} - {} - {}\n'.format(
                self.startDepth, self.endDepth, self.stepDepth) +\
               "SQL file location : {}\n".format(os.path.abspath(self.db_file))

    def __str__(self):
        return self._info()

    def __repr__(self):
        return self._info()

    def _readJSON(self):
        # fin = open(self.json_file, 'r')
        with open(self.json_file, 'r') as fin:
            json_setting = json.load(fin)
            self.startInline = json_setting['inline'][0]
            self.endInline = json_setting['inline'][1]
            self.stepInline = json_setting['inline'][2]
            self.startCrline = json_setting['crline'][0]
            self.endCrline = json_setting['crline'][1]
            self.stepCrline = json_setting['crline'][2]
            self.startDepth = json_setting['depth'][0]
            self.endDepth = json_setting['depth'][1]
            self.stepDepth = json_setting['depth'][2]
            self.inline_A = json_setting['Coordinate'][0][0]
            self.crline_A = json_setting['Coordinate'][0][1]
            self.east_A = json_setting['Coordinate'][0][2]
            self.north_A = json_setting['Coordinate'][0][3]
            self.inline_B = json_setting['Coordinate'][1][0]
            self.crline_B = json_setting['Coordinate'][1][1]
            self.east_B = json_setting['Coordinate'][1][2]
            self.north_B = json_setting['Coordinate'][1][3]
            self.inline_C = json_setting['Coordinate'][2][0]
            self.crline_C = json_setting['Coordinate'][2][1]
            self.east_C = json_setting['Coordinate'][2][2]
            self.north_C = json_setting['Coordinate'][2][3]

            self.nEast = (self.endInline - self.startInline) // \
                self.stepInline + 1
            self.nNorth = (self.endCrline - self.startCrline) // \
                self.stepCrline + 1

            self._coordinate_conversion()

    def _coordinate_conversion(self):
        self.gamma_x = (self.east_B - self.east_A) / \
            (self.crline_B - self.crline_A)
        self.beta_x = (self.east_C - self.east_B) / \
            (self.inline_C - self.inline_B)
        self.alpha_x = self.east_A - \
            self.beta_x * self.inline_A - \
            self.gamma_x * self.crline_A
        self.gamma_y = (self.north_B - self.north_A) / \
            (self.crline_B - self.crline_A)
        self.beta_y = (self.north_C - self.north_B) / \
            (self.inline_C - self.inline_B)
        self.alpha_y = self.north_A - \
            self.beta_y * self.inline_A - \
            self.gamma_y * self.crline_A

    def _get_existing_attr(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("""SELECT name FROM sqlite_master
                    WHERE type='table' ORDER BY name""")
        temp = cur.fetchall()
        self.attr = tuple([item[0] for item in temp])
        conn.close()

    def coord_2_line(self, coordinate):
        x = coordinate[0]
        y = coordinate[1]
        d = np.matrix([[x - self.alpha_x],
                       [y - self.alpha_y]])
        G = np.matrix([[self.beta_x, self.gamma_x],
                       [self.beta_y, self.gamma_y]])
        m = G.I * d
        # m = m.astype(int)

        inline, crline = m[0][0], m[1][0]
        param_in = (inline - self.startInline) // self.stepInline + \
            ((inline - self.startInline) % self.stepInline) // \
            (self.stepInline / 2)
        inline = self.startInline + self.stepInline * param_in
        param_cr = (crline - self.startCrline) // self.stepCrline + \
            ((inline - self.startCrline) % self.stepCrline) // \
            (self.stepCrline)
        crline = self.startCrline + self.stepCrline * param_cr
        return (inline, crline)

    def line_2_coord(self, inline, crline):
        x = self.alpha_x + self.beta_x * inline + self.gamma_x * crline
        y = self.alpha_y + self.beta_y * inline + self.gamma_y * crline
        return (x, y)

    def get_inline(self, inline, attr):
        if attr in self.attr:
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()
            # cur.execute("""SELECT attribute FROM {table}
            #             WHERE inline=:il
            #             ORDER BY crline""".format(table=attr),
            #             {"il": inl})
            cur.execute("""SELECT attribute FROM position JOIN {table}
                        ON position.id = {table}.id
                        WHERE inline = {inl}""".format(table=attr, inl=inline))
            vv = cur.fetchall()
            conn.close()
            vv = [v[0] for v in vv]
            return vv
        else:
            pass

    def get_crline(self, crline, attr):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        # cur.execute("""SELECT vel FROM velocity WHERE
        #             crline=:xl ORDER BY inline""",
        #             {"xl": crl})
        cur.execute("""SELECT attribute FROM position JOIN {table}
                    ON position.id = {table}.id
                    WHERE crline = {crl}""".format(table=attr, crl=crline))
        vv = cur.fetchall()
        conn.close()
        vv = [v[0] for v in vv]
        return vv

    def get_depth(self, depth, attr):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        # cur.execute("""SELECT vel FROM velocity WHERE
        #             twt=:dp ORDER BY crline""",
        #             {"dp": depth})
        cur.execute("""SELECT attribute FROM position JOIN {table}
                    ON position.id = {table}.id
                    WHERE twt = {d}""".format(table=attr, d=depth))
        vv = cur.fetchall()
        conn.close()
        vv = [v[0] for v in vv]
        return vv

    def get_cdp(self, CDP, attr):
        il = CDP[0]
        cl = CDP[1]
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        # cur.execute("""SELECT vel FROM velocity WHERE
        #             inline=:inl AND crline=:xl ORDER BY twt""",
        #             {"inl": il, "xl": cl})
        cur.execute("""SELECT attribute FROM position JOIN {table}
                    ON position.id = {table}.id
                    WHERE inline = {inl} AND crline = {crl}
                    """.format(table=attr, inl=il, crl=cl))
        vv = cur.fetchall()
        conn.close()
        vv = [v[0] for v in vv]
        return vv

    def set_inline(self, inline, attr, vel):
        val = [(v[0],) for v in vel]
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.executemany("""UPDATE {table}
                       SET attribute = ?
                       WHERE inline={inl}
                       """.format(table=attr, inl=inline), val)
        conn.commit()
        conn.close()

    def set_crline(self, crline, attr, vel):
        val = [(v[0],) for v in vel]
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.executemany("""UPDATE {table}
                       SET attribute = ?
                       WHERE crline={crl}
                       """.format(table=attr, crl=crline), val)
        conn.commit()
        conn.close()

    def set_depth(self, depth, attr, vel):
        val = [(v[0],) for v in vel]
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.executemany("""UPDATE {table}
                       SET attribute = ?
                       WHERE twt={d}""".format(table=attr, d=depth), val)
        conn.commit()
        conn.close()

    def set_cdp(self, CDP, attr, vel):
        il = CDP[0]
        cl = CDP[1]
        val = [(v[0],) for v in vel]
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.executemany("""UPDATE {table}
                       SET attribute = ?
                       WHERE inlne={inl} AND crline={crl}
                       """.format(table=attr, inl=il, crl=cl), val)
        conn.commit()
        conn.close()

    def export_od(self, attr, fname):
        try:
            with open(fname, 'w') as fout:
                fout.write("{}\t{}\t{}\n".format(
                                            self.stepInline, self.stepCrline,
                                            self.stepDepth))
                conn = sqlite3.connect(self.db_file)
                cur = conn.cursor()
                for inl in range(self.startInline, self.endInline+1,
                                 self.stepInline):
                    for crl in range(self.startCrline, self.endCrline+1,
                                     self.stepCrline):
                        cur.execute('''SELECT attribute FROM {table}
                                    WHERE inline=:inl AND crline=:xl
                                    ORDER BY twt'''.format(talbe=attr),
                                    {'inl': inl, 'xl': crl})
                        temp = cur.fetchall()
                        if len(temp) == 0:
                            continue
                        else:
                            tempStr = list()
                            for i in range(len(temp)):
                                tempStr.append(str(temp[i][0]))
                            data = '\t'.join(tempStr) + '\n'
                            string = str(inl) + '\t' + str(crl) + '\t'
                            fout.write(string + data)
        except:
            print("failed to export")

if __name__ == "__main__":
    # a = SeisCube(os.path.join(os.path.pardir, "velocity_2.db"),
    #              os.path.join(os.path.pardir, "survey.json"))

    # data1 = a.get_Inline(1620)
    # data2 = a.get_Crline(5680)
    # data3 = a.get_Cdp((1620, 5680))
    # data4 = a.get_Depth(2400)
    # print(a)
    # print(a.nInline)
    # print(a.alpha_x, a.beta_x, a.gamma_x, sep=' ', end='\n')
    pass
