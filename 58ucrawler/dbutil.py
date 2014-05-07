import os
import sqlite3


db_name = 'tc_skill.db'
table_name = 't_tc_user'


def create_table():
    print 'Creating DB', db_name, '...'
    # check whether the db is exist
    files = os.listdir('.')
    if db_name in files:
        print "A db file already existed! Delete it first or just use it."
        exit(0)
    conn = sqlite3.connect(db_name)
    conn.execute('''CREATE TABLE %s
                (uid int(20) primary key not null ,
                nickname varchar(10),
                sex varchar(1),
                age int(8),
                location varchar(10),
                city varchar(10),
                skill text,
                want text,
                fetched int(1))''' % table_name)
    print "DB created successfully"
    print "Table %s created successfully" % table_name


def insert_uid(uid, city):
    conn = sqlite3.connect(db_name)
    conn.execute("INSERT INTO %s (uid, city, fetched) values (%s, %s)" % (table_name, uid, city))
    conn.commit()
    conn.close()


def insert_uids(uids, city):
    if len(uids) <= 0:  # skip empty set
        return
    conn = sqlite3.connect(db_name)
    for uid in uids:
        sql = "INSERT INTO %s (uid, city) values (?, ?)" % table_name
        try:
            conn.execute(sql, (uid, city))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()


def update_page_data(result):
    conn = sqlite3.connect(db_name)
    sql = "UPDATE %s SET nickname = ?, sex = ?, age = ?, location = ?,  skill = ?,  want = ?, fetched = 1 where uid = ?" % table_name
    conn.execute(sql, (result['nickname'], result['sex'], result['age'],
                       result['location'], result['skill'], result['want'], result['uid']))
    conn.commit()
    conn.close()


def get_fetching_uids():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("SELECT uid from %s where fetched is null limit 10" % table_name)
    res = cur.fetchall()
    for uid in res:
        sql = "UPDATE %s set fetched = 1 where uid = ?" % table_name
        cur.execute(sql, uid)
    conn.commit()
    cur.close()
    conn.close()
    return res


def export(out_filename):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    sql = "SELECT * from %s" % table_name
    cur.execute(sql)
    out_file = open(out_filename, 'wb')
    headers = ",".join([i[0] for i in cur.description])  # write headers
    out_file.write(headers.encode('utf-8'))
    out_file.write("\n")
    while True:
        row = cur.fetchone()
        if row is None:
            break
        encoded_row = []
        for item in row:
            item = unicode(item)
            item = item.encode('utf-8')
            encoded_row.append(item)
        out_file.write(",".join(encoded_row))
        out_file.write("\n")
    out_file.close()
    cur.close()
    conn.close()
    print 'Export to file ** %s ** Done!' % out_filename


if __name__ == '__main__':
    pass