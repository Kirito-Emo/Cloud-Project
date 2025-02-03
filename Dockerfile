FROM python:3.10.9-slim-buster

# Ensures that Python outputs are sent straight to terminal (stdout) without buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxrender1 \
    gcc \
    g++ \
    build-essential
RUN pip3 install --no-cache-dir -r requirements.txt

# To fix vulnerabilities
RUN pip3 install setuptools==70.0.0
RUN python -m pip install --upgrade pip==23.3
RUN apt-get remove --purge -y binutils && apt-get autoremove -y

# Expose port
EXPOSE 8501

# Copy all the files needes for the application
ADD data /app/data
ADD logs /app/logs
COPY app.py /app
ADD models /app/models

# Creates a non-root user (streamlit) to enhance security
RUN useradd -m streamlit && chown -R streamlit /app
USER streamlit

# Create an entry point to make the image executable
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]