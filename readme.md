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
