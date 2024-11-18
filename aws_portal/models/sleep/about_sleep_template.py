from aws_portal.extensions import db


class AboutSleepTemplate(db.Model):
    """
    The about_sleep_template table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    text: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    """
    __tablename__ = "about_sleep_template"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    text = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "text": self.text
        }

    def __repr__(self):
        return "<AboutSleepTemplate %s>" % self.name
