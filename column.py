import os, random, string

class Column:

    def __init__(self, name, table):
        self.name = name
        self.table = table
        self.childColumns = []      #childColumns is a list that contains existing column objects
        self.columnNumber = self.getColumn()
    
    
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
        
        # Read through the input file looking for matches in the appropriate column
        # If a match is found, leave it out in writing to the temp file
        with open(self.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
            for line in inFile:
                vals = line.split(',')
                if not vals[self.columnNumber] in values:
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
        
        # Read through the input file looking for matches in the appropriate column
        # If a match is found, leave it out in writing to the temp file
        with open(self.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
            for line in inFile:
                vals = line.split(',')
                if vals[self.columnNumber] in values:
                    outFile.write(line)
                    
        # Handle any dependent table columns
        for col in self.childColumns:
            col.keep(values)
        
        # Swap the old file for the new one
        os.remove(self.table.path)
        os.rename(tempPath, self.table.path)
    
    def mod(self,values):    # Takes a list of tuples of (fromValue, toValue) and changes any matching values to the new value  
        # Check if the GTFS file exists
        if not os.path.isfile(self.table.path):
            return
            
        # Assign temporary filename in GTFS path
        temp = ''.join(random.choice(string.lowercase) for i in range(6)) + '.txt'
        tempPath = self.table.path + '.' + temp

        # Build a list of column values for checking against
        valueList = [i[0] for i in values]
        
        # Read through the input file looking for matches in the appropriate column
        # If a match is found, swap the value in the temp file
        with open(self.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
            for line in inFile:
                vals = line.split(',')
                if vals[self.columnNumber] in valueList:
                    newValue = values[valueList.index(vals[self.columnNumber])][1]
                    vals[self.columnNumber] = str(newValue)
                    newLine = ','.join(vals)
                    outFile.write(newLine)
                else:
                    outFile.write(line)
                    
        # Handle any dependent table columns
        for col in self.childColumns:
            col.mod(values)
        
        # Swap the old file for the new one
        os.remove(self.table.path)
        os.rename(tempPath, self.table.path)
    
    
    def getColumn(self):
        if self.table.exists:
            with open(self.table.path, 'r') as f:
                line = f.readline()
                try:
                    return line.split(',').index(self.name)
                except ValueError:
                    return None
        else: return None
        
    def makeSequence(self, outputValues=False):
        '''Searches through the routes and stop_times and replaces
           every route_id with a number. Numbers are generated
           starting at 1 and increasing by 1 for each subsequent
           new route_id encountered.
           If outputValues is set to true, a file will be
           created that contains the mappings between the
           old route_id and the new one
        '''
        # set up list for id and unique int value
        trips = []
        i = 0

        # Loop through the trips file and build the list to pass in for mod
        with open(self.table.path, 'r') as f:
            for line in f:
                vals = line.split(',')
                trips.append((vals[self.columnNumber],i))
                i = i + 1

        # Remove the column heading        
        trips.pop(0)
        
        # Send the list of trips to mod
        self.mod(trips)
        
        # Write the ID mapping to file (if applicable)
        if outputValues:
            with open(os.path.join(self.table.gtfsPath,'route_mapping.txt'), 'w') as m:
                m.write('route_id,sequence_nm\n')
                for mapping in trips:
                    m.write(','.join(str(x) for x in mapping) + '\n')
                
            