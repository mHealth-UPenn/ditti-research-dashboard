from moto import mock_aws
import pytest
import requests
from aws_portal.utils.aws import (
    Column, Connection, Loader, MutationClient, Query, Scanner, Updater
)


def assert_expression(exp, name, operator, *args):
    switch = True
    exp_operator = exp.expression_operator

    # If the top-level operator is AND (due to the deleted_exp filter), get the first value
    if exp_operator == "AND":
        exp = exp.get_expression()["values"][0]
        exp_operator = exp.expression_operator

    while exp.expression_operator == "NOT":
        switch = not switch
        exp = exp.get_expression()["values"][0]

    if exp_operator == "NOT":
        values = (switch,)
    else:
        values = exp.get_expression()["values"][1:]

    assert exp_operator == operator
    assert exp.get_expression()["values"][0].name == name
    assert values == args


@mock_aws
class TestMutationClient:
    def test_open_connection(self):
        foo = MutationClient()
        assert foo.get_connection() is None

        foo.open_connection()
        assert type(foo.get_connection()) is requests.sessions.Session

    def test_set_mutation(self):
        foo = MutationClient()
        assert foo.get_body() is None

        foo.set_mutation("foo", "bar", {"baz": "baz", "qux": "qux"})
        bar = {
            "query": "mutation($in:foo!){bar(input:$in){baz qux}}",
            "variables": "{\"in\": {\"baz\": \"baz\", \"qux\": \"qux\"}}"
        }

        assert foo.get_body() == bar

    def test_post_mutation_no_body(self):
        foo = MutationClient()
        foo.open_connection()
        assert foo.get_body() is None

        with pytest.raises(ValueError) as e:
            foo.post_mutation()

        bar = str(e.value)
        assert bar == "Mutation is not set. Call set_mutation() first."

    @pytest.mark.skip(reason="Must implement mock for graphql endpoint.")
    def test_post_mutation(self):
        foo = MutationClient()
        foo.open_connection()
        foo.set_mutation(
            "CreateUserPermissionInput",
            "createUserPermission",
            {
                "exp_time": "1900-01-01T09:00:00.000Z",
                "tap_permission": True,
                "team_email": "foo@email.com",
                "user_permission_id": "foo",
                "information": "foo"
            }
        )

        foo.post_mutation()

        query = "user_permission_id==\"foo\""
        bar = Query("User", query)
        res = bar.scan()
        assert len(res["Items"]) == 1
        assert "exp_time" in res["Items"][0]
        assert res["Items"][0]["exp_time"] == "1900-01-01T09:00:00.000Z"
        assert "tap_permission" in res["Items"][0]
        assert res["Items"][0]["tap_permission"]
        assert "team_email" in res["Items"][0]
        assert res["Items"][0]["team_email"] == "foo@email.com"
        assert "user_permission_id" in res["Items"][0]
        assert res["Items"][0]["user_permission_id"] == "foo"
        assert "information" in res["Items"][0]
        assert res["Items"][0]["information"] == "foo"

        connection = Connection()
        connection.open_connection("dynamodb")
        loader = Loader("User")
        loader.connect(connection)
        loader.load_table()
        res = loader.table.delete_item(Key={"id": res["Items"][0]["id"]})

        res = bar.scan()
        assert len(res["Items"]) == 0


@mock_aws
class TestConnection:
    def test_open_connection(self):
        connection = Connection()
        assert connection.session is None

        connection.open_connection("dynamodb")
        assert connection.session is not None
        assert connection.session.meta.service_name == "dynamodb"


@mock_aws
class TestLoader:
    def test_get_tablename(self):
        loader = Loader("foo")
        for k, v in loader.config.items():
            assert loader.get_tablename(k) == v

    def test_load_table(self):
        connection = Connection()
        connection.open_connection("dynamodb")
        loader = Loader("User")
        loader.connect(connection)
        assert loader.table is None

        loader.load_table()
        tablename = loader.get_tablename("User")
        assert loader.table is not None
        assert loader.table.name == tablename


class TestUpdater:
    def test_set_key_from_query(self, with_mocked_tables):
        query = "user_permission_id==\"abc123\""
        foo = Query("User", query)
        res = foo.scan()
        assert len(res["Items"]) == 1

        baz = Updater("User")
        baz.set_key_from_query(query)
        bar = res["Items"][0]["id"]
        assert baz.get_key() == {"id": bar}

    @mock_aws
    def test_set_expression(self):
        foo = Updater()
        exp = {"information": "foo"}
        foo.set_expression(exp)
        bar = "SET information=:in"
        baz = {":in": "foo"}
        assert foo.get_update_expression() == bar
        assert foo.get_expression_attribute_values() == baz

    @mock_aws
    def test_update_exception(self):
        foo = Updater()

        with pytest.raises(ValueError) as e:
            foo.update()

        assert str(e.value) == "tablekey and key must be set"

    def test_update(self, with_mocked_tables):
        query = "user_permission_id==\"abc123\""
        foo = Query("User", query)
        res = foo.scan()
        assert len(res["Items"]) == 1
        assert "information" in res["Items"][0]
        assert res["Items"][0]["information"] == ""

        bar = Updater("User")
        bar.set_key_from_query(query)
        exp = {"information": "foo"}
        bar.set_expression(exp)
        bar.update()
        res = foo.scan()
        assert len(res["Items"]) == 1
        assert "information" in res["Items"][0]
        assert res["Items"][0]["information"] == "foo"

        exp = {"information": ""}
        bar.set_expression(exp)
        bar.update()
        res = foo.scan()
        assert len(res["Items"]) == 1
        assert "information" in res["Items"][0]
        assert res["Items"][0]["information"] == ""


