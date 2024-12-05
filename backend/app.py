from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

app = Flask(__name__)

# File paths for saved models
model_paths = {
    "random_forest": "rf_ddos_model.pkl",
    "knn": "knn_ddos_model.pkl",
    "naive_bayes": "gnb_ddos_model.pkl"
}

# LabelEncoder for consistent encoding
label_encoder = LabelEncoder()

@app.route('/upload', methods=['POST'])
def upload_and_train():
    try:
        # Get the uploaded file
        file = request.files['file']
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # Load the CSV data
        data = pd.read_csv(file)

        # Ensure necessary columns are present
        required_columns = ['src_ip', 'dst_ip', 'protocol', 'is_ddos']
        if not all(col in data.columns for col in required_columns):
            return jsonify({"error": f"Missing required columns: {', '.join(required_columns)}"}), 400

        # Preprocessing: Convert categorical features to numeric
        data['src_ip'] = data['src_ip'].apply(lambda x: int(x.replace('.', '')))
        data['dst_ip'] = data['dst_ip'].apply(lambda x: int(x.replace('.', '')))
        data['protocol'] = label_encoder.fit_transform(data['protocol'])

        # Split features and target
        X = data.drop("is_ddos", axis=1)
        y = data["is_ddos"]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train and save models
        models = {
            "random_forest": RandomForestClassifier(),
            "knn": KNeighborsClassifier(),
            "naive_bayes": GaussianNB()
        }

        for model_name, model in models.items():
            model.fit(X_train, y_train)
            with open(model_paths[model_name], 'wb') as f:
                pickle.dump(model, f)

        return jsonify({"message": "Models trained and saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Load the model
        model_name = request.args.get('model')  # Model name should be passed in the request
        if model_name not in model_paths:
            return jsonify({"error": "Invalid model name provided"}), 400

        if not os.path.exists(model_paths[model_name]):
            return jsonify({"error": f"Model {model_name} not found. Please train the model first."}), 400

        with open(model_paths[model_name], 'rb') as f:
            model = pickle.load(f)

        # Load input data
        input_data = request.json  
        df = pd.DataFrame(input_data)

        # Ensure data is preprocessed like in training
        df['src_ip'] = df['src_ip'].apply(lambda x: int(x.replace('.', '')))
        df['dst_ip'] = df['dst_ip'].apply(lambda x: int(x.replace('.', '')))
        df['protocol'] = label_encoder.transform(df['protocol'])  

        # Ensure only the features used during training are passed
        required_columns = ['src_ip', 'dst_ip', 'protocol']
        df = df[required_columns]

        # Make predictions
        predictions = model.predict(df)
        return jsonify({"predictions": predictions.tolist()}), 200

    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
