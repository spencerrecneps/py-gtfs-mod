import os

class Column:

    def __init__(self, name, table):
        self.name = name
        self.table = table
        self.childColumns = list()      #childColumns is a list that contains existing column objects
    
    def __unicode__():
        return u'Column %d in table %d' % self.name,  self.table
        
    def addChild(self, childColumn):
        if not isinstance(childColumn, Column):
            raise TypeError('Not a valid column object')
            return False
        self.childColumns.append(childColumn)
        return True