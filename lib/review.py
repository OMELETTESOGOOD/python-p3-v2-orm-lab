# lib/review.py
from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:

    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee: {self.employee_id}>"

    # --- year property ---
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be >= 2000")
        self._year = value

    # --- summary property ---
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str):
            raise ValueError("Summary must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Summary cannot be empty")
        self._summary = value

    # --- employee_id property ---
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise ValueError("employee_id must be an integer")
        if not Employee.find_by_id(value):
            raise ValueError("employee_id must reference a valid Employee in the database")
        self._employee_id = value

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)"
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review_id, year, summary, employee_id = row
        review = cls.all.get(review_id)
        if review:
            review.year = year
            review.summary = summary
            review.employee_id = employee_id
        else:
            review = cls(year, summary, employee_id, review_id)
            cls.all[review_id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        sql = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
        type(self).all[self.id] = self

    def delete(self):
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in type(self).all:
            del type(self).all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM reviews").fetchall()
        return [cls.instance_from_db(row) for row in rows]
