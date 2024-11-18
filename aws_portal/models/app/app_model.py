from aws_portal.extensions import db


class App(db.Model):
    """
    The app table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    """
    __tablename__ = "app"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

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
        return "<App %s>" % self.name
