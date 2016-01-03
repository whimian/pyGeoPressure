import sqlite3


class Reader(object):
    """class to create sqlite database with text file
    """
    def __init__(self, db_name=None):
        self.db_file = str(db_name) + ".db" if db_name is not None \
            else "new_db.db"
        self._create_db()

    def _create_db(self):
        f = open(self.db_file, 'w')
        f.close()
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE position(
            id INTEGER PRIMARY KEY,
            inline INTEGER,
            crline INTEGER,
            twt REAL
        )''')
        conn.commit()
        conn.close()

    def _update_db(self, vel, attr):
        # po = [[v[0], v[1], v[2]] for v in vel]
        # at = [[v[3]] for v in vel]
        n = len(vel)
        # for i in xrange(n):
        #     po[i].insert(0, i)
        #     at[i].insert(0, i)

        po = [tuple([i, vel[i][0], vel[i][1], vel[i][2]]) for i in xrange(n)]
        at = [tuple([i, vel[i][3]]) for i in xrange(n)]

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.executemany("INSERT INTO position VALUES (?, ?, ?, ?)",
                        po)

        # for i in xrange(n):
        #     temp = po[i]
        #     temp.insert(0, i)
        #     cur.execute("INSERT INTO position VALUES (?, ?, ?, ?)",
        #                 tuple(temp))
        cur.execute("""CREATE TABLE {}(
            id INTEGER PRIMARY KEY,
            attribute REAL
        )""".format(attr))
        cur.executemany("INSERT INTO {} VALUES (?, ?)".format(attr), at)
        # for i in xrange(n):
        #     temp = at[i]
        #     temp.insert(0, i)
        #     cur.execute("INSERT INTO {} VALUES (?, ?)".format(attr),
        #                 tuple(temp))
        conn.commit()
        conn.close()

    def read_HRS(self, textfile, attr):
        velocity = list()
        with open(textfile, 'r') as textVel:
            for line in textVel:
                temp = line.split()
                temp = [float(t) for t in temp]
                del temp[2]
                del temp[2]
                velocity.append(temp)

        self._update_db(velocity, attr)

    def read_od(self, textfile, attr):
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

        self._update_db(velocity, attr)
