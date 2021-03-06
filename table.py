from column import Column

class Table:

    def __init__(self, name, path, gtfsPath, cols, exists):
        self.name = name
        self.path = path
        self.gtfsPath = gtfsPath
        self.exists = exists
        self.columns = {}
        for col in cols:
            self.columns[col] = Column(col, self)
        
        
    def __unicode__(self):
        return u'Table %s' % self.name
    
    
    def __repr__(self):
        return r'Table %s' % self.name