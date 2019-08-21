from model.dbhandler import DBHandler


class Tag():
    """Tag CRUD handler."""

    def __init__(self, params=None):
        self.db_handler = DBHandler(params)

    def list(self, status=None, todo_id=None):
        select_query = """
            SELECT tags.*
            FROM tags
        """

        joins = []
        where = []
        if status is not None:
            where.append({
                'condition': 'tags.status = %s',
                'data': status
            })

        if todo_id is not None:
            joins.extend([{
                'table': 'todo_tags',
                'on': 'todo_tags.tag_id = tags.tag_id'
            }, {
                'table': 'todos',
                'on': 'todos.todo_id = todo_tags.todo_id'
            }])
            where.append({
                'condition': 'todos.todo_id = %s',
                'data': todo_id
            })

        find_query = self.db_handler.prepare_query(
            select=select_query,
            joins=joins,
            where=where,
            group_by='tags.tag_id',
            order_by='tags.tag_id'
        )

        tags = self.db_handler.find(find_query)
        return tags
