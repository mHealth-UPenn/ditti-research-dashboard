import pytest
from aws_portal.utils.aws import Column, Connection, Loader, Query, Scanner


def assert_expression(exp, name, operator, *args):
    switch = True
    exp_operator = exp.expression_operator

    while exp.expression_operator == 'NOT':
        switch = not switch
        exp = exp.get_expression()['values'][0]

    if exp_operator == 'NOT':
        values = (switch,)

    else:
        values = exp.get_expression()['values'][1:]

    assert exp_operator == operator
    assert exp.get_expression()['values'][0].name == name
    assert values == args


class TestConnection:
    def test_open_connection(self):
        connection = Connection()
        assert connection.session is None

        connection.open_connection('dynamodb')
        assert connection.session is not None
        assert connection.session.meta.service_name == 'dynamodb'


class TestLoader:
    def test_get_tablename(self):
        for app in Loader.config.keys():
            for k, v in Loader.config[app].items():
                assert Loader.get_tablename(app, k) == v

    def test_load_table(self):
        connection = Connection()
        connection.open_connection('dynamodb')
        loader = Loader('DittiApp', 'User')
        loader.connect(connection)
        assert loader.table is None

        loader.load_table()
        tablename = Loader.get_tablename('DittiApp', 'User')
        assert loader.table is not None
        assert loader.table.name == tablename


class TestUpdater:
    def test_set_expression(self):
        foo = Updater()
        exp = {'information': 'foo'}
        foo.set_expression(exp)
        bar = 'set info.information=:i'
        baz = {':i': 'foo'}
        assert foo.get_update_expression == bar
        assert foo.get_expression_attribute_values == baz

    def test_update():
        query = 'user_permission_id==abc123'
        foo = Query('DittiApp', 'User', query)
        res = foo.scan()
        assert len(res['Items']) == 1
        assert 'information' in res['Items'][0]
        assert res['Items'][0]['information'] == ''

        key = {'user_permission_id': 'abc123'}
        bar = Updater('DittiApp', 'User', key)
        exp = {'information': 'foo'}
        bar.set_expression(exp)
        bar.update()
        res = foo.scan()
        assert len(res['Items']) == 1
        assert 'information' in res['Items'][0]
        assert res['Items'][0]['information'] == 'foo'

        exp = {'information': ''}
        bar.set_expression(exp)
        bar.update()
        res = foo.scan()
        assert len(res['Items']) == 1
        assert 'information' in res['Items'][0]
        assert res['Items'][0]['information'] == ''


class TestColumn:
    def test_eq(self):
        exp = Column('foo') == 'bar'
        assert_expression(exp, 'foo', '=', 'bar')

    def test_ne(self):
        exp = Column('foo') != 'bar'
        assert_expression(exp, 'foo', '<>', 'bar')

    def test_lt(self):
        exp = Column('foo') < 'bar'
        assert_expression(exp, 'foo', '<', 'bar')

    def test_le(self):
        exp = Column('foo') <= 'bar'
        assert_expression(exp, 'foo', '<=', 'bar')

    def test_gt(self):
        exp = Column('foo') > 'bar'
        assert_expression(exp, 'foo', '>', 'bar')

    def test_ge(self):
        exp = Column('foo') >= 'bar'
        assert_expression(exp, 'foo', '>=', 'bar')

    def test_invert(self):
        exp = ~Column('foo')
        assert_expression(exp, 'foo', 'NOT', False)

        exp = ~~Column('foo')
        assert_expression(exp, 'foo', 'NOT', True)

    def test_between(self):
        exp = Column('foo').between('bar', 'baz')
        assert_expression(exp, 'foo', 'BETWEEN', 'bar', 'baz')

    def test_begins_with(self):
        exp = Column('foo').begins_with('bar')
        assert_expression(exp, 'foo', 'begins_with', 'bar')

    def test_contains(self):
        exp = Column('foo').contains('bar')
        assert_expression(exp, 'foo', 'contains', 'bar')


class TestScanner:
    def test_query(self):
        exp = Column('user_permission_id') == 'abc123'
        res = Scanner('DittiApp', 'User').query(exp).scan()
        assert res['Count'] == 1
        assert res['ResponseMetadata']['HTTPStatusCode'] == 200

    def test_scan(self):
        res = Scanner('DittiApp', 'User').scan()
        assert res['Count']
        assert res['ResponseMetadata']['HTTPStatusCode'] == 200


class TestQuery:
    def test_scan(self):
        abc123 = 'user_permission_id=="abc123"'
        res = Query('DittiApp', 'User', abc123).scan()
        assert res['Count'] == 1
        assert res['ResponseMetadata']['HTTPStatusCode'] == 200

    def test_check_query(self):
        invalid = '#user_permission_id=="abc123"'

        with pytest.raises(ValueError):
            Query.check_query(invalid)

        valid = 'aA1="-:.<>()~!'
        assert Query.check_query(valid)

    def test_build_query(self):
        query = 'foo=="bar"'
        exp = Query.build_query(query)
        assert_expression(exp, 'foo', '=', 'bar')

    def test_build_blocks(self):
        query = '(a=="a"ORa=="b")AND(b=="a"AND(b=="b"ORb=="c"))'
        blocks = ['a=="a"ORa=="b"', 'b=="b"ORb=="c"', 'b=="a"AND$1', '$0AND$2']
        assert Query.build_blocks(query) == blocks

    def test_build_expression(self):
        blocks = ['foo=="bar"']
        exp = Query.build_expression(blocks)
        assert_expression(exp, 'foo', '=', 'bar')

    def test_get_expression_from_string_eq(self):
        exp = Query.get_expression_from_string('foo=="bar"')
        assert_expression(exp, 'foo', '=', 'bar')

    def test_get_expression_from_string_ne(self):
        exp = Query.get_expression_from_string('foo!="bar"')
        assert_expression(exp, 'foo', '<>', 'bar')

    def test_get_expression_from_string_lt(self):
        exp = Query.get_expression_from_string('foo<<"bar"')
        assert_expression(exp, 'foo', '<', 'bar')

    def test_get_expression_from_string_le(self):
        exp = Query.get_expression_from_string('foo<="bar"')
        assert_expression(exp, 'foo', '<=', 'bar')

    def test_get_expression_from_string_gt(self):
        exp = Query.get_expression_from_string('foo>>"bar"')
        assert_expression(exp, 'foo', '>', 'bar')

    def test_get_expression_from_string_ge(self):
        exp = Query.get_expression_from_string('foo>="bar"')
        assert_expression(exp, 'foo', '>=', 'bar')

    def test_get_expression_from_string_not(self):
        exp = Query.get_expression_from_string('~foo')
        assert_expression(exp, 'foo', 'NOT', False)

    def test_get_expression_from_string_not_not(self):
        exp = Query.get_expression_from_string('~~foo')
        assert_expression(exp, 'foo', 'NOT', True)

    def test_get_expression_from_string_between(self):
        exp = Query.get_expression_from_string('fooBETWEEN"bar""baz"')
        assert_expression(exp, 'foo', 'BETWEEN', 'bar', 'baz')

    def test_get_expression_from_string_begins_with(self):
        exp = Query.get_expression_from_string('fooBEGINS"bar"')
        assert_expression(exp, 'foo', 'begins_with', 'bar')

    def test_get_expression_from_string_contains(self):
        exp = Query.get_expression_from_string('fooCONTAINS"bar"')
        assert_expression(exp, 'foo', 'contains', 'bar')
