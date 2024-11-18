from aws_portal.extensions import db


class AccessGroup(db.Model):
    """
    The access_group table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    app_id: sqlalchemy.Column
        The primary key of the app that an access group grants permissions for.
    app: sqlalchemy.orm.relationship
    accounts: sqlalchemy.orm.relationship
    permissions: sqlalchemy.orm.relationship
        The permissions that an access group grants for an app.
    """
    __tablename__ = "access_group"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    app_id = db.Column(db.Integer, db.ForeignKey("app.id", ondelete="CASCADE"))
    app = db.relationship("App")

    # ignore archived accounts
    accounts = db.relationship(
        "JoinAccountAccessGroup",
        back_populates="access_group",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   AccessGroup.id == JoinAccountAccessGroup.access_group_id," +
            "   JoinAccountAccessGroup.account_id == Account.id," +
            "   Account.is_archived == False" +
            ")"
        )
    )

    permissions = db.relationship(
        "JoinAccessGroupPermission",
        back_populates="access_group",
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
            "app": self.app.meta,
            "permissions": [p.meta for p in self.permissions]
        }

    def __repr__(self):
        return "<AccessGroup %s>" % self.name
