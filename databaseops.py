import sqlite3
import shutil
import datetime

def main():
    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            URL TEXT,
            Text TEXT,
            Tries INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def backup():
    source_file = 'database.db'

    current_date = datetime.date.today().strftime('%Y-%m-%d')
    backup_file = f'database_backup_{current_date}.db'

    # Copy the source file to the backup location
    shutil.copyfile(source_file, backup_file)

    
if __name__ == '__main__':
    main()