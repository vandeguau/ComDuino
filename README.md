# COMDUINO - Arduino Serial Data Acquisition and Visualization Tool

## Description:

COMDUINO is a Python-based application designed to interact with an Arduino board via serial communication. The primary function of this program is to facilitate:

## Data Acquisition: 
Reading and receiving data transmitted from an Arduino through the serial port. This data typically includes sensor readings or any other relevant information from the connected Arduino.

## Real-time Data Visualization and Storage: 
Displaying the acquired data in real-time using Matplotlib within a graphical interface. Additionally, it provides functionality to store this data in a CSV file format for future analysis or long-term storage.

## Key Features:
Allows selection of the Arduino's communication port.
Enables setting the communication speed (baud rate) for data transmission.
Offers options to specify the type of data being acquired from the Arduino.

## Functionality:
Upon initialization, the program continuously reads data sent by the Arduino. As new data arrives, it is dynamically displayed in a graphical plot within the user interface. Simultaneously, the program writes these incoming data points to a CSV file, ensuring a log of the received information for future reference or analysis.

## Use Cases:

Monitoring sensor data in real-time.
Experimentation requiring data acquisition and visualization.
Scientific projects involving Arduino-based data collection.

Note: This tool provides a versatile solution for real-time data acquisition, visualization, and storage, making it valuable for various projects involving Arduino boards and sensor data.
