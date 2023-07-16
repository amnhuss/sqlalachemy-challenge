# Import the dependencies.
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
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

app.route("/")
def home():
    return (
        f"<h1>Welcome to the Surf's Up Weather API!</h2>"
        f"<p>Select to view:</p>"
        "<ul>"
        f"<li> <strong>Precipitation data from the last 12 months:</strong> /api/v1.0/precipitation<br/> </li>"
        f"<li> <strong>List of all stations:</strong> /api/v1.0/stations<br/> </li>"
        f"<li> <strong>List of all active stations :</strong> /api/v1.0/tobs<br/></li>"
        f"<li> <strong>Max, min, and average temperatures since specified start date:</strong> /api/v1.0/yyyy-mm-dd<br/></li>"
        f"<li> <strong>Max, min, and average temperatures between specified start date and end date:</strong>/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/></li>"
        "</ul>"
    )

########################################################################################################
#Return the previous 12 months of precipitation data as a JSON list
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Retreive last 12 months of precipitation data

    #Set a variable to store the date of one year ago
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)


    #Query all dates and precipitation data from a year ago until now
    last_years_prcp = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > year_ago).\
        order_by(measurement.date).all()
    
    #Close the session after the query is complete
    session.close()

    #Create a dictionary from the row data and append to a list of precipitation_data
    precipitation_data = []
    for date, prcp in last_years_prcp:
        prcp_dict = {}
        #Set the date as the key and the value of prcp as the result
        prcp_dict[date] = prcp
        precipitation_data.append(prcp_dict)

    #Return a jsonified version of our dictionary
    return jsonify(precipitation_data)

########################################################################################################
#Return a JSON list of all stations from the dataset
@app.route("/api/v1.0/stations")
def stations():

    #Query the names of all stations
    station_list = session.query(Station.station, Station.name).all()
    #Close the session after the query is complete
    session.close()
    #Create a dictionary from the row data and append to a list of station_data
    station_data = []

    for station, name in station_list:
        station_dict = {}
        station_dict["name"] = name
        station_data.append(station_dict)

    #Return a jsonified version of our dictionary
    return jsonify(station_data)

########################################################################################################
#Return a JSON list of temperature observations of the most-active station for the previous year of data
@app.route("/api/v1.0/tobs")
def tobs_func():
    #Retreive last 12 months of temperature data

    #Set a variable to store the date of one year ago
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and temperature data
    USC00519281_last_years_temp = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date > year_ago).\
        filter(measurement.station == "USC00519281").\
        order_by(measurement.date).all()
    
    #Close the session after the query is complete
    session.close()

    #Create a dictionary from the row data and append to a list of tobs_data
    tobs_data = []
    for date, tobs in USC00519281_last_years_temp:
        tobs_dict = {}

        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs

        tobs_data.append(tobs_dict)

    #Return a jsonified version of our dictionary
    return jsonify(tobs_data)

########################################################################################################
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date
@app.route("/api/v1.0/<start>")
def minmaxmean_temps(start):
    lowest_temperature = session.query(measurement.station , func.min(measurement.tobs)).\
        filter(measurement.date >= start).all()

    highest_temperature = session.query(measurement.station , func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()

    average_temperature = session.query(measurement.station , func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()

    #Query the most recent date in the database to use in case the user queries a date beyond this
    max_date = session.query(func.max(measurement.date)).first()

    #Close the session after the query is complete
    session.close()

    # Create a dictionary to store the temperature values
    tobs_values = {}
    # Convert the row objects to dictionaries
    lowest_temp_dict = {"tmin": lowest_temperature[0][1]}
    avg_temp_dict = {"tavg": average_temperature[0][1]}
    highest_temp_dict = {"tmax": highest_temperature[0][1]}
    # Add the dictionaries to the tobs_values dictionary
    tobs_values.update(lowest_temp_dict)
    tobs_values.update(avg_temp_dict)
    tobs_values.update(highest_temp_dict)

    # Return the dictionary as a JSON response

    #If the start date is in range, return the tobs_value dictionary
    if start <= max_date[0]:
        return jsonify(tobs_values)
    #If the start date is out of range, return an eror message
    else: 
        return jsonify({"error": f"Start date {start} out of range."}, 404)


########################################################################################################
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date
@app.route("/api/v1.0/<start>/<end>")
def minmaxmean_temps_start_and_end(start, end):
    lowest_temperature = session.query(measurement.station , func.min(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    highest_temperature = session.query(measurement.station , func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    average_temperature = session.query(measurement.station , func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    #Query the most recent date in the database to use in case the user queries a date beyond this
    max_date = session.query(func.max(measurement.date)).first()

    #Close the session after the query is complete
    session.close()

    # Create a dictionary to store the temperature values
    tobs_values = {}
    # Convert the row objects to dictionaries
    lowest_temp_dict = {"tmin": lowest_temperature[0][1]}
    avg_temp_dict = {"tavg": average_temperature[0][1]}
    highest_temp_dict = {"tmax": highest_temperature[0][1]}
    # Add the dictionaries to the tobs_values dictionary
    tobs_values.update(lowest_temp_dict)
    tobs_values.update(avg_temp_dict)
    tobs_values.update(highest_temp_dict)

    # Return the dictionary as a JSON response

    #If the start date is in range, return the tobs_value dictionary
    if start <= max_date[0]:
        return jsonify(tobs_values)
    #If the start date is out of range, return an eror message
    else: 
        return jsonify({"error": f"Start date {start} out of range."}, 404)


################################################################################

if __name__ == '__main__':
    app.run(debug=True)