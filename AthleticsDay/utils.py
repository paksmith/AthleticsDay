import pymysql

def create_connection():
    return pymysql.connect(  
        host = '127.0.0.1',
        user = 'root',
        password = '13com',
        db = 'AthleticsDay',
        charset = 'utf8mb4',
        cursorclass = pymysql.cursors.DictCursor
    )

