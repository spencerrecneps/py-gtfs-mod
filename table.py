import os
from column import Column


class Table:

    def __init__(self, name, columns):
        self.name = name
        self.columns = list()
        for column in columns:
            self.columns.append(Column(column, self))
        
    def __unicode__():
        return u'Table %d' % self.name