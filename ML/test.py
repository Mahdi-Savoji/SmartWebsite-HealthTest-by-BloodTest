import pandas as pd
from model import predict_diabetes

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
result = predict_diabetes(new_data)
print(f"Predicted Diagnosis (0 = No Diabetes, 1 = Diabetes): {result}")