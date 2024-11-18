from aws_portal.extensions import db


class Api(db.Model):
    """
    The api table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    """
    __tablename__ = "api"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name
        }

    def __repr__(self):
        return "<Api %s>" % self.name
