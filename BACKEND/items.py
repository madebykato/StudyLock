from BACKEND.database import Database

class ItemsManager(Database):

    def add_item(self, user_id, course_id, title, item_type, deadline=None, room=None):
        if not title or not title.strip():
            raise ValueError("Title cannot be empty.")

        if not item_type or not item_type.strip():
            raise ValueError("Item type cannot be empty.")

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO items 
                (user_id, course_id, title, item_type, deadline, room, completed)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (
                user_id,
                course_id,
                title.strip(),
                item_type.strip(),
                deadline,
                room
            ))
            conn.commit()
            return cursor.lastrowid

    def get_items(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    items.id,
                    items.title,
                    items.item_type,
                    courses.course_name,
                    items.deadline,
                    items.room,
                    items.completed
                FROM items
                LEFT JOIN courses ON items.course_id = courses.id
                WHERE items.user_id = ?
                ORDER BY 
                    items.completed ASC,
                    date(items.deadline) ASC
            """, (user_id,))
            return cursor.fetchall()

    def get_items_by_type(self, user_id, item_type):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    items.id,
                    items.title,
                    items.item_type,
                    courses.course_name,
                    items.deadline,
                    items.room,
                    items.completed
                FROM items
                LEFT JOIN courses ON items.course_id = courses.id
                WHERE items.user_id = ?
                AND items.item_type = ?
                ORDER BY 
                    items.completed ASC,
                    date(items.deadline) ASC
            """, (user_id, item_type))
            return cursor.fetchall()

    def get_items_by_course(self, user_id, course_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    items.id,
                    items.title,
                    items.item_type,
                    courses.course_name,
                    items.deadline,
                    items.room,
                    items.completed
                FROM items
                LEFT JOIN courses ON items.course_id = courses.id
                WHERE items.user_id = ?
                AND items.course_id = ?
                ORDER BY 
                    items.completed ASC,
                    date(items.deadline) ASC
            """, (user_id, course_id))
            return cursor.fetchall()

    def mark_completed(self, user_id, item_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE items
                SET completed = 1,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                AND user_id = ?
            """, (item_id, user_id))
            conn.commit()

    def mark_incomplete(self, user_id, item_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE items
                SET completed = 0,
                    completed_at = NULL
                WHERE id = ?
                AND user_id = ?
            """, (item_id, user_id))
            conn.commit()

    def delete_item(self, user_id, item_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM items
                WHERE id = ?
                AND user_id = ?
            """, (item_id, user_id))
            conn.commit()

    def get_next_deadline(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    items.id,
                    items.title,
                    items.item_type,
                    courses.course_name,
                    items.deadline,
                    items.room
                FROM items
                LEFT JOIN courses ON items.course_id = courses.id
                WHERE items.user_id = ?
                AND items.completed = 0
                AND items.deadline IS NOT NULL
                AND date(items.deadline) >= date('now')
                ORDER BY date(items.deadline) ASC
                LIMIT 1
            """, (user_id,))
            return cursor.fetchone()

    def get_days_until_deadline(self, user_id, item_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    CAST(julianday(deadline) - julianday(date('now')) AS INTEGER)
                FROM items
                WHERE user_id = ?
                AND id = ?
                AND deadline IS NOT NULL
            """, (user_id, item_id))

            row = cursor.fetchone()

            if row is None or row[0] is None:
                return None

            return row[0]

    def get_countdown_text(self, user_id, item_id):
        days_left = self.get_days_until_deadline(user_id, item_id)

        if days_left is None:
            return "No deadline"

        if days_left > 1:
            return f"{days_left} days left"

        if days_left == 1:
            return "1 day left"

        if days_left == 0:
            return "Due today"

        if days_left == -1:
            return "Overdue by 1 day"
        return f"Overdue by {abs(days_left)} days"

    def count_total_items(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM items
                WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchone()[0]

    def count_completed_items(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM items
                WHERE user_id = ?
                AND completed = 1
            """, (user_id,))
            return cursor.fetchone()[0]

    def count_current_items(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM items
                WHERE user_id = ?
                AND completed = 0
            """, (user_id,))
            return cursor.fetchone()[0]

    def count_items_by_type(self, user_id, item_type):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM items
                WHERE user_id = ?
                AND item_type = ?
            """, (user_id, item_type))
            return cursor.fetchone()[0]

    def get_item_types(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT item_type
                FROM items
                WHERE user_id = ?
                ORDER BY item_type
            """, (user_id,))
            return cursor.fetchall()