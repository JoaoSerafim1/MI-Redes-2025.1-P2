#Base Image
FROM python:3.9-slim

#Main work directory
WORKDIR /python_redes

#Install fontconfig
RUN apt-get update -y && apt-get install -y fontconfig

# Install Tkinter
RUN apt-get update -y && \
    apt-get install -y tk && \
    apt-get install -y python3-pip
# Install CustomTkinter
RUN pip install customtkinter

#Install Mosquitto Broker
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y mosquitto && \
    apt-get install -y mosquitto-clients

#Install Paho MQTT
RUN pip install paho-mqtt

#Expose Ports
EXPOSE 8001
EXPOSE 8002