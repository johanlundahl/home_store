import re
import operator
import json
from datetime import datetime

operators = { 'lt':operator.lt, 'le':operator.le, 'eq':operator.eq, 'ne':operator.ne, 'ge':operator.ge, 'gt':operator.gt }

class Filter:   
    def __init__(self, name, operator='eq', value=None):
        self.name = name
        self.operator = operators[operator]
        self.value = value

    @classmethod
    def from_querystring(cls, str):
        match = re.compile("(.+)\[(.+)\]=(.+)").match(str)
        if match:
            name, operator, value = match.groups()
            return Filter(name, operator, cls.value_parse(value))
        match = re.compile('(.+)=(.+)').match(str)
        if match:
            name, value = match.groups()
            return Filter(name, value=cls.value_parse(value))

    @classmethod
    def from_arg(cls, name, value):
        match = re.compile("(.+)\[(.+)\]").match(name)
        if match:
            name, operator = match.groups()
            return Filter(name, operator, cls.value_parse(value))
        return Filter(name, value=cls.value_parse(value))

    @classmethod
    def args_matching(cls, args, name):
        return [a for a in args if a[:len(name)] == name]

    @property
    def evaluate(self):
        return lambda x: self.operator(x.__dict__[self.name], self.value)  

    def __str__(self):
        return 'Filter(name={}, operator={}, value={})'.format(self.name, self.operator, self.value)

    def __repr__(self):
        return str(self)

    @classmethod
    def value_parse(cls, str):
        try:
            date = datetime.strptime(str, '%Y-%m-%d')
            return str
        except:
            return json.loads(str)
        