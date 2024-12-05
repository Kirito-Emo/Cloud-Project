import requests
import pandas as pd
from datetime import datetime

def fetch_dogecoin_data():
    # Endpoint di CoinGecko
    url = "https://api.coingecko.com/api/v3/coins/dogecoin/market_chart"
    params = {
        "vs_currency": "usd",  # Valuta
        "days": "max",         # Tutti i dati disponibili
        "interval": "daily"    # Dati giornalieri
    }

    # Richiesta API
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Errore nell'accesso all'API: {response.status_code}")

    data = response.json()

    # Estrazione dei prezzi e volumi
    prices = data["prices"]
    volumes = data["total_volumes"]

    # Creazione di un DataFrame
    df = pd.DataFrame({
        "date": [datetime.fromtimestamp(x[0] / 1000) for x in prices],
        "price": [x[1] for x in prices],
        "volume": [x[1] for x in volumes]
    })

    # Salvataggio su CSV
    df.to_csv("dogecoin_data.csv", index=False)
    print("Dati salvati in 'dogecoin_data.csv'.")

if __name__ == "__main__":
    fetch_dogecoin_data()