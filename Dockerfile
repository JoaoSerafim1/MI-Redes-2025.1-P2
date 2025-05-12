FROM python:3.9-slim
WORKDIR /python_redes

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 

#Install fontconfig
RUN apt-get update && apt-get install -y fontconfig

# Download Package Information
RUN apt-get update -y

# Install Tkinter
RUN apt-get install tk -y && \
    apt-get install -y python3-pip

# Install CustomTkinter
RUN pip install customtkinter

# Install requests
RUN pip install requests

COPY . .
EXPOSE 8000
EXPOSE 8001
EXPOSE 8002

CMD [ "python", "Djangoapp/manage.py","runserver", "0.0.0.0:8000" ]