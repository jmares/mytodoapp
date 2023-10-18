import sqlite3
from sqlite3 import Error
import sys, os
import logging
from datetime import datetime, date
import time

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug(f"{this_function}: start")
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logging.debug(f"{this_function}: connection to db successful")
        return conn
    except Error as e:
        logging.critical(f"{this_function}: could not connect to database - {e}")

    return conn


def get_log_file_mode(log_file):
    """
    Determine the file-mode for the log-file for weekday rotation

    Parameters:
    log_file (str): path for the log-file

    Returns: 
    string: file-mode append ('a') or write ('w')
    """
    now = datetime.now()
    # check if log-file exists 
    if os.path.isfile(log_file):
        # if the log-file exists, compare the modified date to the current date
        file_date = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(log_file)))
        if file_date == now.strftime("%Y-%m-%d"):
            # if the modified date equals the current date, set file-mode to append
            file_mode = 'a'
        else:
            # if the modified date is different (older), set file-mode to (over)write
            file_mode = 'w'
    else:
        # if the log-file doesn't exist, set file-mode to write
        file_mode = 'w'

    return file_mode


def main():

    this_function = sys._getframe().f_code.co_name
    start_time = time.time()
    now = datetime.now()
    # create log-file per weekday: eg. srlvocab_Wed.log
    try: 
        log_file = 'logs/' + 'importer_' + now.strftime('%a') + '.log'
        log_level = logging.DEBUG
        file_mode = get_log_file_mode(log_file)
        logging.basicConfig(filename=log_file, encoding='UTF-8', filemode=file_mode, format='%(asctime)s - %(levelname)s : %(message)s', level=log_level)
        #print(log_file, log_level, file_mode)
    except Exception as e:
        print(e)

    logging.info(f"App: {os.path.basename(__file__)}")
    logging.info(f"{this_function}: start")

    try:
        # create a database connection
        conn = create_connection('instance/todo.db')


        # select list of words
        if conn is not None:
            cur = conn.cursor()

            f_data = open('./new_todo.csv', 'r', encoding="utf-8")
            lines = f_data.readlines()
            f_data.close()

            for line in lines:
                line = line.strip()
                if line == "":
                    break
                sql = f'''INSERT INTO todo_item (content, completed) VALUES ("{line}", 0);'''

                logging.debug(f"{this_function}: {sql}")
                res = cur.execute(sql)
                conn.commit()
                
            conn.close()
        
        else:
            print("Error! cannot create the database connection.")
    except Exception as e:
        logging.error(f"{this_function}: {e}")

    end_time = time.time()
    duration = str(round(end_time - start_time, 3))
    logging.info(f"{this_function}: time needed for script {duration} seconds")
    logging.info(f"{this_function}: ending execution\n")
    #print(f"duration: {duration}s")



if __name__ == '__main__':
    main()