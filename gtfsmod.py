import os
import time
from table import Table

class GTFSModifier:


    def __init__(self, path):
        self.path = path

        # Set up the tables
        t = {                           # Add all GTFS tables with some basic info about each
              'agency': {'required': True,'columns': ['agency_id',
                                                      'agency_name',
                                                      'agency_url',
                                                      'agency_timezone',
                                                      'agency_lang',
                                                      'agency_phone',
                                                      'agency_fare_url']},
              'stops': {'required': True,'columns': ['stop_id',
                                                     'stop_code',
                                                     'stop_name',
                                                     'stop_desc',
                                                     'stop_lat',
                                                     'stop_lon',
                                                     'zone_id',
                                                     'stop_url',
                                                     'location_type',
                                                     'parent_station',
                                                     'stop_timezone',
                                                     'wheelchair_boarding']},
              'routes': {'required': True,'columns': ['route_id',
                                                      'agency_id',
                                                      'route_short_name',
                                                      'route_long_name',
                                                      'route_desc',
                                                      'route_type',
                                                      'route_url',
                                                      'route_color',
                                                      'route_text_color']},
              'trips': {'required': True,'columns': ['route_id',
                                                     'service_id',
                                                     'trip_id',
                                                     'trip_headsign',
                                                     'trip_short_name',
                                                     'direction_id',
                                                     'block_id',
                                                     'shape_id',
                                                     'wheelchair_accessible',
                                                     'bikes_allowed']},
              'stop_times': {'required': True,'columns': ['trip_id',
                                                          'arrival_time',
                                                          'departure_time',
                                                          'stop_id',
                                                          'stop_sequence',
                                                          'stop_headsign',
                                                          'pickup_type',
                                                          'drop_off_type',
                                                          'shape_dist_traveled']},
              'calendar': {'required': True,'columns': ['service_id',
                                                        'monday',
                                                        'tuesday',
                                                        'wednesday',
                                                        'thursday',
                                                        'friday',
                                                        'saturday',
                                                        'sunday',
                                                        'start_date',
                                                        'end_date']},
              'calendar_dates': {'required': False,'columns': ['service_id',
                                                               'date',
                                                               'exception_type']},
              'fare_attributes': {'required': False,'columns': ['fare_id',
                                                                'price',
                                                                'currency_type',
                                                                'payment_method',
                                                                'transfers',
                                                                'transfer_duration']},
              'fare_rules': {'required': False,'columns': ['fare_id',
                                                           'route_id',
                                                           'origin_id',
                                                           'destination_id',
                                                           'contains_id']},
              'shapes': {'required': False,'columns': ['shape_id',
                                                       'shape_pt_lat',
                                                       'shape_pt_lon'
                                                       'shape_pt_sequence',
                                                       'shape_dist_traveled']},
              'frequencies': {'required': False,'columns': ['trip_id',
                                                            'start_time',
                                                            'end_time',
                                                            'headway_secs',
                                                            'exact_times']},
              'transfers': {'required': False,'columns': ['from_stop_id',
                                                          'to_stop_id',
                                                          'transfer_type',
                                                          'min_transfer_time']},
              'feed_info': {'required': False,'columns': ['feed_publisher_name',
                                                          'feed_publisher_url',
                                                          'feed_lang',
                                                          'feed_start_date',
                                                          'feed_end_date',
                                                          'feed_version']}}
        self.tables = {}
        for name, vals in t.iteritems():
            exists = False              # Assume a table doesn't exist unless we find it
            filePath = os.path.join(self.path, name + '.txt')
            if os.path.isfile(filePath):
                exists = True
            self.tables[name] = Table(name,filePath,self.path,vals['columns'], exists)

        # Set up direct column relationships
        self.tables['stops'].columns['stop_id'].addRelationship(True, self.tables['stop_times'].columns['stop_id'])
        self.tables['stops'].columns['stop_id'].addRelationship(True, self.tables['transfers'].columns['from_stop_id'])
        self.tables['stops'].columns['stop_id'].addRelationship(True, self.tables['transfers'].columns['to_stop_id'])
        self.tables['trips'].columns['trip_id'].addRelationship(True, self.tables['stop_times'].columns['trip_id'])
        self.tables['trips'].columns['trip_id'].addRelationship(True, self.tables['frequencies'].columns['trip_id'])
        self.tables['calendar'].columns['service_id'].addRelationship(True, self.tables['trips'].columns['service_id'])
        self.tables['calendar'].columns['service_id'].addRelationship(True, self.tables['calendar_dates'].columns['service_id'])
        self.tables['shapes'].columns['shape_id'].addRelationship(True, self.tables['trips'].columns['shape_id'])

        # Set up indirect column relationships
        self.tables['agency'].columns['agency_id'].addRelationship(False,
                                                                   self.tables['routes'].columns['route_id'],
                                                                   self.tables['routes'].columns['agency_id'])
        self.tables['routes'].columns['route_id'].addRelationship(False,
                                                                  self.tables['trips'].columns['trip_id'],
                                                                  self.tables['trips'].columns['route_id'])


    def makeShapes(self, path):
        '''Creates a geojson file with all of the stops.
           Future enhancement = read the shapes file and take
           and arg for creating a shape for a particular
           trip'''
        from geojson import Feature, FeatureCollection, Point
        import geojson

        features = []
        stops = self.tables['stops']
        with open(stops.path, 'r') as stopsFile:
            next(stopsFile)         #skip header row
            for line in stopsFile:
                vals = line.split(',')

                # Establish the point
                point = Point((float(vals[stops.columns['stop_lon'].columnNumber]),
                               float(vals[stops.columns['stop_lat'].columnNumber])))

                # Establish attribute data
                attrs = {}
                for key, col in stops.columns.iteritems():
                    if col.columnNumber is not None:
                        attrs[col.name] = vals[col.columnNumber]

                # Create the feature
                feat = Feature(geometry=point,
                               id=vals[stops.columns['stop_id'].columnNumber],
                               properties=attrs)

                # Add to the list of features
                features.append(feat)

        fc = FeatureCollection(features)
        with open(path, 'w') as outFile:
            geojson.dump(fc, outFile)


    def stopBusCount(self, stop_ids_in, service_ids, route_ids=None, start_time=None, end_time=None):
        '''Returns a dictionary of stop_ids and a count of the number of times
        that a bus of any route (or optionally specified route_ids) stops at the
        given stop_ids on the service days identified in the list of service_ids.
        N.B. all inputs are lists except start_time and end_time.
        Start and end times are given in the format "HH:MM:SS" with the first two
        digits being the hour (in 24 hour time), the middle two digits being the
        minutes, and the last two digits being the seconds'''
        #process inputs
        if start_time is None and end_time is not None:
            raise Exception("Start time must be given with end time")
        if end_time is None and start_time is not None:
            raise Exception("End time must be given with start time")
        stop_ids_in = [str(i) for i in stop_ids_in]
        stop_ids = dict()
        for i in stop_ids_in:
            stop_ids[i] = 0
        service_ids = [str(i) for i in service_ids]
        if route_ids:
            route_ids = [str(i) for i in route_ids]

        #get tables
        trips = self.tables['trips']
        stopTimes = self.tables['stop_times']

        #build list of trip_ids
        trip_ids = []
        with open(trips.path, 'r') as tripsFile:
            next(tripsFile)
            for line in tripsFile:
                vals = line.split(',')
                if vals[trips.columns['service_id'].columnNumber] in service_ids:
                    if route_ids:
                        if vals[trips.columns['route_id'].columnNumber] in route_ids:
                            trip_ids.append(vals[trips.columns['trip_id'].columnNumber])
                    else:
                        trip_ids.append(vals[trips.columns['trip_id'].columnNumber])

        #read the stop times and count every instance that matches the trip_id and stop_id list
        with open(stopTimes.path, 'r') as stopTimesFile:
            next(stopTimesFile)
            for line in stopTimesFile:
                vals = line.split(',')
                tripId = vals[stopTimes.columns['trip_id'].columnNumber]
                stopId = vals[stopTimes.columns['stop_id'].columnNumber]
                depTime = vals[stopTimes.columns['departure_time'].columnNumber].strip()

                # check for times > 24 hrs
                depCheck = depTime.split(':',1)
                if int(depCheck[0]) > 23:
                    depCheck[0] = '00'
                    depTime = ':'.join(depCheck)

                if tripId in trip_ids:
                    if stopId in stop_ids_in:
                        if start_time and end_time:
                            startCutoff = time.strptime(start_time,'%H:%M:%S')
                            endCutoff = time.strptime(end_time,'%H:%M:%S')
                            busTime = time.strptime(depTime,'%H:%M:%S')
                            if busTime < startCutoff:
                                continue    #ignore this row
                            if busTime > endCutoff:
                                continue    #ignore this row
                        stop_ids[stopId] = stop_ids[stopId] + 1

        return stop_ids


    def __unicode__(self):
        return u'GTFS Modifier Object with path %s' % self.path


    def __repr__(self):
        return r'GTFS Modifier Object with path %s' % self.path
