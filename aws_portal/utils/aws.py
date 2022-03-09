from functools import reduce
import os
import re
import boto3
from boto3.dynamodb.conditions import Attr


class Connection:
    def __init__(self):
        self.__session = None

    def open_connection(self, resource):
        self.__session = boto3.resource(resource)

    @property
    def session(self):
        return self.__session


class Loader:
    config = {
        'DittiApp': {
            'User': os.getenv('AWS_TABLENAME_USER'),
            'Tap': os.getenv('AWS_TABLENAME_TAP')
        }
    }

    def __init__(self, app, tablekey):
        self.__app = app
        self.__tablekey = tablekey
        self.__table = None

    @classmethod
    def get_tablename(cls, app, tablekey):
        return cls.config[app][tablekey]

    def connect(self, connection):
        self.__session = connection.session

    def load_table(self):
        tablename = self.get_tablename(self.__app, self.__tablekey)
        self.__table = self.__session.Table(tablename)

    @property
    def table(self):
        return self.__table


class Updater:
    def __init__(self, app=None, tablekey=None):
        self.app = app
        self.tablekey = tablekey
        self.__key = None
        self.__update_expression = None
        self.__expression_attribute_values = None

    def set_key_from_query(self, q, pk='id'):
        res = Query(self.app, self.tablekey, q).scan()
        key = res['Items'][0][pk]
        self.__key = {pk: key}

    def get_key(self):
        return self.__key

    def set_expression(self, exp):
        e = reduce(lambda l, r: l + f' {r}=:{r[0]},', exp.keys(), 'set')[:-1]
        a = {':%s' % k[0]: str(v) for k, v in exp.items()}
        self.__update_expression = e
        self.__expression_attribute_values = a

    def get_update_expression(self):
        return self.__update_expression

    def get_expression_attribute_values(self):
        return self.__expression_attribute_values

    def update(self):
        if not (self.app and self.tablekey and self.__key):
            raise ValueError('app, tablekey, and key must be set')

        connection = Connection()
        connection.open_connection('dynamodb')
        loader = Loader(self.app, self.tablekey)
        loader.connect(connection)
        loader.load_table()
        res = loader.table.update_item(
            Key=self.__key,
            UpdateExpression=self.__update_expression,
            ExpressionAttributeValues=self.__expression_attribute_values,
            ReturnValues='UPDATED_NEW'
        )

        return res


class Column:
    def __init__(self, col):
        self.__col = col
        self.__switch = False

    def __eq__(self, other):
        return Attr(self.__col).eq(other)

    def __ne__(self, other):
        return Attr(self.__col).ne(other)

    def __lt__(self, other):
        return Attr(self.__col).lt(other)

    def __le__(self, other):
        return Attr(self.__col).lte(other)

    def __gt__(self, other):
        return Attr(self.__col).gt(other)

    def __ge__(self, other):
        return Attr(self.__col).gte(other)

    def __invert__(self):
        self.__switch = not self.__switch
        return ~Attr(self.__col).eq(self.__switch)

    def between(self, start, stop):
        return Attr(self.__col).between(start, stop)

    def begins_with(self, other):
        return Attr(self.__col).begins_with(other)

    def contains(self, other):
        return Attr(self.__col).contains(other)


class Scanner:
    def __init__(self, app, tablekey):
        self.__loader = Loader(app, tablekey)
        self.__filter = None

    def query(self, expression):
        self.__filter = expression
        return self

    def scan(self, connection=None, **kwargs):
        if kwargs is None:
            kwargs = {}

        if self.__filter is not None:
            kwargs.update({'FilterExpression': self.__filter})

        if connection is None:
            connection = Connection()
            connection.open_connection('dynamodb')

        self.__loader.connect(connection)
        self.__loader.load_table()
        result = self.__loader.table.scan(**kwargs)

        return result


class Query:
    invalid_chars = r'[^\w|\d|=|"|\-|:|\.|<|>|(|)|~|!]'
    blocks = r'((?<=\()[\w\d=<>"\-:.$~!]+(?=\)))'
    conditionals = r'(==|!=|<=|>=|<<|>>|BETWEEN|BEGINS|CONTAINS|~~|~)'
    comparitors = r'(AND|OR)'
    values = r'((?<=")[\w\d\-:.]+(?="))'
    keys = r'[a-z_]+(?=([^"]*"[^"]*")*[^"]*$)'

    def __init__(self, app, key, query):
        self.check_query(query)
        self.expression = self.build_query(query)
        self.app = app
        self.key = key

    def scan(self, **kwargs):
        return Scanner(self.app, self.key)\
            .query(self.expression)\
            .scan(**kwargs)

    @classmethod
    def check_query(cls, query):
        match = re.search(cls.invalid_chars, query)

        if match is not None:
            string = match.group(0)
            pos = match.start(0)

            raise ValueError(
                'Query contains invalid string at position %s: %s'
                % (pos, string)
            )

        return True

    @classmethod
    def build_query(cls, query):
        blocks = cls.build_blocks(query)
        expression = cls.build_expression(blocks)

        return expression

    @classmethod
    def build_blocks(cls, query, blocks=None):
        blocks = blocks or []

        match = re.findall(cls.blocks, query)
        if not match:
            blocks.append(query)
            return blocks

        for i, block in enumerate(match):
            _i = i + len(blocks)
            query = query.replace(f'({block})', '$%s' % _i)

        blocks.extend(match)
        return cls.build_blocks(query, blocks=blocks)

    @classmethod
    def build_expression(cls, blocks, expressions=None):
        expressions = expressions or []
        block = blocks[0]
        blocks = blocks[1:]
        expression = None

        strings = re.split(cls.comparitors, block)
        for i, string in enumerate(strings):
            if i % 2:
                continue

            if '$' in string:
                ix = int(string.replace('$', ''))
                _expression = expressions[ix]

            else:
                _expression = cls.get_expression_from_string(string)

            if not i:
                expression = _expression
                continue

            comparison = strings[i - 1]

            if comparison == 'OR':
                expression = expression | _expression

            elif comparison == 'AND':
                expression = expression & _expression

        expressions.append(expression)

        if not blocks:
            return expressions[-1]

        return cls.build_expression(blocks, expressions)

    @classmethod
    def get_expression_from_string(cls, string):
        key = re.search(cls.keys, string).group(0)
        condition = re.search(cls.conditionals, string).group(0)
        values = re.findall(cls.values, string) or ['']

        if condition == '==':
            expression = Column(key) == values.pop()

        elif condition == '!=':
            expression = Column(key) != values.pop()

        elif condition == '<=':
            expression = Column(key) <= values.pop()

        elif condition == '>=':
            expression = Column(key) >= values.pop()

        elif condition == '<<':
            expression = Column(key) < values.pop()

        elif condition == '>>':
            expression = Column(key) > values.pop()

        elif condition == 'BETWEEN':
            expression = Column(key).between(*values)

        elif condition == 'BEGINS':
            expression = Column(key).begins_with(values.pop())

        elif condition == 'CONTAINS':
            expression = Column(key).contains(values.pop())

        elif condition == '~':
            expression = ~Column(key)

        elif condition == '~~':
            expression = ~~Column(key)

        return expression
