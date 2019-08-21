from model.dbhandler import DBHandler
from model.tag import Tag


class ToDo():
    """ToDo CRUD handler."""

    def __init__(self, params=None):
        self.db_handler = DBHandler(params)

    def print_todo(self, todo):
        for key, value in todo.items():
            if key == 'tags':
                print(key + ':')
                for tag in value:
                    for tagk, tagv in tag.items():
                        print('\t', tagk + ':', tagv)
                    print()
            else:
                print(key + ':')
                print('\t', value)

    def get_tags(self, todo_id):
        tags = self.db_handler.find("""
            SELECT tags.*
            FROM todos
            JOIN todo_tags
            ON  todo_tags.todo_id = todos.todo_id
            JOIN tags
            ON tags.tag_id = todo_tags.tag_id
            WHERE todos.todo_id = %s
            """, (todo_id,))
        return tags

    def prepare_tags(self, todos):
        tag_handler = Tag(self.db_handler.params)
        for todo in todos:
            tags = tag_handler.list(todo_id=todo['todo_id'])
            todo['tags'] = tags

    def add_tags(self, todo_id, tags):
        tags = self.db_handler.find("""
            SELECT tags.tag_id
            FROM tags
            WHERE tags.name IN %s
            ORDER BY tags.tag_id
        """, tuple(tags))

        for tag in tags:
            self.db_handler.insert("""
                INSERT INTO todo_tags(todo_id, tag_id, status)
                VALUES (%s, %s, %s)
                RETURNING todo_tags.todo_tag_id
            """, (todo_id, tag['tag_id'], 'active'))

    def create(self, title, summary=None, description=None, tags=None):
        insert_result = self.db_handler.insert("""
            INSERT INTO todos(title, summary, description)
            VALUES (%s, %s, %s)
            RETURNING todo_id
        """, (title, summary, description))
        todo_id = insert_result['todo_id']

        if tags is not None:
            self.add_tags(todo_id, tags)

        return todo_id

    def get(self, todo_id, include_tags=True):
        select_statement = """
            SELECT todos.*
            FROM todos
        """

        where_statements = [{
            'condition': 'todos.todo_id = %s',
            'data': todo_id
        }]

        final_query = self.db_handler.prepare_query(
            select=select_statement,
            where=where_statements
        )
        todo = self.db_handler.find_one(final_query)

        if include_tags:
            self.prepare_tags([todo])

        return todo

    def list(self, todo_ids=None, status=None, tags=None, include_tags=True):
        select_statement = """
            SELECT todos.*
            FROM todos
        """

        where_statements = []
        if status is not None:
            where_statements.append({
                'condition': 'todos.status = %s',
                'data': status
            })

        if todo_ids is not None:
            where_statements.append({
                'condition': 'todos.todo_id IN %s',
                'data': tuple(todo_ids)
            })

        joins_statements = []
        if tags is not None:
            joins_statements.extend([{
                'table': 'todo_tags',
                'on': 'todo_tags.todo_id = todos.todo_id'
            }, {
                'table': 'tags',
                'on': 'tags.tag_id = todo_tags.tag_id'
            }])
            where_statements.append({
                'condition': 'tags.name IN %s',
                'data': tuple(tags)
            })

        final_query = self.db_handler.prepare_query(
            select=select_statement,
            joins=joins_statements,
            where=where_statements,
            group_by='todos.todo_id',
            order_by='todos.todo_id'
        )
        todos = self.db_handler.find(final_query)

        if include_tags:
            self.prepare_tags(todos)

        return todos

    def remove_tags(self, todo_id, tag_ids):
        delete_statement = """
            DELETE FROM todo_tags
        """

        where_statements = [{
            'condition': 'todo_tags.todo_id = %s',
            'data': todo_id
        }]

        if tag_ids is not None:
            where_statements.append({
                'condition': 'todo_tags.tag_id IN %s',
                'data': tuple(tag_ids)
            })

        final_query = self.db_handler.prepare_query(
            delete=delete_statement,
            where=where_statements
        )
        self.db_handler.delete(final_query)

        return None
