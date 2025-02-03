import streamlit as st
import pandas as pd
import joblib
import logging
from PIL import Image

# Set up logging to write to a persistent file
logging.basicConfig(
    filename='/app/logs/predictions.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to load model and transformer
@st.cache_resource
def load(transformer_path, model_path):
    transformer = joblib.load(transformer_path)
    model = joblib.load(model_path)
    return transformer, model

# App title
st.title('Dogecoin Price Prediction')
image = Image.open('data/dogecoin-image.png')
st.image(image, use_container_width=True)

# Function to make predictions
def inference(subject_data, transformer, model, feat_cols):
    try:
        df = pd.DataFrame([subject_data], columns=feat_cols)
        tr = transformer.fit(df)
        X = tr.transform(df)
        features = pd.DataFrame(X, columns=feat_cols)
        prediction = model.predict(features)
        logging.info(f"Input: {subject_data} -> Predicted Close Price: {prediction[0]}")
        print(f'Predicted Close Price: {prediction[0]}')
        return prediction[0]
    except Exception as err:
        logging.error(f"Error during prediction: {err}")
        print(f'Error during prediction: {err}')
        return "Error"

# User input with basic protection against XSS/SQLi attacks
st.header('Enter data for prediction')
high = st.number_input('High', min_value=0.0, step=0.01)
low = st.number_input('Low', min_value=0.0, step=0.01)
open = st.number_input('Open', min_value=0.0, step=0.01)
volume = st.number_input('Volume', min_value=0.0, step=0.01)
date = st.date_input('Date')

# Extract features from date
day = date.day
month = date.month
year = date.year
dayofweek = date.weekday()

# Prepare data for prediction
subject_data = [high, low, open, volume, day, month, year, dayofweek]

# Make the prediction
try:
    if st.button('Predict Dogecoin Price'):
        feat_cols = ['High', 'Low', 'Open', 'Volume', 'Day', 'Month', 'Year', 'DayOfWeek']
        transformer, model = load('models/doge_transformer.joblib', 'models/doge_model.joblib')
        prediction = inference(subject_data, transformer, model, feat_cols)
        st.write(f'Predicted Close Price: {prediction}')
except Exception as e:
    st.error(f'Error during prediction: {e}')