from sqlalchemy import func, tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from aws_portal.extensions import bcrypt, db

from .joins import JoinAccountAccessGroup, JoinAccountStudy
from ..study.study_model import Study
from ..auth.permission import Permission
from ..auth.joins import JoinAccountAccessGroup, JoinAccountStudy, JoinAccessGroupPermission, JoinRolePermission
from ..auth.access_group import AccessGroup
from ..auth.role import Role


class Account(db.Model):
    """
    The account table mappeing class.

    Vars
    ----
    id: sqlalchemy.Column
    public_id: sqlalchemy.Column
        A random string to be used for JWT authentication, e.g.,
        `public_id=str(uuid.uuid4())`.
    created_on: sqlalchemy.Column
        The timestamp of the account"s creation, e.g., `datetime.now(UTC)`.
        The created_on value cannot be modified.
    last_login: sqlalchemy.Column
    first_name: sqlalchemy.Column
    last_name: sqlalchemy.Column
    email: sqlalchemy.Column
    phone_number: sqlalchemy.Column
    is_confirmed: sqlalchemy.Column
        Whether the account holder has logged in and set their password.
    is_archived: sqlalchemy.Column
    access_groups: sqlalchemy.orm.relationship
    studies: sqlalchemy.orm.relationship
    """
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String, nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String, nullable=True, unique=True)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    _password = db.Column(db.String, nullable=False)

    # ignore archived access groups
    access_groups = db.relationship(
        "JoinAccountAccessGroup",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   Account.id == JoinAccountAccessGroup.account_id," +
            "   JoinAccountAccessGroup.access_group_id == AccessGroup.id," +
            "   AccessGroup.is_archived == False" +
            ")"
        )
    )

    # ignore archived studies
    studies = db.relationship(
        "JoinAccountStudy",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   Account.id == JoinAccountStudy.account_id," +
            "   JoinAccountStudy.study_id == Study.id," +
            "   Study.is_archived == False" +
            ")"
        )
    )

    @validates("created_on")
    def validate_created_on(self, key, val):
        """
        Make the created_on column read-only.
        """
        if self.created_on:
            raise ValueError("Account.created_on cannot be modified.")

        return val

    @hybrid_property
    def full_name(self):
        """
        str: The full name of the account holder
        """
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        return func.concat(cls.first_name, " ", cls.last_name)

    @hybrid_property
    def password(self):
        """
        str: The account holder"s password
        """
        return self._password

    @password.setter
    def password(self, val):
        """
        Hashes the password using bcrypt
        """
        password_hash = bcrypt.generate_password_hash(val).decode("utf-8")
        self._password = password_hash
        return True

    def check_password(self, val):
        """
        Whether a password matches the account holder"s password.

        Args
        ----
        val: str
            The password to check.

        Returns
        -------
        bool
        """
        return bcrypt.check_password_hash(self._password, val)

    def get_permissions(self, app_id, study_id=None):
        """
        Get all of an account"s permissions for an app and optionally for a
        study.

        Args
        ----
        app_id: int
            The app"s primary key.
        study_id: int (optional)
            The study"s primary key.

        Returns
        -------
        """

        # query all permissions that are granted to the account by access
        # groups that grant access to the app
        q1 = Permission.query.join(JoinAccessGroupPermission)\
            .join(AccessGroup)\
            .filter(AccessGroup.app_id == app_id)\
            .join(JoinAccountAccessGroup)\
            .filter(
                (~AccessGroup.is_archived) &
                (JoinAccountAccessGroup.account_id == self.id)
        )

        # if a study id was passed and the study is not archived
        if study_id and not Study.query.get(study_id).is_archived:

            # query all permissions that are granted to the account by the
            # study
            q2 = Permission.query.join(JoinRolePermission)\
                .join(Role)\
                .join(JoinAccountStudy, Role.id == JoinAccountStudy.role_id)\
                .filter(
                    JoinAccountStudy.primary_key == tuple_(self.id, study_id)
            )

            # return the union of all permission for the app and study
            permissions = q1.union(q2)

        else:

            # return all permissions for the app
            permissions = q1

        return permissions

    def validate_ask(self, action, resource, permissions):
        """
        Validate a request using a set of permissions

        Args
        ----
        action: str
        resource: str
        permissions:

        Raises
        ------
        ValueError
            If the account has no permissions that satisfy the request.
        """

        # build a query using the requested action and resource
        query = Permission.definition == tuple_(action, resource)

        # also check if the account has wildcard permissions
        query = query | (Permission.definition == tuple_(action, "*"))
        query = query | (Permission.definition == tuple_("*", resource))
        query = query | (Permission.definition == tuple_("*", "*"))

        # filter the account"s permissions
        valid = permissions.filter(query).first()

        # if no permissions were found
        if valid is None:
            raise ValueError("Unauthorized Ask")

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "createdOn": self.created_on,
            "lastLogin": self.last_login,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "phoneNumber": self.phone_number,
            "isConfirmed": self.is_confirmed,
            "accessGroups": [j.access_group.meta for j in self.access_groups],
            "studies": [s.meta for s in self.studies]
        }

    def __repr__(self):
        return "<Account %s>" % self.email
