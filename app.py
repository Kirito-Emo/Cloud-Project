from flask import Flask, request, jsonify
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler

class LSTMModel(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1):
        super(LSTMModel, self).__init__()
        self.lstm = torch.nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = torch.nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h_0 = torch.zeros(1, x.size(0), 50).to(x.device)
        c_0 = torch.zeros(1, x.size(0), 50).to(x.device)
        out, _ = self.lstm(x, (h_0, c_0))
        out = self.fc(out[:, -1, :])
        return out

app = Flask(__name__)
model = LSTMModel(input_size=1, hidden_size=50, output_size=1)
model.load_state_dict(torch.load("dogecoin_lstm_model.pth"))
model.eval()
scaler = MinMaxScaler()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    df = pd.DataFrame(data)
    df["price"] = scaler.transform(df["price"].values.reshape(-1, 1))
    X = torch.tensor(df["price"].values, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)
    with torch.no_grad():
        prediction = model(X).item()
    prediction = scaler.inverse_transform([[prediction]])
    return jsonify({"prediction": prediction[0][0]})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)