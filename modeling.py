import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import sklearn.metrics as metrics
import numpy as np

# Read the modeling data from CSV
type = "walking_1"
df = pd.read_csv(f"modeling/modeling_{type}.csv")
print("Data shape:", df.shape)
print(df.head())
print(df.columns.tolist())

# Assume the target variable is "price_numeric" and the rest are features.
target_column = "price"
X = df.drop(columns=[target_column])
y = df[target_column]

target_names = df.drop(columns=[target_column]).columns.values

# Split data into training and test sets (e.g., 80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    random_state=42)

# Create and train the RandomForestRegressor
rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
rf_regressor.fit(X_train, y_train)

# Predict on the test set
y_pred = rf_regressor.predict(X_test)

#evaluate the model
#accuracy = metrics.accuracy_score(y_test, y_pred)
explained_variance=metrics.explained_variance_score(y_test, y_pred)
mean_absolute_error=metrics.mean_absolute_error(y_test, y_pred) 
mse=metrics.mean_squared_error(y_test, y_pred) 
mean_squared_log_error=metrics.mean_squared_log_error(y_test, y_pred)
median_absolute_error=metrics.median_absolute_error(y_test, y_pred)
r2=metrics.r2_score(y_test, y_pred)


print('explained_variance: ', round(explained_variance,4))    
print('mean_squared_log_error: ', round(mean_squared_log_error,4))
print('r2: ', round(r2,4))
print('MAE: ', round(mean_absolute_error,4))
print('MSE: ', round(mse,4))
print('RMSE: ', round(np.sqrt(mse),4))

#metrics.classification_report(y_test, y_pred, target_names=target_names)