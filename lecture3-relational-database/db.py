import sqlite3

def parse_row(row,columns):
    # Turn a row into a dictionary 
    parsed_row = {}
    for i in range(len(columns)):
        parsed_row[columns[i]] = row[i]
    return parsed_row 

def parse_cursor(cursor,columns):
    # parse the whole table/ cursor 
    return [parse_row(row,columns) for row in cursor]


def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


class DatabaseDriver(object):
    def __init__(self):
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.create_task_table()
        self.create_subtasks_table()

    # -- TASKS -----------------------------------------------------------

    def create_task_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    done INTEGER NOT NULL
                );
            """
            )
        except Exception as e:
            print(e)

    def delete_task_table(self):
        self.conn.execute("DROP TABLE IF EXISTS tasks;")

    def get_all_tasks(self):
        cursor = self.conn.execute("SELECT * FROM tasks;")
        tasks = parse_cursor(cursor,['id','description','done'])
        return tasks

    def insert_task_table(self, description, done):
        cursor = self.conn.execute("INSERT INTO tasks (description, done) VALUES (?, ?);", (description, done))
        self.conn.commit()
        return cursor.lastrowid

    def get_task_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (id,))
        for row in cursor:
            return parse_row(row,['id','description','done'])
        return None

    def update_task_by_id(self, id, description, done):
        """
        Using SQL, updates a task by id
        """
        self.conn.execute(
            """
            UPDATE tasks
            SET description = ?, done = ?
            WHERE id = ?;
        """,
            (description, done, id),
        )
        self.conn.commit()

    def delete_task_by_id(self, id):
        """
        Using SQL, deletes a task by id
        """
        self.conn.execute(
            """
            DELETE FROM tasks
            WHERE id = ?;
        """,
            (id,),
        )
        self.conn.commit()

    #-- SUBTASKS -------ONE TO MANY 
    
    def create_subtasks_table(self):
        try:
            self.conn.execute(
            """
                CREATE TABLE subtask(
                    id INTEGER PRIMARY KEY,
                    description TEXT NOT NULL, 
                    done BOOLEAN NOT NULL, 
                    task_id INTEGER NOT NULL, 
                    FOREIGN KEY (task_id) REFERENCES task(id)
                );
            """
            )
        except Exception as e:
            print(e)
        
    def get_all_subtasks(self):
        cursor = self.conn.execute("SELECT * FROM subtask")
        subtasks =  parse_cursor(cursor,['id','description','done','task_id'])
        return subtasks
        
    def insert_subtask(self,description,done,task_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO subtask(description,done,task_id) VALUES(?,?,?);
            """,(description,done,task_id)
        )
        self.conn.commit()
        return cursor.lastrowid 
    
    def get_subtask_by_id(self,id):
        cursor = self.conn.execute(
            """ 
                SELECT * FROM  subtask WHERE id = ?
            """,(id,)
        )
        return parse_cursor(cursor,['description','done','task_id'])
        return None 

    def get_subtasks_of_task(self,id):
        cursor = self.conn.execute(
            """ 
                SELECT * FROM subtask WHERE task_id = ?;
            """,(id,)
        )
        return parse_cursor(cursor,['description','done','task_id'])



DatabaseDriver = singleton(DatabaseDriver)