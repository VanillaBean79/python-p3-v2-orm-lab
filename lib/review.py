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

    @property
    def year(self):
        """Return the year of the reivew."""
        return self._year
    
    @year.setter
    def year(self, value):
        """Set the year for review, ensuring it's an integer."""
        if not isinstance(value, int):
            raise ValueError(f"Year must be an integer.")
        if value < 2000:
            raise ValueError(f"Year must be greater or equal to 2000, got {value}.")
        self._year = value

    @property
    def summary(self):
        """Return the summary of the review."""
        return self._summary

    @summary.setter
    def summary(self, value):
        """Set the summary for the review, ensuring it's not empty."""
        if not value or len(value.strip()) == 0:
            raise ValueError("Summary must not be empty.")
        self._summary = value

    @property
    def employee_id(self):
        """Return the employee_id associated with this review."""
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        """Set the employee_id for the review, ensuring it's a valid employee ID."""
        from employee import Employee 
        
        
        sql = "SELECT COUNT(*) FROM employees WHERE id = ?"
        CURSOR.execute(sql, (value,))
        result = CURSOR.fetchone()

        if result[0] == 0:
            raise ValueError(f"Employee with ID {value} does not exist.")
        
        self._employee_id = value

    

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        if self.id is None:
        # If there's no id, we're inserting a new review
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
             """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
        
            self.id = CURSOR.lastrowid
        
            Review.all[self.id] = self
        else:
            sql = """
             UPDATE reviews
             SET year = ?, summary = ?, employee_id = ?
             WHERE id = ?
             """

            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review
        
    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
       
        return cls(year=row[1], summary=row[2], employee_id=row[3], id=row[0])
        
   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        else:
            return None 
    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ? 
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = """
            DELETE FROM reviews
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Review.all:
            del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = """
            SELECT * FROM reviews
        """
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()

        return [cls.instance_from_db(row) for row in rows ]

