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
import datetime
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
#start at the homepage and list all the available routes
@app.route("/")
def home():
   
    return (
        "<html>"
        "<body>"
        "<h1>Welcome Hawaii Climate API</h1>"
        
        "<h3>Precipitation:</h3>"
        "<p>/api/v1.0/precipitation</p>"
        
        "<h3>Stations:</h3>"
        "<p>/api/v1.0/stations</p>"
        
        "<h3>Temperature Observations:</h3>"
        "<p>/api/v1.0/tobs</p>"
        
        "<h3>Minimum, average, and maximum of the temperature for a specified start or start-end range:</h3>"
        "<p>/api/v1.0/start/end</p>"
        
        "</body>"
        "</html>"

    )

#convert a query results from  retrieving only the last 12 months of data to a dictionary using date as the key and prcp as the value.    
@app.route("/api/v1.0/precipitation")   
def precipitation():   
    
    # calculate the date one year from the last date in data set.
    lasty = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    
    # perform a query to retrieve the data and precipitation scores
    dp = session.query(measurement.date, measurement.prcp).filter(measurement.date>=lasty).all()
    
    #close the session
    session.close()
    
    # create a dictionary
    list_d = []
    for date, prcp, in dp:
        date_dict = {}
        date_dict["date"] = date
        date_dict["prcp"] = prcp
        list_d.append(date_dict)
        
    #return the JSON representation of the dictionary
    return jsonify(list_d)

#return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def st():  
    
    #query the database to get station information
    st = session.query(station.station,station.name,station).all()
    
    #close the session
    session.close()  
    
    #convert the query result to a list
    list_st = [{"station": t[0], "name": t[1]} for t in st]
    
        
    #return a JSON list
    return jsonify(list_st)

#query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    
    #calculate the date one year ago from  (August 23, 2017)
    lasty = dt.date(2017, 8, 23)-dt.timedelta(days=365)  
    
    #query the database to get temperature observations (tobs) for the most-active station 'USC00519281' for the previous year of data. 
    tob = session.query(measurement.tobs,measurement.date).\
        filter(measurement.station == 'USC00519281').filter(measurement.date>=lasty).all()
        
    #close the session
    session.close()
    
    #convert the query result to a list 
    list_tob = [{"tobs": t[0], "date": t[1]} for t in tob]
    
    #return a JSON list
    return jsonify(list_tob)
 

#return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end dates range 
#defines an API endpoint that can accept one or two parameters for a specified start or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start="", end=""):
    #use a try to look for invalid start date format
    try:
        #convert start to datetime
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        
        #if the user gives an end date
        if len(end) > 0:
            
            #convert end to datetime
            end_date = dt.datetime.strptime(end, '%Y-%m-%d')
            
            #query to calculate min, avg, and max Tobs between start and end
            sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
            date_mes = session.query(*sel).\
                filter(measurement.date >= start).\
                filter(measurement.date <= end).all()
            
                
        #if the user doesn't give an end date
        else:
            #query to calculate min, avg, and max Tobs from start to last date
            sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
            date_mes = session.query(*sel).\
                filter(measurement.date >= start).all()
           
        
        #close the session
        session.close() 
        
        #convert the query result to a list
        list_m = [{"min": t[0], "average": t[1], "max": t[2]} for t in date_mes]
        
        #return a JSON list
        return jsonify(list_m)
    
    except ValueError:
        return jsonify({"error": "Invalid date"})


#run the Flask app
if __name__ == "__main__":
    app.run(debug=True)