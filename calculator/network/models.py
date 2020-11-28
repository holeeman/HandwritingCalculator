# -*- coding: utf-8 -*-
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model
from .symbols import Symbols

class ClassifierNetwork:
    NUM_CLASSES = len(Symbols.classes)
    INPUT_SHAPE = (100, 100, 3)

    def __init__(self):
        self.model = None
        self.arch = self.get_architecture()
        self.compiled = False
        self.num_classes = ClassifierNetwork.NUM_CLASSES

    def get_architecture(self):
        arch = [
                Conv2D(128, 14, padding='valid', activation='relu', strides=4, input_shape=ClassifierNetwork.INPUT_SHAPE),
                MaxPooling2D(3, padding='valid', strides=2),

                Conv2D(256, 9, padding='same', activation='relu'),
                MaxPooling2D(3, padding='valid', strides=2),

                Conv2D(512, 3, padding='same', activation='relu'),
                Conv2D(512, 3, padding='same', activation='relu'),
                MaxPooling2D(2, padding='valid', strides=2),

                Flatten(),
                Dense(128, activation='relu'),
                Dropout(0.5),
                Dense(128, activation='relu'),
                Dropout(0.5),
                Dense(ClassifierNetwork.NUM_CLASSES, activation='softmax')
            ]
        return arch
    
    def compile(self):
        if self.model:
            self.model.compile(
                loss='categorical_crossentropy',
                optimizer='adam',
                metrics=['accuracy']
            )
            self.compiled = True
    
    def train(self, train_data, epochs, patience):
        if self.model and self.compiled:
            X_train, y_train, X_val, y_val= train_data

            X_train = X_train.astype('float32')
            X_train = X_train / 255

            X_val = X_val.astype('float32')
            X_val = X_val / 255

            y_train = to_categorical(y_train, self.num_classes)
            y_val = to_categorical(y_val, self.num_classes)

            early_stopping = EarlyStopping(monitor='val_loss', patience=patience)

            return self.model.fit(
                X_train, y_train,
                epochs=epochs,
                validation_data=(X_val, y_val),
                shuffle=True,
                callbacks=[early_stopping]
            )
    def predict(self, X):
        if self.model:
            return self.model.predict(X)
    
    def load(self, file):
        self.model = load_model(file)

    def save(self, file):
        if self.model:
            self.model.save(file)

def loadClassifierModel(modelPath):
    network = ClassifierNetwork()
    network.load(modelPath)
    return network
