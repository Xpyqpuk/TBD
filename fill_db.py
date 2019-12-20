import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import MySQLdb
from scipy.spatial import distance
from dateutil.parser import parse
import time
import sys

create_tables = False
rebuild_data = False
if len(sys.argv) > 1:
    create_tables = 'create_tables' in sys.argv
    rebuild_data = 'rebuild_data' in sys.argv

if (rebuild_data):
    print(time.strftime('%I%p:%M:%S'), 'Reading files')
    acc=pd.read_csv('./acc2005_2016.csv')
    cas=pd.read_csv('./cas2005_2016.csv')
    veh=pd.read_csv('./veh2005_2016.csv')

    print(time.strftime('%I%p:%M:%S'), 'Calculating areas centers')
    lat, lon = acc['Latitude'], acc['Longitude']
    lat_nan = np.where(np.isnan(lat))
    lon_nan = np.where(np.isnan(lon))
    tmp = np.unique(np.append(lon_nan, lat_nan))
    x = np.array((lat, lon)).T
    x = x[~tmp]

if create_tables:
    print(time.strftime('%I%p:%M:%S'), 'Connecting to DB')
    connection = MySQLdb.connect(user="DreamTeam",
                                 passwd="1234",
                                 host="localhost",
                                 db="RoadAccidentsDB",)
    cur = connection.cursor()

    print(time.strftime('%I%p:%M:%S'), 'Creating tables')
    query = 'create table if not exists accidents(acc_index VARCHAR(255) PRIMARY KEY NOT NULL, place INT, time TIME, date DATE NOT NULL, road_type INT NOT NULL, accident_severity INT NOT NULL, road_class INT NOT NULL, vehicles_number INT NOT NULL, casualities_number INT NOT NULL, INDEX(acc_index, place, time, date));'
    cur.execute(query)
    query = 'create table if not exists casualty(acc_index VARCHAR(255) NOT NULL, casualty_type INT NOT NULL, casualty_class INT NOT NULL, casualty_sex INT NOT NULL, casualty_age INT NOT NULL, car_passenger INT NOT NULL, INDEX(acc_index, casualty_sex, casualty_age));'
    cur.execute(query)
    query = 'create table if not exists vehicle(acc_index VARCHAR(255) NOT NULL, veh_type INT NOT NULL, driver_sex INT NOT NULL, driver_age INT NOT NULL, vehicle_age INT NOT NULL, INDEX(acc_index, veh_type, driver_sex, driver_age, vehicle_age));'
    cur.execute(query)
    query = 'create table if not exists user_info(userid VARCHAR(255) PRIMARY KEY NOT NULL, veh_type INT, gender INT, area INT, age INT, vehicle_age INT, INDEX(userid));'
    cur.execute(query)

if rebuild_data:
    print(time.strftime('%I%p:%M:%S'), 'Columns that may be Null:')
    for col in acc.columns:
        if acc[col].hasnans:
            print(col, end=' ')
    for col in cas.columns:
        if cas[col].hasnans:
            print(col, end=' ')
    for col in veh.columns:
        if veh[col].hasnans:
            print(col, end=' ')
    print()

    print(time.strftime('%I%p:%M:%S'), 'Converting time')
    def convert_time(elem):
        return parse(elem).strftime("%Y/%m/%d")
    acc['Date'] = acc['Date'].apply(convert_time)

    print(time.strftime('%I%p:%M:%S'), 'Saving accidents dataset')
    acc = acc.rename(str.lower, axis='columns')
    acc = acc.rename({'accident_index':'acc_index', 'number_of_vehicles':'vehicles_number', 'number_of_casualties':'casualities_number', 'x1st_road_class':'road_class'}, axis='columns')
    acc = acc[['acc_index', 'place', 'time', 'date', 'road_type', 'accident_severity', 'road_class', 'vehicles_number', 'casualities_number']]
    acc.to_csv('/tmp/accidents', encoding='utf-8', index=False, header=False)

    print(time.strftime('%I%p:%M:%S'), 'Saving casualty dataset')
    cas = cas.rename(str.lower, axis='columns')
    cas = cas.rename({'accident_index':'acc_index', 'sex_of_casualty':'casualty_sex', 'age_of_casualty':'casualty_age'}, axis='columns')
    cas = cas[['acc_index', 'casualty_type', 'casualty_class', 'casualty_sex', 'casualty_age', 'car_passenger']]
    cas.to_csv('/tmp/casualty', encoding='utf-8', index=False, header=False)

    print(time.strftime('%I%p:%M:%S'), 'Saving vehicle dataset')
    veh = veh.rename(str.lower, axis='columns')
    veh = veh.rename({'accident_index':'acc_index', 'vehicle_type':'veh_type', 'sex_of_driver':'driver_sex', 'age_of_driver':'driver_age', 'age_of_vehicle':'vehicle_age'}, axis='columns')
    veh = veh[['acc_index', 'veh_type', 'driver_sex', 'driver_age', 'vehicle_age']]
    veh.to_csv('/tmp/vehicle', encoding='utf-8', index=False, header=False)

if create_tables:
    print(time.strftime('%I%p:%M:%S'), 'Filling accidents db with data')
    query = 'load data infile \'/tmp/accidents\' into table accidents fields terminated by \',\';'
    cur.execute(query)
    print(time.strftime('%I%p:%M:%S'), 'Filling casualty db with data')
    query = 'load data infile \'/tmp/casualty\' into table casualty fields terminated by \',\';'
    cur.execute(query)
    print(time.strftime('%I%p:%M:%S'), 'Filling vehicle db with data')
    query = 'load data infile \'/tmp/vehicle\' into table vehicle fields terminated by \',\';'
    cur.execute(query)
    connection.commit()
