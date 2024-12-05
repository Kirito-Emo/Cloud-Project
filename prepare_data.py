import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def prepare_data(file_path, window_size=30):
    # Caricamento dei dati
    df = pd.read_csv(file_path)

    # Normalizzazione
    scaler = MinMaxScaler()
    df["price"] = scaler.fit_transform(df["price"].values.reshape(-1, 1))

    # Creazione di sequenze
    sequences = []
    targets = []
    for i in range(len(df) - window_size):
        seq = df["price"].values[i:i + window_size]
        target = df["price"].values[i + window_size]
        sequences.append(seq)
        targets.append(target)

    # Conversione in array numpy
    X = np.array(sequences)
    y = np.array(targets)

    return X, y, scaler


if __name__ == "__main__":
    X, y, scaler = prepare_data("dogecoin_data.csv")
    print(f"Shape dei dati di training: {X.shape}, {y.shape}")