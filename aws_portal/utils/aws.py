from functools import reduce
import json
import os
import re
import requests
import boto3
from boto3.dynamodb.conditions import Attr
from requests_aws4auth import AWS4Auth


class MutationClient:
    """
    The client that makes mutation requests to AWS AppSync

    Vars
    ----
    f_string: str
        used for formatting the mutation request body
    headers: dict
        used to validate the mutation request
    """
    f_string = 'mutation($in:%(inp)s!){%(fun)s(input:$in){%(var)s}}'

    def __init__(self):
        self.__body = None
        self.__conn = None

    def get_body(self):
        """
        Returns
        -------
        str: the formatted mutation request body
        """
        return self.__body

    def get_connection(self):
        """
        Returns
        -------
        http.client.HTTPSConnection: the connection to AppSync
        """
        return self.__conn

    def open_connection(self):
        """
        Initialize an HTTP connection to AppSync
        """
        self.__conn = requests.Session()
        self.__conn.auth = AWS4Auth(
            os.getenv('APPSYNC_ACCESS_KEY'),
            os.getenv('APPSYNC_SECRET_KEY'),
            'us-east-1',
            'appsync'
        )

    def set_mutation(self, inp, fun, var):
        """
        Set the mutation request body. See AWS AppSync documentation for more
        details on how the mutation request is formatted

        Args
        ----
        inp: str
            the name of the input variable
        fun: str
            the name of the function
        var: str
            the value of the variable
        """
        fmt = {'inp': inp, 'fun': fun, 'var': ' '.join(var.keys())}
        query = self.f_string % fmt
        self.__body = {
            "query": query,
            "variables": "{\"in\": %s}" % json.dumps(var)
        }

    def post_mutation(self):
        """
        POST the mutation request

        Returns
        -------
        str: the response from AppSync

        Raises
        ------
        ValueError
            if the mutation was not set before calling
        """
        if self.__conn is None:
            self.open_connection()

        if self.__body is None:
            raise ValueError('Mutation is not set. Call set_mutation() first.')

        res = self.__conn.request(
            'POST',
            os.getenv('APP_SYNC_HOST'),
            json=self.__body
        )

        return res.text


class Connection:
    """
    A connection with an AWS resource
    """
    def __init__(self):
        self.__session = None

    def open_connection(self, resource):
        """
        Open a connection with a given resource

        Args
        ----
        resource: str
            the name of the resource
        """
        self.__session = boto3.resource(resource)

    @property
    def session(self):
        """
        boto3.resource: an AWS resource session
        """
        return self.__session


class Loader:
    """
    Loads a dynamodb table

    Args
    ----
    tablekey: the short name of the table (User, Tap, etc.)
    """
    def __init__(self, tablekey):
        self.__tablekey = tablekey
        self.__table = None
        self.config = {
            'User': os.getenv('AWS_TABLENAME_USER'),
            'Tap': os.getenv('AWS_TABLENAME_TAP')
        }

    def get_tablename(self, tablekey):
        """
        Get the full name of a table as it appears on dynamodb

        Args
        ----
        tablekey: str
            the short name of the table (User, Tap, etc.)
        
        Returns
        -------
        str: the full name of the table as it appears on dynamodb
        """
        return self.config[tablekey]

    def connect(self, connection):
        """
        Connect to an AWS session
        """
        self.__session = connection.session

    def load_table(self):
        """
        Load the table
        """
        tablename = self.get_tablename(self.__tablekey)
        self.__table = self.__session.Table(tablename)

    @property
    def table(self):
        """
        DynamoDB.Table
        """
        return self.__table


