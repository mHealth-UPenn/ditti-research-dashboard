from sqlalchemy import func
from aws_portal.extensions import db


class BlockedToken(db.Model):
    """
    The blocked_token table mapping class. This is used to log users out using
    JWT tokens.

    Vars
    ----
    id: sqlalchemy.Column
    jti: sqlalchemy.Column
        The token to block.
    created_on: sqlalchemy.Column
    """
    __tablename__ = "blocked_token"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return "<BlockedToken %s>" % self.id
