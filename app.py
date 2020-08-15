import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/waihee_rain<br/>"
        f"/api/v1.0/<start><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data"""
    # Query all prcp

    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    all_precipitations = []
    for date, station, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["station"] = station
        precipitation_dict["prcp"] = prcp

        all_precipitations.append(precipitation_dict)

    return jsonify(all_precipitations)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station data including the name, station code, station id, latitude, longitude, elevation"""
    # Query all stations
    results = session.query(Station.name, Station.station, Station.id, Station.latitude, Station.longitude, Station.elevation).all()


    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for name, station, id, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["name"] = name
        station_dict["station"] = station
        station_dict["id"] = id
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation


        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/waihee_rain")
def waihee():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of the most recent 12 months precipitation data for waihee"""
    # Query all prcp

    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= (dt.date(2017, 8, 23) - dt.timedelta(days=+365))).all()

    session.close()

    # Convert list of tuples into normal list
    all_waihee = []
    for date, station, prcp in results:
        waihee_dict = {}
        waihee_dict["date"] = date
        waihee_dict["station"] = station
        waihee_dict["prcp"] = prcp

        all_waihee.append(waihee_dict)

    return jsonify(all_waihee)


@app.route("/api/v1.0/<start>")
def weather_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """minimum temperature, the average temperature, and the max temperature for a given start range, or a 404 if not."""
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    group_by(Measurement.date).all()
    

    session.close()

    canonicalized = start.replace(" ", "")
    all_dates=[]
    for TMIN, TAVE, TMAX in results:
        search_term = Measurement.date
        if search_term == canonicalized:
            TMIN, TAVE, TMAX = results
            start_dict = {}
            start_dict["min_temp"] = TMIN
            start_dict["ave_temp"] = TAVE
            start_dict["max_temp"] = TMAX

            all_dates.append(start_dict)

            return jsonify(start_dict)

        return jsonify({"error": f"Dates not found"})








if __name__ == '__main__':
    app.run(debug=True)
