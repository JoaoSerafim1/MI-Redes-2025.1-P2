#Base Image
FROM python:3.9-slim

#Main work directory
WORKDIR /python_redes


#Atualizar pacotes
RUN apt-get update -y

#Install pip
RUN apt-get install -y python3-pip

#Install fontconfig
RUN apt-get install -y fontconfig

# Install Tkinter
RUN apt-get install -y tk
# Install CustomTkinter
RUN pip install customtkinter

#Install Paho MQTT
RUN pip install paho-mqtt

#Install requests
RUN pip install requests

#Install Mosquitto Broker
RUN apt-get upgrade -y && \
    apt-get install -y mosquitto && \
    apt-get install -y mosquitto-clients


#Expose Ports
EXPOSE 1883
EXPOSE 8001
EXPOSE 8002
EXPOSE 8025