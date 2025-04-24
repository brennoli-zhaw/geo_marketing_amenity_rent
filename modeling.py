import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Read the modeling data from CSV
df = pd.read_csv("modeling_data.csv")
print("Data shape:", df.shape)
print(df.head())

# Assume the target variable is "price_numeric" and the rest are features.
target_column = "price_numeric"
X = df.drop(columns=[target_column])
y = df[target_column]

# Split data into training and test sets (e.g., 80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    random_state=42)

# Create and train the RandomForestRegressor
rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
rf_regressor.fit(X_train, y_train)

# Predict on the test set
y_pred = rf_regressor.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Random Forest Mean Squared Error (MSE):", mse)
print("Random Forest R2 Score:", r2)
