#from flask import Flask
# import 'Flask' library from 'flask' module

#app = Flask(__name__)
# create a new 'Flask' instance called 'app', with a magic method executed on 'name'

#@app.route('/')
# define the root ('/' denotes the base root) 
#def hello_world():
# 'hello_world()' function applied to our route
#    return 'Hello world'

import datetime as dt
import numpy as np
import pandas as pd
# import dependencies

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# import 'SQLAlchemy' dependencies

from flask import Flask, jsonify
# import 'flask' dependencies

### this first section sets up our SQL database

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
# this allows us to access the 'SQLite' database file

Base.prepare(engine, reflect=True)
# reflect tables into the database

Measurement = Base.classes.measurement
Station = Base.classes.station
# create reference variables for each class

session = Session(engine)
# create session link to database

### with our database created, now set up the flask app

## all routes need to be put under this line of code, or they may not work:
app = Flask(__name__)
# create a new flask instance called 'app', with a magic method executed on 'name'

## suppose we want to import our 'app.py' file into another file named example.py,
## the variable '__name__' would be set to 'example'. Here's how that looks: 

#import app
#print("example __name__ = %s", __name__)
#if __name__ == "__main__":
#    print("example is being run directly.")
#else:
#   print("example is being imported")

## moving on to create our routes

@app.route("/")
# define welcome route
def welcome():
# create a function 'welcome' with a return
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')
    # the naming convention '/api/v1.0/...' + <route> signifies that this is
    # version 1 of our application

@app.route("/api/v1.0/precipitation")
# create a route for precipitation. This needs to be included at the end of the
# http root statement to yield precipitation data
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # calculates date range, 2016.08.23-2017.08.23
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    # retrieves the date and precipitation data for the previous year
    # the './' signifies that the query continues on the next line
    precip = {date: prcp for date, prcp in precipitation}
    # creates a json with date as the key and precipitation as the value 
    return jsonify(precip)
    # returns the json file for precipitation data

@app.route("/api/v1.0/stations")
# create a route for station analysis. This needs to be included at the end of
# of the http rootstatement to yield station data
def stations():
    results = session.query(Station.station).all()
    # query the database 'Station' to pul all 'station' data from the table
    stations = list(np.ravel(results))
    # unravel results into a 1-dimensional array and lists the bits
    return jsonify(stations=stations) 
    # returns the stations list as a json 

@app.route("/api/v1.0/tobs")
# create a route for temperature observations. This needs to be included at the
# end of the http root statement to yield the temp obs data
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # calculates date range of a year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
        # retrieves temperature observations for a specific station over date range
    temps = list(np.ravel(results))
    # unravel the results into a 1-dimensional array and list the bits
    return jsonify(temps=temps)
    # returns the temperatures list as a json

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# creates a route for temperature statistics, however two instances need to be 
# declared because we have to specify the start and end date
# we declare the start and end date in the http line
def stats(start=None, end=None):
# define the 'stats' function with two parameters: start and end dates
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # create a list with the temperature statistics we are going to query
    if not end:
    # since start and end dates are not well-defined, we add an 'if not' statement
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
            # query the database for the temp statistics after the start date
            # note the asterisk, this denotes that there will be multiple results returned
        temps = list(np.ravel(results))
        # unravel the results into a 1-dimensional array and list the bits
        return jsonify(temps)
        # return the temperature statistics list as a json

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
        # query the database for temp statistics over the date range
    temps = list(np.ravel(results))
    # unravel the results into a 1-dimensional array and list the bits
    return jsonify(temps) 
    # return the temperature statistics list as a json   
