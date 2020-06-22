from keras.models import load_model
# Regression Example With Boston Dataset: Standardized and Larger
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

# Instantiate the model as you please (we are not going to use this)

def larger_model():
	# create model
	model = Sequential()
	model.add(Dense(20, input_dim=3, kernel_initializer='normal', activation='relu'))
	model.add(Dense(20, kernel_initializer='normal', activation='relu'))
	model.add(Dense(20, kernel_initializer='normal', activation='relu'))
	model.add(Dense(1, kernel_initializer='normal'))
	# Compile model
	model.compile(loss='mean_squared_error', optimizer='adam')
	return model

def get_caudal(gra,p_h,pot):
    model2 = KerasRegressor(build_fn=larger_model, epochs=10, batch_size=10, verbose=1)


    model2.model = load_model('modelBV1.h5')

    gra = gra/1000
   # gra = 0.021
   # p_h = 340.000
   # pot = 4.00
    Xnew = np.array([[float(gra), float(p_h), float(pot)]])

    caudl = model2.predict(Xnew)
    print(caudl)
    return round(float(caudl),2)


def  frec(q50,frec):

    return((q50*frec/50))