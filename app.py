import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#####precipitation app route
@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of all precipitation records"""
    # Query all precipitation data
    results = session.query(
                Measurement.date,
                Measurement.prcp).all()
    session.close()

    # Convert list into dict
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

#####station app route
@app.route("/api/v1.0/stations")
def stat():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of all stations"""
    # Query all stations
    stations = session.query(
                Station.station).all()
    session.close()

    # Convert list into dict
    all_stations = []
    for station in stations:
        station_dict = {}
        station_dict["date"] = station
        all_stations.append(station_dict)

    return jsonify(stations)

#####tobs app route
@app.route("/api/v1.0/tobs")
def temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of all tobs for most active station in the last year"""
    # Query the date range for the last year

    last_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    last_date = dt.datetime.strptime(last_date_str,'%Y-%m-%d')

    first_date = last_date - dt.timedelta(days=365)

     # Query the most active station
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
    order_by((func.count(Measurement.station)).desc()).all()

    most_active = station_activity[0][0]

    # Query all data for that station for the last year
    precip_active_station = session.query(Measurement.tobs).\
                    filter(Measurement.date > first_date).\
                    filter(Measurement.station == most_active).all()

    # Convert list into dict
    active_tobs = []
    for tob in precip_active_station:
        act_tobs_dict = {}
        act_tobs_dict["tobs"] = tob
        active_tobs.append(act_tobs_dict)

    return jsonify(precip_active_station)

#####start app route
#@app.route("/api/v1.0/<start>")
#def start_stat(start):

    #"""Calculate stats for temperatures in the range matches
    #   the path variable supplied by the user, or a 404 if not."""

    #dt_start_date = dt.datetime.strptime(start,'%Y-%m-%d')

    #user_stats = session.query(func.avg(Measurement.tobs), 
    #                              func.min(Measurement.tobs),
    #                              func.max(Measurement.tobs)).\
    #             filter(Measurement.date > first_date).all()

        # Convert list into dict
    #start_temps = []
    #for stat in user_stats:
    #    start_temp_dict = {}
    #    start_temp_dict["tobs"] = tob
    #   start_temps.append(start_temp_dict)

    #return jsonify(user_stats)

if __name__ == '__main__':
    app.run(debug=True)
