from aws_portal.extensions import db


class Role(db.Model):
    """
    The role table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    permissions: sqlalchemy.orm.relationship
    """
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    permissions = db.relationship(
        "JoinRolePermission",
        back_populates="role",
        cascade="all, delete-orphan"
    )

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "permissions": [p.meta for p in self.permissions]
        }

    def __repr__(self):
        return "<Role %s>" % self.name
