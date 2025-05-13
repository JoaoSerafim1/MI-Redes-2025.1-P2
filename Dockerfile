#Base Image
FROM python:3.9-slim

#Main work directory
WORKDIR /python_redes

#Install pip
RUN apt-get update -y && \
    apt-get install -y python3-pip

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

#Install fontconfig
RUN apt-get update -y && \
    apt-get install -y fontconfig

# Install Tkinter
RUN apt-get update -y && \
    apt-get install -y tk
# Install CustomTkinter
RUN pip install customtkinter

#Install Mosquitto Broker
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y mosquitto && \
    apt-get install -y mosquitto-clients

#Install Paho MQTT
RUN apt-get update -y && \
    pip install paho-mqtt

# Install requests
RUN pip install requests

#Expose Ports
COPY . .
EXPOSE 8000
EXPOSE 1883
EXPOSE 8001
EXPOSE 8002

CMD [ "python", "Djangoapp/manage.py","runserver", "0.0.0.0:8000" ]
