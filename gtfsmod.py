import os
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
            
        # Set up column relationships
        self.tables['stops'].columns['stop_id'].addChild(self.tables['stop_times'].columns['stop_id'])
        self.tables['stops'].columns['stop_id'].addChild(self.tables['transfers'].columns['from_stop_id'])
        self.tables['stops'].columns['stop_id'].addChild(self.tables['transfers'].columns['to_stop_id'])
        self.tables['routes'].columns['route_id'].addChild(self.tables['trips'].columns['route_id'])
        self.tables['trips'].columns['trip_id'].addChild(self.tables['stop_times'].columns['trip_id'])
        self.tables['trips'].columns['trip_id'].addChild(self.tables['frequencies'].columns['trip_id'])
        self.tables['calendar'].columns['service_id'].addChild(self.tables['trips'].columns['service_id'])
        self.tables['calendar'].columns['service_id'].addChild(self.tables['calendar_dates'].columns['service_id'])
        self.tables['shapes'].columns['shape_id'].addChild(self.tables['trips'].columns['shape_id'])
    
    
    def __unicode__(self):
        return u'GTFS Modifier Object with path %s' % self.path
    
    def __repr__(self):
        return r'GTFS Modifier Object with path %s' % self.path