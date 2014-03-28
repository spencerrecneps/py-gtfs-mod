import os, random, string

class Relationship:
    
    def __init__(self, direct, column=None, helperColumn=None):
        self.direct = direct
        self.column = column
        self.helperColumn = helperColumn
        
        
    def __unicode__(self):
        return u'Column %s with helper %s' % (self.column.name, self.helperColumn.name)


    def __repr__(self):
        return r'Column %s with helper %s' % (self.column.name, self.helperColumn.name)
    
    
    def setColumn(self, column):
        self.column = column
        
        
    def setHelperColumn(self, column):
        if not self.direct:
            raise AttributeError('Cannot set help column on a direct relationship')
        self.helperColumn = column
        
    
    def rm(self, values, replace):
        if self.direct:
            self.column.rm(values, True)
        else:
            # Assign temporary filename
            tempPath = self.column.getTempPath()
            
            # Iterate the temporary file and find the helper column
            with open(self.column.path, 'r') as inFile, open(tempPath, 'w') as outFile:
                for line in inFile:
                    vals = line.split(',')
                    if not vals[self.helperColumn.columnNumber] in values:
                        outFile.write(line)
            
            # Handle any dependent table columns
            for rel in self.column.relationships:
                rel.column.rm(values, replace)
                        
            # Swap the old file for the new one if replace is True
            if replace:
                os.remove(self.table.path)
                os.rename(tempPath, self.table.path)
                        
            
    