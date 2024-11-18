from sqlalchemy import select, tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql.schema import UniqueConstraint
from aws_portal.extensions import db


class Permission(db.Model):
    """
    The permission table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    """
    __tablename__ = "permission"

    # ensure the action-resource combination is unique.
    __table_args__ = (UniqueConstraint("_action_id", "_resource_id"),)
    id = db.Column(db.Integer, primary_key=True)

    _action_id = db.Column(
        db.Integer,
        db.ForeignKey("action.id", ondelete="CASCADE")
    )

    _resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resource.id", ondelete="CASCADE")
    )

    _action = db.relationship("Action")
    _resource = db.relationship("Resource")

    @hybrid_property
    def action(self):
        """
        str: an entry's action
        """
        return self._action.value

    @action.setter
    def action(self, value):
        q = Action.query.filter(Action.value == value)

        # if the action does not exist, create a new action
        action = q.first() or Action(value=value)
        db.session.add(action)
        self._action = action

    @action.expression
    def action(cls):
        return select(Action.value)\
            .where(Action.id == cls._action_id)\
            .scalar_subquery()

    @hybrid_property
    def resource(self):
        """
        str: an entry's resource
        """
        return self._resource.value

    @resource.setter
    def resource(self, value):
        q = Resource.query.filter(Resource.value == value)

        # if the resource does not exist, create a new resource
        resource = q.first() or Resource(value=value)
        db.session.add(resource)
        self._resource = resource

    @resource.expression
    def resource(cls):
        return select(Resource.value)\
            .where(Resource.id == cls._resource_id)\
            .scalar_subquery()

    @validates("_action_id")
    def validate_action(self, key, val):
        """
        Ensure an entry's action cannot be modified.
        """
        if self._action_id is not None:
            raise ValueError("permission.action cannot be modified.")

        return val

    @validates("_resource_id")
    def validate_resource(self, key, val):
        """
        Ensure an entry's resource cannot be modified.
        """
        if self._resource_id is not None:
            raise ValueError("permission.resource cannot be modified.")

        return val

    @hybrid_property
    def definition(self):
        """
        tuple of str: an entry's (action, resource) definition
        """
        return self.action, self.resource

    @definition.expression
    def definition(cls):
        return tuple_(
            select(Action.value)
            .where(Action.id == cls._action_id)
            .scalar_subquery(),
            select(Resource.value)
            .where(Resource.id == cls._resource_id)
            .scalar_subquery()
        )

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "action": self.action,
            "resource": self.resource
        }

    def __repr__(self):
        return "<Permission %s %s>" % self.definition


class Action(db.Model):
    """
    The action table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    value: sqlalchemy.Column
    """
    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "value": self.value
        }

    def __repr__(self):
        return "<Action %s>" % self.value


class Resource(db.Model):
    """
    The resource table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    value: sqlalchemy.Column
    """
    __tablename__ = "resource"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "value": self.value
        }

    def __repr__(self):
        return "<Resource %s>" % self.value
