import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Sample dataset
data = {
    "area":[1000,1500,2000,2500,3000],
    "bedrooms":[2,3,3,4,5],
    "age":[10,5,3,2,1],
    "price":[3000000,4500000,6000000,7500000,9000000]
}

df = pd.DataFrame(data)

X = df[['area','bedrooms','age']]
y = df['price']

model = LinearRegression()
model.fit(X,y)

# Save model
pickle.dump(model, open("model.pkl","wb"))

print("Model trained and saved!")
