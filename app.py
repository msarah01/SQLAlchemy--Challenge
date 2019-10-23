import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station= Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def Home_Page():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    prcp = list(np.ravel(results))

    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    stations = session.query(Station.station, Station.name)

    stations = pd.read_sql(stations.statement, stations.session.bind)

    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs(): 

    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year). order_by(Measurement.date).all()  
 
@app.route("/api/v1.0/<start>/<end>")
def start_end(): 
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')

    end_date= dt.datetime.strptime(end,'%Y-%m-%d')

    last_year = dt.timedelta(days=365)

    start = start_date-last_year

    end = end_date-last_year

    session = Session(engine)

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    start_end = list(np.ravel(result))

    return jsonify(start_end)

if __name__ == '__main__':
   app.run(debug= True)