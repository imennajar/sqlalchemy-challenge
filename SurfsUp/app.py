# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
import datetime as dt
import numpy as np
import pandas as pd
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"

    )
    
@app.route("/api/v1.0/precipitation")   
def precipitation():   
    # Calculate the date one year from the last date in data set.
    lasty = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    dp = session.query(measurement.date, measurement.prcp).filter(measurement.date>=lasty).all()
    session.close()

    # Create a dictionary
    list_d = []
    for date, prcp, in dp:
        date_dict = {}
        date_dict["date"] = date
        date_dict["prcp"] = prcp
        list_d.append(date_dict)
    return jsonify(list_d)


@app.route("/api/v1.0/stations")
def st():  
    st = session.query(station.station,station.name,station.latitude,station.longitude,station.elevation).all()
    session.close()  
    # Convert list of tuples into normal list
    # Convert list of tuples into a list of dictionaries
    list_st = []
    for s in st:
        station_dict = {
            "station": s[0],
            "name": s[1],
            "latitude": s[2],
            "longitude": s[3],
            "elevation": s[4]
        }
        list_st.append(station_dict)

    return jsonify(list_st)

@app.route("/api/v1.0/tobs")
def tobs():
    lasty = dt.date(2017, 8, 23)-dt.timedelta(days=365)    
    tob = session.query(measurement.tobs,measurement.date).\
        filter(measurement.station == 'USC00519281').filter(measurement.date>=lasty).all()
    session.close()
    # Convert list of tuples into a list
    list_tob = [{"tobs": t[0], "date": t[1]} for t in tob]
    return jsonify(list_tob)
 
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date range 
#defines an API endpoint that accepts one parameters for a specified start date
@app.route("/api/v1.0/<start>")
def starting(start):
    #convert the start date to datetime objects 
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    #request to calculate the minimum, average, and maximum of the Tobs between the given date and the last date in the dataset
    date_mes = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
    #close the session
    session.close() 
    #convert the result to a list  
    list_date_mes = list(np.ravel(date_mes))
    #jsonify and return the result
    return jsonify(list_date_mes)



#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end dates range 
#defines an API endpoint that accepts two parameters for a specified start date and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end): 
    #convert the start and end dates to datetime objects    
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    #request to calculate the minimum, average, and maximum of the Tobs between the two dates
    date_mes = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    #close the session
    session.close() 
    #convert the result to a list  
    list_date_mes = list(np.ravel(date_mes))
    #jsonify and return the result
    return jsonify(list_date_mes)

#run the Flask app
if __name__ == "__main__":
    app.run(debug=True)