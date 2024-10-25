import joblib
import numpy as np
import pandas as pd

# Load the saved model
model_pipeline = joblib.load('best_diabetes_stacked_model_with_tuned_threshold.pkl')

def predict_diabetes(data, threshold=0.3):
    """
    Predicts the likelihood of diabetes and returns 0 or 1 based on the given threshold.

    Args:
        data (pd.DataFrame): DataFrame containing the features for prediction.
        threshold (float): Probability threshold to determine the prediction (default: 0.3).

    Returns:
        int: 0 for No Diabetes, 1 for Diabetes.
    """
    # Predict the probability of each class (0: No Diabetes, 1: Diabetes)
    predicted_proba = model_pipeline.predict_proba(data)
    
    # Extract the probability for class 1 (Diabetes)
    diabetes_proba = predicted_proba[0][1]
    
    # Apply the threshold to return 0 or 1
    return int(diabetes_proba >= threshold)

# Example input data
new_data = pd.DataFrame({
    'Gender': ['Male'],        # Categorical
    'Age': [45],               # Numerical
    'BMI': [28.7],             # Numerical
    'Chol': [220],             # Numerical
    'TG': [150],               # Numerical
    'HDL': [45],               # Numerical
    'LDL': [130],              # Numerical
    'Cr': [1.1],               # Numerical
    'BUN': [14.5]              # Numerical
})

# Example of Predictino Functino Usage 
# result = predict_diabetes(new_data)
# print(f"Predicted Diagnosis (0 = No Diabetes, 1 = Diabetes): {result}")