class TestColumn:
    def test_eq(self):
        exp = Column("foo") == "bar"
        assert_expression(exp, "foo", "=", "bar")

    def test_ne(self):
        exp = Column("foo") != "bar"
        assert_expression(exp, "foo", "<>", "bar")

    def test_lt(self):
        exp = Column("foo") < "bar"
        assert_expression(exp, "foo", "<", "bar")

    def test_le(self):
        exp = Column("foo") <= "bar"
        assert_expression(exp, "foo", "<=", "bar")

    def test_gt(self):
        exp = Column("foo") > "bar"
        assert_expression(exp, "foo", ">", "bar")

    def test_ge(self):
        exp = Column("foo") >= "bar"
        assert_expression(exp, "foo", ">=", "bar")

    def test_invert(self):
        exp = ~Column("foo")
        assert_expression(exp, "foo", "NOT", False)

        exp = ~~Column("foo")
        assert_expression(exp, "foo", "NOT", True)

    def test_between(self):
        exp = Column("foo").between("bar", "baz")
        assert_expression(exp, "foo", "BETWEEN", "bar", "baz")

    def test_begins_with(self):
        exp = Column("foo").begins_with("bar")
        assert_expression(exp, "foo", "begins_with", "bar")

    def test_contains(self):
        exp = Column("foo").contains("bar")
        assert_expression(exp, "foo", "contains", "bar")


class TestScanner:
    def test_query(self, with_mocked_tables):
        exp = Column("user_permission_id") == "abc123"
        res = Scanner("User").query(exp).scan()
        assert res["Count"] == 1
        assert res["ResponseMetadata"]["HTTPStatusCode"] == 200

    def test_scan(self, with_mocked_tables):
        res = Scanner("User").scan()
        assert res["Count"]
        assert res["ResponseMetadata"]["HTTPStatusCode"] == 200


class TestQuery:
    def test_scan(self, with_mocked_tables):
        abc123 = "user_permission_id==\"abc123\""
        res = Query("User", abc123).scan()
        assert "Items" in res
        assert len(res["Items"]) == 1

    @mock_aws
    def test_check_query(self):
        invalid = "#user_permission_id==\"abc123\""

        with pytest.raises(ValueError):
            Query.check_query(invalid)

        valid = "aA1=\"-:.<>()~!"
        assert Query.check_query(valid)

    @mock_aws
    def test_build_query(self):
        query = "foo==\"bar\""
        exp = Query.build_query(query)
        assert_expression(exp, "foo", "=", "bar")

    @mock_aws
    def test_build_blocks(self):
        query = "(a==\"a\"ORa==\"b\")AND(b==\"a\"AND(b==\"b\"ORb==\"c\"))"
        blocks = ["a==\"a\"ORa==\"b\"",
                  "b==\"b\"ORb==\"c\"", "b==\"a\"AND$1", "$0AND$2"]
        assert Query.build_blocks(query) == blocks

    @mock_aws
    def test_build_expression(self):
        blocks = ["foo==\"bar\""]
        exp = Query.build_expression(blocks)
        assert_expression(exp, "foo", "=", "bar")

    @mock_aws
    def test_get_expression_from_string_eq(self):
        exp = Query.get_expression_from_string("foo==\"bar\"")
        assert_expression(exp, "foo", "=", "bar")

    @mock_aws
    def test_get_expression_from_string_ne(self):
        exp = Query.get_expression_from_string("foo!=\"bar\"")
        assert_expression(exp, "foo", "<>", "bar")

    @mock_aws
    def test_get_expression_from_string_lt(self):
        exp = Query.get_expression_from_string("foo<<\"bar\"")
        assert_expression(exp, "foo", "<", "bar")

    @mock_aws
    def test_get_expression_from_string_le(self):
        exp = Query.get_expression_from_string("foo<=\"bar\"")
        assert_expression(exp, "foo", "<=", "bar")

    @mock_aws
    def test_get_expression_from_string_gt(self):
        exp = Query.get_expression_from_string("foo>>\"bar\"")
        assert_expression(exp, "foo", ">", "bar")

    @mock_aws
    def test_get_expression_from_string_ge(self):
        exp = Query.get_expression_from_string("foo>=\"bar\"")
        assert_expression(exp, "foo", ">=", "bar")

    @mock_aws
    def test_get_expression_from_string_not(self):
        exp = Query.get_expression_from_string("~\"foo\"")
        assert_expression(exp, "foo", "NOT", False)

    @mock_aws
    def test_get_expression_from_string_not_not(self):
        exp = Query.get_expression_from_string("~~\"foo\"")
        assert_expression(exp, "foo", "NOT", True)

    @mock_aws
    def test_get_expression_from_string_between(self):
        exp = Query.get_expression_from_string("fooBETWEEN\"bar\"\"baz\"")
        assert_expression(exp, "foo", "BETWEEN", "bar", "baz")

    @mock_aws
    def test_get_expression_from_string_begins_with(self):
        exp = Query.get_expression_from_string("fooBEGINS\"bar\"")
        assert_expression(exp, "foo", "begins_with", "bar")

    @mock_aws
    def test_get_expression_from_string_contains(self):
        exp = Query.get_expression_from_string("fooCONTAINS\"bar\"")
        assert_expression(exp, "foo", "contains", "bar")
