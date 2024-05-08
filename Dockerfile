# Base image
FROM ubuntu:22.04

# Working directory, Streamlit does not work at root
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt /app/

# Install Python
RUN apt update -y
RUN apt install -y python3-pip python-dev-is-python3 build-essential

# Install dependencies
RUN pip install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm

# Copy the current code to the 
COPY . .

# Running with Streamlit
CMD [ "streamlit", "run", "App.py"]
