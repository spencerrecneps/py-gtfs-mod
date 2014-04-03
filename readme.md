# GTFS Modifier

A simple Python-based tool for making changes to GTFS files. For more information on GTFS, please see the reference documentation at https://developers.google.com/transit/gtfs/.

## Basic usage

Create a new GTFSModifier class that points to the directory where the tables are stored.
#### Example
```
from gtfsmod import GTFSModifier
g = GTFSModifier('/home/username/path/to/gtfs')
```
From here, you can reference the tables and columns and call functions as outlined below.

## Tables
Table objects refer to the various GTFS tables. The main GTFSModifier class includes a dictionary object called, oddly enough, 'tables' that references each of the GTFS tables.
#### Example
```
from gtfsmod import GTFSModifier
g = GTFSModifier('/home/username/path/to/gtfs')
g.tables['stops']       # returns the object corresponding to the stops.txt table
```

## Columns
Column objects refer to the columns within each GTFS table. Each Table class contains a dictionary object called 'columns'.
#### Example
```
from gtfsmod import GTFSModifier
g = GTFSModifier('/home/username/path/to/gtfs')
stops = g.tables['stops']
stops.columns['stop_id']		# returns the object corresponding to the stop_id column in the stops.txt table
```
Most of the functionality of GTFS Modifier is contained in the column class. For example, you can remove items, change their values, or isolate them from the rest of the system. Here are the functions for each of these primary tasks:
* rm()
* mod()
* keep()

Each of these functions takes a list of values that it matches against the values in the column and then acts accordingly when it finds a match.
#### Example
```
from gtfsmod import GTFSModifier
g = GTFSModifier('/home/username/path/to/gtfs')
stops = g.tables['stops']
stop_id = stops.columns['stop_id']
stop_id.rm([1,2])				# removes any entries for stop_id 1 or 2
stop_id.mod([(3,9),(4,8)])		# replaces any entry with stop_id 3 with '9' or with stop_id 4 with '8'
stop_id.keep([7])				# removes all entries except stop_id 7 
```

Column operations can also cascade through to other tables if there is a dependency. For example, removing a route from the routes table will remove the trips associated with that route in the trips table, and would also remove related stop_times entries.
#### Example
```
from gtfsmod import GTFSModifier
g = GTFSModifier('/home/username/path/to/gtfs')
g.tables['routes'].columns['route_id'].rm(['1,2'])	# removes routes 1 and 2 from routes, trips, and stop_times
```