class Updater:
    """
    Updates an item's value on a dynamodb table

    Args
    ----
    tablekey: the short name of the table (User, Tap, etc., optional)
    """
    def __init__(self, tablekey=None):
        self.tablekey = tablekey
        self.__key = None
        self.__update_expression = None
        self.__expression_attribute_values = None

    def set_key_from_query(self, q, pk='id'):
        """
        Set the primary key of the item to update using the primary key of the
        first result from a query. This function assumes the query is against a
        column of unique values

        Args
        ----
        q: str
            The query to make
        pk: str (optional)
            The name of the table's primary key, default 'id'
        """
        res = Query(self.tablekey, q).scan()
        key = res['Items'][0][pk]
        self.__key = {pk: key}

    def get_key(self):
        """
        Returns
        -------
        str
        """
        return self.__key

    def set_expression(self, exp):
        """
        Set the update expression. See boto3 documentation for more information
        about how dynamodb update expressions are formatted

        Args
        ----
        exp: dict
            A set of key, value pairs where the key is the name of the column
            to update and the value is the new value to update the column
            with. Any number of key, value pairs can be passed to this function
        """
        e = reduce(lambda l, r: l + f' {r}=:{r[0] + r[1]},', exp.keys(), 'SET')
        a = {':%s' % k[0] + k[1]: v for k, v in exp.items()}
        self.__update_expression = e[:-1]
        self.__expression_attribute_values = a

    def get_update_expression(self):
        """
        Returns
        -------
        str
        """
        return self.__update_expression

    def get_expression_attribute_values(self):
        """
        Returns
        -------
        dict
        """
        return self.__expression_attribute_values

    def update(self):
        """
        Update the table

        Raises
        ------
        ValueError
            If tablekey or key is not set

        Returns
        ------
        dict
            The return value of DynamoDB.Table.update_items
        """
        if not (self.tablekey and self.__key):
            raise ValueError('tablekey and key must be set')

        connection = Connection()
        connection.open_connection('dynamodb')
        loader = Loader(self.tablekey)
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
    """
    A helper class for dynamodb columns that handles comparison operations

    Args
    ----
    col: str
        The name of the column
    """
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
    """
    Scans a dynamodb table

    Args
    ----
    tablekey: str
        The short name of the table (User, Tap, etc.)
    """
    def __init__(self, tablekey):
        self.__loader = Loader(tablekey)
        self.__filter = None

    def query(self, expression):
        """
        Sets the query to scan with

        Args
        ----
        expression: str

        Returns
        -------
        self
        """
        self.__filter = expression
        return self

    def scan(self, connection=None, **kwargs):
        """
        Scan the table

        Args
        ----
        connection: Connection (optional)
        kwargs
            optional arguments to pass to DynamoDB.Table.Scan

        Returns
        -------
        dict
            The return value of DynamoDB.Table.Scan
        """
        if kwargs is None:
            kwargs = {}

        # if a filter was set
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
    """
    Handles queries against a dynamodb table

    Args
    ----
    key: str 
        The short name of the table (User, Tap, etc.)
    query: str (optional)
        The expression to query the table with, for example:
            '(a=="a"ORa=="b")AND(b=="a"AND(b=="b"ORb=="c"))'
        Valid conditionals include:
            == - equals
            != - not equals
            <= - less than or equal to
            >= - greater than or equal to
            << - less than
            >> - greater than
            BETWEEN - between two values, e.g., 'fooBETWEEN"bar""baz"'
            BEGINS - will return results that begin with a given value
            CONTAINS - will return results that contain a given value
            ~~ - will return results that are true
            ~ - will return results that are false
        Expressions are evaluated by paranthetical sub-expressions first, then
        from left to right. Expressions can only contain these characters:
            a-zA-Z0-9_-=":.<>()~!

    Vars
    ----
    invalid_chars: str
        a regex string for identifying invalid chatacters
    blocks: str
        a regex string for extracting paranthetical blocks
    conditionals: str
        a regex string for identifying conditionals
    comparitors: str
        a regex string for identifying comparitors
    values: str
        a regex string for values
    keys: str
        a regex string for keys
    """
    invalid_chars = r'[^\w|\d|=|"|\-|:|\.|<|>|(|)|~|!]'
    blocks = r'((?<=\()[\w\d=<>"\-:.$~!]+(?=\)))'
    conditionals = r'(==|!=|<=|>=|<<|>>|BETWEEN|BEGINS|CONTAINS|~~|~)'
    comparitors = r'(AND|OR)'
    values = r'((?<=")[\w\d\-:.]+(?="))'
    keys = r'[a-zA-Z_]+(?=")'

    def __init__(self, key, query=None):
        if query is not None:
            self.check_query(query)
            self.expression = self.build_query(query)

        else:
            self.expression = None

        self.key = key

    def scan(self, **kwargs):  # TODO update unit test
        """
        Run the query

        Args
        ----
        kwargs
            Optional arguments for DynamoDB.Table.scan

        Returns
        -------
        dict
            {
                Items: the items returned by the scan,
                ConsumedCapacity: the number of read units consumed by the scan
            }
        """
        scanner = Scanner(self.key).query(self.expression)
        res = scanner.scan(ReturnConsumedCapacity='TOTAL', **kwargs)
        units = res['ConsumedCapacity']['CapacityUnits']
        items = res['Items']

        # iteratively scan the entire table
        while 'LastEvaluatedKey' in res:
            last = res['LastEvaluatedKey']
            res = scanner.scan(
              ExclusiveStartKey=last,
              ReturnConsumedCapacity='TOTAL',
              **kwargs
            )

            # tally the consumed read units
            units = units + res['ConsumedCapacity']['CapacityUnits']
            items.extend(res['Items'])

        return {'Items': items, 'ConsumedCapacity': units}

    @classmethod
    def check_query(cls, query):
        """
        Validates whether a query is valid

        Args
        ----
        query: str

        Returns
        -------
        boolean

        Raises
        ------
        ValueError
            if the query contains invalid characters
        """
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
        """
        Build the query expression to pass to DynamoDB.Table.scan

        Args
        ----
        query: str

        Returns
        -------
        DynamoDB.conditions.Attr
        """

        # get paranthetical subexperssions
        blocks = cls.build_blocks(query)

        # build the expression
        expression = cls.build_expression(blocks)

        return expression

    @classmethod
    def build_blocks(cls, query, blocks=None):
        """
        Extracts paranthentical subexpressions from a given query

        Args
        ----
        query: str
        blocks: list of str

        Returns
        -------
        list of str
            a list of subexpressions sorted in the order of evaluation. Nested
            subexpressions are replaced with '$X' in following subexpressions,
            where X is the index of the nested subexpression. For example, the
            expression '(a=="a"ORa=="b")AND(b=="a"AND(b=="b"ORb=="c"))' will
            return:
                ['a=="a"ORa=="b"', 'b=="b"ORb=="c"', 'b=="a"AND$1', '$0AND$2']
        """

        # an empty list on the first call
        blocks = blocks or []

        # get all subqueries by locating all expressions that are closed by a
        # single set of parantheses
        match = re.findall(cls.blocks, query)

        # if there are no more parantheses, return
        if not match:
            blocks.append(query)
            return blocks

        # replace nested subqueries with '$X'
        for i, block in enumerate(match):
            _i = i + len(blocks)
            query = query.replace(f'({block})', '$%s' % _i)

        blocks.extend(match)
        return cls.build_blocks(query, blocks=blocks)

    @classmethod
    def build_expression(cls, blocks, expressions=None):
        """
        Build the expression to be passed to DynamoDB.Table.scan given a set
        of blocks

        Args
        ----
        blocks: list of str
        expressions: list of DynamoDB.conditions.Attr
            A list used for iteratively building the expression, where the last
            element will be the ultimate return value
        
        Returns
        -------
        DynamoDB.conditions.Attr
        """

        # an empty list on the first call
        expressions = expressions or []

        # get the first block
        block = blocks[0]
        blocks = blocks[1:]
        expression = None

        # iterate over each subexpression in this block
        strings = re.split(cls.comparitors, block)
        for i, string in enumerate(strings):

            # odd-indexed items will be comparitors. Continue
            if i % 2:
                continue

            # if this subexpression is a nested subexpression
            if '$' in string:

                # get the index and subexpression
                ix = int(string.replace('$', ''))
                _expression = expressions[ix]

            else:

                # parse the subexpression
                _expression = cls.get_expression_from_string(string)

            # if this is the first subexpression, then there is no previous
            # expression to combine it with. Continue
            if not i:
                expression = _expression
                continue

            # the last item will be the comparitor with the previous expression
            comparison = strings[i - 1]

            if comparison == 'OR':
                expression = expression | _expression

            elif comparison == 'AND':
                expression = expression & _expression

        expressions.append(expression)

        # on last call
        if not blocks:
            return expressions[-1]

        return cls.build_expression(blocks, expressions)

    @classmethod
    def get_expression_from_string(cls, string):
        """
        Parse a subexpression
        
        Args
        ----
        string: str

        Returns
        -------
        DynamoDB.conditions.Attr
        """

        # remove conditionals
        popped = re.sub(cls.conditionals, '', string)

        # get the subexpression's key
        print(cls.keys, popped, re.search(cls.keys, popped))
        key = re.search(cls.keys, popped).group(0)

        # get the subexpression's conditional
        condition = re.search(cls.conditionals, string).group(0)

        # get the subexpressions values
        values = re.findall(cls.values, string) or ['']

        # build the expression
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
