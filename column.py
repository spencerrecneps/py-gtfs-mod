import os, random, string
from relationship import Relationship

class Column:

    def __init__(self, name, table):
        self.name = name
        self.table = table
        self.columnNumber = self.getColumn()
        self.relationships = []
    
    
    def __unicode__(self):
        return u'Column %s in %s' % (self.name, self.table)
    
    
    def __repr__(self):
        return r'Column %s in %s' % (self.name, self.table)
        
    
    def addRelationship(self, direct, column=None, helperColumn=None):
        self.relationships.append(Relationship(direct, column, helperColumn))
    
    
    def rm(self, values, cascade=False, replace=False):
        '''Takes a list of values to look for and produces
           a new GTFS file with matching values removed.
           Will also cascade to child fields. For example,
           calling this on routes.route_id would remove
           all trips and stop_times associated with the
           route being removed.
           Future enhancement: take a cascade parameter
           that stops it from cascading if desired'''
        # Check if the GTFS file exists
        if not os.path.isfile(self.table.path):
            return
        
        # Assign temporary filename in GTFS path
        tempPath = self.getTempPath()
        
        # Read through the input file looking for matches in the appropriate column
        # If a match is found, leave it out in writing to the temp file
        with open(self.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
            for line in inFile:
                vals = line.split(',')
                if not vals[self.columnNumber] in values:
                    outFile.write(line)
                    
        # Handle any dependent table columns
        if cascade:
            for rel in self.relationships:
                rel.rm(values, cascade=cascade, replace=replace)
                        
        # Swap the old file for the new one if replace is True
        if replace:
            os.remove(self.table.path)
            os.rename(tempPath, self.table.path)
        
        
    def keep(self, values, cascade=False, replace=False):
        '''Takes a list of values to look for and produces 
           a new GTFS file with only the matching rows'''     
        # Check if the GTFS file exists
        if not os.path.isfile(self.table.path):
            return
        
        # Assign temporary filename in GTFS path
        tempPath = self.getTempPath()
        
        # Read through the input file looking for matches in the appropriate column
        # If a match is found, leave it in when writing to the temp file
        with open(self.table.path, 'r') as inFile, open(tempPath, 'w') as outFile:
            # Write the header to the new file
            header = inFile.readline()
            outFile.write(header)
            # Loop through and write matching lines
            for line in inFile:
                vals = line.split(',')
                if vals[self.columnNumber] in values:
                    outFile.write(line)
                    
        # Handle any dependent table columns
        if cascade:
            for rel in self.relationships:
                rel.keep(values, cascade=cascade, replace=replace)
        
        # Swap the old file for the new one if replace is true
        if replace:
            os.remove(self.table.path)
            os.rename(tempPath, self.table.path)
    
    
    def mod(self,values,cascade=False,replace=False):
        '''Takes a list of tuples of (fromValue, toValue) and 
           changes any matching values to the new value. Also
           cascades to related columns, much like rm()'''  
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
        if cascade:
            for rel in self.relationships:
                if rel.shallow:
                    rel.column.mod(values, cascade=False, replace=replace)
                else:
                    rel.helperColumn.mod(values, cascade=True, replace=replace)
        
        # Swap the old file for the new one if replace is new
        if replace:
            os.remove(self.table.path)
            os.rename(tempPath, self.table.path)
    
    
    def getColumn(self):
        '''Helper function for determining the
           index number of the column'''
        if self.table.exists:
            with open(self.table.path, 'r') as f:
                line = f.readline()
                try:
                    return line.split(',').index(self.name)
                except ValueError:
                    return None
        else: return None
        
    
    def makeSequence(self, replace=False, mapping=True, prefix=None):
        '''Searches through the column and its relationships and replaces
           every route_id with a number. Numbers are generated
           starting at 1 and increasing by 1 for each subsequent
           new route_id encountered.
           If mapping is set to true, a file will be
           created that contains the mappings between the
           old route_id and the new one'''
        
        # set up list for id and unique int value
        trips = []
        i = 0

        # Loop through the trips file and build the list to pass in for mod
        with open(self.table.path, 'r') as f:
            for line in f:
                vals = line.split(',')
                if prefix:
                    trips.append((vals[self.columnNumber],prefix + str(i)))
                else:
                    trips.append((vals[self.columnNumber],i))
                i = i + 1

        # Remove the column heading        
        trips.pop(0)
        
        # Send the list of trips to mod
        self.mod(trips, replace=replace, cascade=True)
        
        # Write the ID mapping to file (if applicable)
        if mapping:
            with open(os.path.join(self.table.gtfsPath,self.name + '_mapping.txt'), 'w') as m:
                m.write(self.name + ',sequence_nm\n')
                for mapping in trips:
                    m.write(','.join(str(x) for x in mapping) + '\n')
                    
                    
    def getTempPath(self):
        '''Assigns a temporary path'''
        # Assign temporary filename in GTFS path
        temp = ''.join(random.choice(string.lowercase) for i in range(6)) + '.txt'
        tempPath = self.table.path + '.' + temp
        return tempPath
                
            