from aws_portal.extensions import db


class Study(db.Model):
    """
    The study table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    acronym: sqlalchemy.Column
    ditti_id: sqlalchemy.Column
    email: sqlalchemy.Column
    default_expiry_delta: sqlalchemy.Column
        The default amount of time in number of days that a subject is enrolled
        in the study. A JoinStudySubjectStudy's expires_on column will be automatically set
        according to this value.
    consent_information: sqlalchemy.Column
        The consent text to show to a study subject.
    is_archived: sqlalchemy.Column
    data_summary: sqlalchemy.Column
        Text describing why we are collecting participants data.
    is_qi: sqlalchemy.Column
        Indicates if the study is QI (Quality Improvement), defaults to False.
    roles: sqlalchemy.orm.relationship
    """
    __tablename__ = "study"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    acronym = db.Column(db.String, nullable=False, unique=True)
    ditti_id = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    default_expiry_delta = db.Column(db.Integer, nullable=False)
    consent_information = db.Column(db.String)
    data_summary = db.Column(db.Text)
    is_qi = db.Column(db.Boolean, default=False, nullable=False)

    roles = db.relationship("JoinStudyRole", cascade="all, delete-orphan")

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "acronym": self.acronym,
            "dittiId": self.ditti_id,
            "email": self.email,
            "roles": [r.meta for r in self.roles],
            "dataSummary": self.data_summary,
            "isQi": self.is_qi
        }

    def __repr__(self):
        return "<Study %s>" % self.acronym
