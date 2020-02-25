import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


app = Flask(__name__)


Latest_Date = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
Latest_Date = list(np.ravel(Latest_Date))[0]

Latest_Date = dt.datetime.strptime(Latest_Date, '%Y-%m-%d')
Latest_Year = int(dt.datetime.strftime(Latest_Date, '%Y'))
Latest_Month = int(dt.datetime.strftime(Latest_Date, '%m'))
Latest_Day = int(dt.datetime.strftime(Latest_Date, '%d'))

Before365 = dt.date(Latest_Year, Latest_Month, Latest_Day) - dt.timedelta(days=365)
Before365 = dt.datetime.strftime(Before365, '%Y-%m-%d')

@app.route("/")
def home():
    return (f"Welcome to Surf's Up!: Hawaii Climate API<br/>"
            f"Available end points:<br/>"
            f"/api/v1.0/stations ~~~~~ a list of all weather observation stations<br/>"
            f"/api/v1.0/precipitaton ~~ the latest year of rainfall data<br/>"
            f"/api/v1.0/temperature ~~ the latest year of temperature data<br/>"
            f"~~~ datesearch (yyyy-mm-dd)<br/>"
            f"/api/v1.0/datesearch/2017-06-15  ~~~~~~~~~~~ When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start dat<br/>"
            f"/api/v1.0/datesearch/2017-06-15/2017-06-30 ~~ When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive<br/>")
                          
@app.route("/api/v1.0/stations")
def stations():
    Results_Station = session.query(Station.name).all()
    Stations = list(np.ravel(Results_Station))
    return jsonify(Stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > Before365)
                      .order_by(Measurement.date)
                      .all())
    
    Rainfall_Data = []
    for result in results:
        Rainfall_Dict = {result.date: result.prcp, "Station": result.station}
        Rainfall_Data.append(Rainfall_Dict)

    return jsonify(Rainfall_Data)

@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > Before365)
                      .order_by(Measurement.date)
                      .all())

    Temp_Data = []
    for result in results:
        Temp_Dict = {result.date: result.tobs, "Station": result.station}
        Temp_Data.append(Temp_Dict)

    return jsonify(Temp_Data)

@app.route('/api/v1.0/datesearch/<Start_Date>')
def Start(Start_Date):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= Start_Date)
                       .group_by(Measurement.date)
                       .all())

    Dates = []                       
    for result in results:
          Date_Dict = {}
          Date_Dict["Date"] = result[0]
          Date_Dict["Low Temp"] = result[1]
          Date_Dict["Avg Temp"] = result[2]
          Date_Dict["High Temp"] = result[3]
          Dates.append(Date_Dict)
    return jsonify(Dates)

@app.route('/api/v1.0/datesearch/<Start_Date>/<End_Date>')
def Start_End(Start_Date, End_Date):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= Start_Date)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= End_Date)
                       .group_by(Measurement.date)
                       .all())

    Dates = []                       
    for result in results:
         Date_Dict = {}
         Date_Dict["Date"] = result[0]
         Date_Dict["Low Temp"] = result[1]
         Date_Dict["Avg Temp"] = result[2]
         Date_Dict["High Temp"] = result[3]
         Dates.append(Date_Dict)
    return jsonify(Dates)

if __name__ == "__main__":
    app.run(debug=True)