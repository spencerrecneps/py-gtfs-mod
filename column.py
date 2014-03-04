import os, random, string

class Column:

    def __init__(self, name, table):
        self.name = name
        self.table = table
        self.childColumns = []      #childColumns is a list that contains existing column objects
    
    
    def __unicode__(self):
        return u'Column %s in %s' % (self.name, self.table)
    
    
    def __repr__(self):
        return r'Column %s in %s' % (self.name, self.table)
    
        
    def addChild(self, childColumn):
        self.childColumns.append(childColumn)
    
    
    def rm(self,values):        # Takes a list of values to look for and produces a new GTFS file with matching values removed
        # Check if the GTFS file exists
        if not os.path.isfile(self.table.path):
            return
        
        # Assign temporary filename in GTFS path
        temp = ''.join(random.choice(string.lowercase) for i in range(6)) + '.txt'
        tempPath = self.table.path + '.' + temp
        
        # Get the column number of the column
        columnNumber = self.getColumn()
        
        # Read through the input file looking for matches in the appropriate column
        # If a match is found, leave it out in writing to the temp file
        with open(self.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
            for line in inFile:
                vals = line.split(',')
                if not vals[columnNumber] in values:
                    outFile.write(line)
                    
        # Handle any dependent table columns
        for col in self.childColumns:
            col.rm(values)
        
        # Swap the old file for the new one
        os.remove(self.table.path)
        os.rename(tempPath, self.table.path)
        
        
    def keep(self, values):     # Takes a list of values to look for and produces a new GTFS file with only the matching rows     
        # Check if the GTFS file exists
        if not os.path.isfile(self.table.path):
            return
        
        # Assign temporary filename in GTFS path
        temp = ''.join(random.choice(string.lowercase) for i in range(6)) + '.txt'
        tempPath = self.table.path + '.' + temp
        
        # Get the column number of the column
        columnNumber = self.getColumn()
        
        # Read through the input file looking for matches in the appropriate column
        # If a match is found, leave it out in writing to the temp file
        with open(self.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
            for line in inFile:
                vals = line.split(',')
                if vals[columnNumber] in values:
                    outFile.write(line)
                    
        # Handle any dependent table columns
        for col in self.childColumns:
            col.keep(values)
        
        # Swap the old file for the new one
        os.remove(self.table.path)
        os.rename(tempPath, self.table.path)
    
    def mod(self,values):    # Takes a list of tuples of (fromValue, toValue) and changes any matching values to the new value  
        pass
    
    
    def getColumn(self):
        with open(self.table.path, 'r') as f:
            line = f.readline()
            return line.split(',').index(self.name)
                
            