import streamlit as st
import pandas as pd
import joblib
from PIL import Image

# Load the model and scaler
@st.cache_resource
def load(transformer_path, model_path):
    transformer = joblib.load(transformer_path)
    model = joblib.load(model_path)
    return transformer, model

# App title
st.title('Dogecoin Price Prediction')
image = Image.open('data/dogecoin-image.png')
st.image(image, use_container_width=True)

# Make predictions
def inference(subject_data, transformer, model, feat_cols):
    df = pd.DataFrame([subject_data], columns = feat_cols)
    tr = transformer.fit(df)
    X = tr.transform(df)
    features = pd.DataFrame(X, columns = feat_cols)
    try:
        prediction = model.predict(features)
        print(f'Predicted Close Price: {prediction[0]}')
        return prediction[0]
    except Exception as err:
        print(f'Error during prediction: {err}')

# User input
st.header('Enter data for prediction')
high = st.number_input('High')
low = st.number_input('Low')
open = st.number_input('Open')
volume = st.number_input('Volume')
date = st.date_input('Date')

# Extract day, month, year, and day of the week from the date
day = date.day
month = date.month
year = date.year
dayofweek = date.weekday()

# Prepare data for prediction
subject_data = [high, low, open, volume, day, month, year, dayofweek]

# Make the prediction
try:
    if (st.button('Predict Dogecoin Price')):
        feat_cols = ['High', 'Low', 'Open', 'Volume', 'Day', 'Month', 'Year', 'DayOfWeek']
        transformer, model = load('models/doge_transformer.joblib', 'models/doge_model.joblib')
        prediction = inference(subject_data, transformer, model, feat_cols)
        st.write(f'Predicted Close Price: ', prediction)
except Exception as e:
    st.error(f'Error during prediction: {e}')