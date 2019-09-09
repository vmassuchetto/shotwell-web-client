import os
from sqlite3 import connect
from re import sub
from time import mktime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, g, request, jsonify, \
    render_template, send_from_directory, send_file

app = Flask(__name__)
for c in ('shotwell_web_client.config', 'config'):
    try:
        app.config.from_object(c)
    except:
        pass

def dict_factory(cursor, row):
    d = {}
    for i, c in enumerate(cursor.description):
        d[c[0]] = row[i]
    return d

def connect_db():
    """Connects to the Shotwell database."""
    c = connect(os.path.expanduser(app.config['DATABASE']))
    c.row_factory = dict_factory
    return c

def get_db():
    """Opens a database connection if there is none."""
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

def close_db():
    """Closes the database connection."""
    if hasattr(g, 'db'):
        g.db.close()

def get_date_tree():
    db = get_db()
    c = db.execute('''
        SELECT *
        FROM (
            SELECT exposure_time FROM PhotoTable WHERE event_id <> -1
            UNION
            SELECT exposure_time FROM VideoTable WHERE event_id <> -1
        )
        GROUP BY exposure_time
        ORDER BY exposure_time DESC
    ''')
    t = dict()
    for e in c.fetchall():
        date = datetime.fromtimestamp(e['exposure_time'])
        formatted = sub('[0-9][0-9]:[0-9][0-9]:[0-9][0-9] ', '', date.strftime('%c'))
        t.setdefault(date.strftime('%Y'), dict())
        t[date.strftime('%Y')].setdefault(date.strftime('%B'), dict())
        t[date.strftime('%Y')][date.strftime('%B')].setdefault(date.strftime('%d'), set())
        t[date.strftime('%Y')][date.strftime('%B')][date.strftime('%d')].add(formatted)
    return t

@app.route('/vendor/<path:path>')
def send_vendor(path):
    return send_from_directory('node_modules/', path)

@app.route('/items/')
def items():
    start = request.args.get('start', 0)
    query = request.args.get('query', None)

    where = 'AND event_id <> -1'
    orderby = 'item_time DESC'

    if query.startswith('lib_'):
        if query == 'lib_lastimported':
            orderby = 'import_id DESC, item_time DESC'
        elif query == 'lib_trash':
            where = 'AND event_id = -1'
    elif query.startswith('event_'):
        query = query.lstrip('event_')
        date = None
        for fmt in (('%Y%B%d', relativedelta(days=+1)),
                    ('%Y%B', relativedelta(months=+1)),
                    ('%Y', relativedelta(years=+1))):
            try:
                date = [datetime.strptime(query, fmt[0])]
                date.append(date[0] + fmt[1])
            except ValueError:
                pass
        if date is not None:
            where += " AND exposure_time >= '%s' AND exposure_time < '%s'" % (
                int(mktime(date[0].timetuple())), int(mktime(date[1].timetuple())))
    elif query.startswith('tag_'):
        name = query[4:]

        sql = '''
        SELECT * FROM TagTable WHERE name = "%s"
        ''' % name

        db = get_db()
        c = db.execute(sql)
        row = c.fetchone()

        photo_ids = [0]
        video_ids = [0]
        if row['photo_id_list']:
            tmp = row['photo_id_list'].split(',')

            for val in tmp:
                video = False
                if 'thumb' == val[0:5]:
                    strHex = val[5:]
                elif 'video-' == val[0:6]:
                    strHex = val[6:]
                    video = True
                while '0' == strHex[0:1]:
                    strHex = strHex[1:]
                if '' == strHex:
                    continue
                id = int(strHex, 16)
                if id < 1:
                    continue

                if not video:
                    photo_ids.append(id)
                else:
                    video_ids.append(id)

        if len(photo_ids) < 2 and len(video_ids) < 2:
            return '[]'

        sql = '''
        SELECT * FROM (
            SELECT 'photo' AS type, id item_id, exposure_time item_time, import_id
            FROM PhotoTable
            WHERE id IN (%s) AND id > 0 %s
            UNION
            SELECT 'video' AS type, id item_id, exposure_time item_time, import_id
            FROM VideoTable
            WHERE id IN (%s) AND id > 0 %s
        ) ORDER BY %s
        LIMIT %d,%d
        ''' % (",".join(str(x) for x in photo_ids), where, ",".join(str(x) for x in video_ids), where, orderby, int(start), int(app.config['LOAD']))

        db = get_db()
        c = db.execute(sql)
        return jsonify(c.fetchall())

    sql = '''
	SELECT * FROM (
	    SELECT 'photo' AS type, id item_id, exposure_time item_time, import_id
            FROM PhotoTable
            WHERE 1=1 %s
            UNION
            SELECT 'video' AS type, id item_id, exposure_time item_time, import_id
            FROM VideoTable
            WHERE 1=1 %s
	) ORDER BY %s
        LIMIT %d,%d
        ''' % (where, where, orderby, int(start), int(app.config['LOAD']))
    db = get_db()
    c = db.execute(sql)
    return jsonify(c.fetchall())

def get_tags():
    sql = 'SELECT id, name FROM TagTable'
    db = get_db()
    c = db.execute(sql)
    return c.fetchall()

@app.route('/tags/')
def tags():
    return jsonify(get_tags())

@app.route('/thumb/<type>/<id>')
def thumb(type, id):
    if type == 'photo':
        prefix = 'thumb'
    elif type == 'video':
        prefix = 'video-'
    return send_file('%s/%s%016x.jpg' % (os.path.expanduser(app.config['THUMBPATH']), prefix, int(id)))

@app.route('/photo/<id>')
def photo(id):
    db = get_db()
    c = db.execute('SELECT filename FROM PhotoTable WHERE id = ?', [int(id)])
    return send_file(c.fetchone()['filename'])

@app.route('/video/<id>')
def video(id):
    db = get_db()
    c = db.execute('SELECT filename FROM VideoTable WHERE id = ?', [int(id)])
    return send_file(c.fetchone()['filename'])

@app.route('/')
def index():
    date_tree = get_date_tree()

    allTags = get_tags()

    return render_template('index.html', date_tree=date_tree, tags=allTags)

def main():
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('DEBUG', False))

if __name__ == '__main__':
    main()
