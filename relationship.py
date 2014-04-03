import os, random, string
from sets import Set

class Relationship:
    
    def __init__(self, shallow, column=None, helperColumn=None):
        self.shallow = shallow
        self.column = column
        self.helperColumn = helperColumn
        
        
    def __unicode__(self):
        if self.helperColumn:
            return u'Column %s in table %s with helper %s' % (self.column.name, self.column.table.name, self.helperColumn.name)
        else:
            return u'Column %s in table %s' % (self.column.name, self.column.table.name)

    def __repr__(self):
        if self.helperColumn:
            return r'Column %s in table %s with helper %s' % (self.column.name, self.column.table.name, self.helperColumn.name)
        else:
            return r'Column %s in table %s' % (self.column.name, self.column.table.name)
    
    
    def setColumn(self, column):
        self.column = column
        
        
    def setHelperColumn(self, column):
        if not self.shallow:
            raise AttributeError('Cannot set help column on a shallow relationship')
        self.helperColumn = column
        
    
    def rm(self, values, cascade=False, replace=False):
        if self.shallow:
            self.column.rm(values, replace)
        else:
            helperValues = []
            
            # Assign temporary filename
            tempPath = self.column.getTempPath()
            
            # Iterate the temporary file and find the helper column
            with open(self.column.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
                for line in inFile:
                    vals = line.split(',')
                    if not vals[self.helperColumn.columnNumber] in values:
                        outFile.write(line)
                    else:
                        helperValues.append(vals[self.column.columnNumber])
            
            # Handle any dependent table columns
            if cascade:
                for rel in self.column.relationships:
                    rel.column.rm(helperValues, cascade=cascade, replace=replace)
                        
            # Swap the old file for the new one if replace is True
            if replace:
                os.remove(self.table.path)
                os.rename(tempPath, self.table.path)
                        
                        
    def keep(self, values, cascade=False, replace=False):
        if self.shallow:
            self.column.keep(values, replace)
        else:
            helperValues = []
            
            # Assign temporary filename
            tempPath = self.column.getTempPath()
            
            # Iterate the temporary file and find the helper column
            with open(self.column.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
                # Write the header to the new file
                header = inFile.readline()
                outFile.write(header)
                # Loop through and write matching lines
                for line in inFile:
                    vals = line.split(',')
                    if vals[self.helperColumn.columnNumber] in values:
                        outFile.write(line)
                        helperValues.append(vals[self.column.columnNumber])
                                
            # Handle any dependent table columns
            if cascade:
                for rel in self.column.relationships:
                    rel.column.keep(helperValues, cascade=cascade, replace=replace)
                        
            # Swap the old file for the new one if replace is True
            if replace:
                os.remove(self.table.path)
                os.rename(tempPath, self.table.path)