import numpy as np
from datetime import datetime as dt
from datetime import timedelta, date

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

app = Flask(__name__)

# Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
            f"Climate Analysis Home Page!<br/>"
            f"<br/>Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end>"
            )

# Define what to do when a user hits the /precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    print("Server received request for 'Precipitation' page...")
    
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
   
    precipitation = {date: prcp for (date, prcp) in results}
    
    return jsonify(precipitation)

# Define what to do when a user hits the /stations route
@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)
    
    print("Server received request for 'Stations' page...")
    
    results = session.query(Station.station).all()
    session.close()
        
    stations = {}
    station_list = [station[0] for station in results]        
    stations["stations"] = station_list
    
    return jsonify(stations)

# Define what to do when a user hits the /tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    
    print("Server received request for 'Temperature Observations' page...")
    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.strptime(str(last_date[0]), '%Y-%m-%d') - timedelta(days = 365)
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first().station    
    
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > last_year).\
    filter(Measurement.station == most_active_station).all()
    session.close()
    
    date_list = [date for (date, t_obs) in results]
    t_obs_list = [t_obs for (date, t_obs) in results]
    tobs = dict(zip(date_list, t_obs_list))
    
    return jsonify(tobs)

# Define what to do when a user hits the /<start_date> route
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    
    session = Session(engine)
    
    print("Server received request for 'Start Date' page...")
    
    def calc_temps(start_date):
    
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
        
    results = calc_temps(start_date)
    print(results)
    
    temperatures = {}
    #temperatures = list(np.ravel(results))
    
    tmin_list = [tmin for (tmin, tavg, tmax) in results]
    tavg_list = [tavg for (tmin, tavg, tmax) in results]
    tmax_list = [tmax for (tmin, tavg, tmax) in results]

    temperatures["min_temp"] = tmin_list
    temperatures["avg_temp"] = tavg_list
    temperatures["max_temp"] = tmax_list
    
    return jsonify(temperatures)

# Define what to do when a user hits the /<start_date>/<end_date> route
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    
    session = Session(engine)
    
    print("Server received request for 'Start Date and End Date' page...")
    
    def calc_temps(start_date, end_date):
    
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    results = calc_temps(start_date, end_date)
    
    temperatures = {}
    tmin_list = [tmin for (tmin, tavg, tmax) in results]
    tavg_list = [tavg for (tmin, tavg, tmax) in results]
    tmax_list = [tmax for (tmin, tavg, tmax) in results]

    temperatures["min_temp"] = tmin_list
    temperatures["avg_temp"] = tavg_list
    temperatures["max_temp"] = tmax_list

    return jsonify(temperatures)

if __name__ == "__main__":
    app.run(debug=True)
