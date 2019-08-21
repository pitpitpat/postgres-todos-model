import os
import psycopg2
import psycopg2.extras
from configparser import ConfigParser


class DBHandler():
    """Database connection handler."""

    def __init__(self, params=None):
        if params is None:
            self.params = self.config()
        else:
            self.params = params

    def config(self, filename='database.ini', section='postgresql'):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = dir_path + '/' + filename

        parser = ConfigParser()
        parser.read(file_path)

        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        return db

    def connect(self, params=None):
        try:
            self.connection = psycopg2.connect(**self.params)
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def close(self):
        if self.cursor is not None:
            self.cursor
        if self.connection is not None:
            self.connection.close()

    def commit_and_close(self):
        if self.cursor is not None:
            self.cursor
        if self.connection is not None:
            self.connection.commit()
            self.connection.close()

    def prepare_query(self, select=None, delete=None, joins=None, where=None, group_by=None, order_by=None):
        self.connect()

        query = ''
        if select:
            query = select
        elif delete:
            query = delete

        if joins:
            join_clause = ''
            for index, join in enumerate(joins):
                join_clause += ' JOIN ' + join['table']

                if 'on' in join:
                    join_clause += ' ON ' + join['on']
            query += join_clause

        query_data = []
        if where:
            where_clause = ' WHERE '
            for index, where_cond in enumerate(where):
                where_clause += where_cond['condition']

                if index != (len(where) - 1):
                    where_clause += ' and '

                if 'data' in where_cond:
                    query_data.append(where_cond['data'])
            query += where_clause

        if group_by:
            query += ' GROUP BY ' + group_by

        if order_by:
            query += ' ORDER BY ' + order_by

        prepared_query = self.cursor.mogrify(query, query_data)

        self.close()
        return prepared_query

    def insert(self, statement, values):
        self.connect()
        self.cursor.execute(statement, values)
        return_params = self.cursor.fetchone()
        self.commit_and_close()

        return return_params

    def find(self, statement, values=None):
        self.connect()
        if values is not None:
            self.cursor.execute(statement, (values,))
        else:
            self.cursor.execute(statement)

        results = self.cursor.fetchall()
        self.close()

        return results

    def find_one(self, statement, values=None):
        self.connect()
        if values is not None:
            self.cursor.execute(statement, (values,))
        else:
            self.cursor.execute(statement)

        result = self.cursor.fetchone()
        self.close()

        return result

    def delete(self, statement, values=None):
        self.connect()
        if values is not None:
            self.cursor.execute(statement, (values,))
        else:
            self.cursor.execute(statement)
        self.commit_and_close()
