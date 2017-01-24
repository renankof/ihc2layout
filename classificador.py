#!/bin/python
#coding: UTF-8
import json
import codecs
import numpy as np
#from sklearn.svm import SVC
#from sklearn.svm import LinearSVC
#from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import Perceptron, SGDClassifier

class Classificador():
    def __init__(self, nameFile):
        # carrega base inicial
        self.data, self.label = self.base_inicial(nameFile)
        # normalização da base
        self.data, self.nMin, self.nMax = self.normaliza(self.data)
        # carrega online Learning
        self.base_onlineLearning("data-onlineLearning.json")
        # self.cla = Perceptron()
        self.cla = SGDClassifier()
        # train classificador
        self.cla.fit(self.data, self.label)

    def my_predict(self, dataTest):
        # faz bucketização e formata as features em lista
        dataTest = self.formata_features(dataTest)
        if len(dataTest) > 0:
            # normaliza dados de teste
            dataTest = self.normaliza_teste(dataTest, self.nMin, self.nMax)
            # faz a predição
            predict = self.cla.predict(dataTest)

            return predict, dataTest
        else:
            # dado foi excluido ou sejá não posso classificar
            return [], dataTest

    def normaliza(self, data):
        #(x-min)/(max-min)
        npMax =  np.max(data, axis=0)
        npMin =  np.amin(data, axis=0)
        newData = []
        for x in data:
            tempList = []
            for k, value in enumerate(x):
                try:
                    tempValue = ((float(value) - float(npMin[k]))/(float(npMax[k])-float(npMin[k])))
                except ZeroDivisionError:
                    #colocar valor original MIN MAX
                    tempValue = value
                tempList.append(tempValue)
            newData.append(tempList)

        return newData, npMin, npMax

    def normaliza_teste(self, data, nMin, nMax):
        newData = []
        for x in data:
            tempList = []
            for k, value in enumerate(x):
                tempValue = value
                if value > nMax[k]:
                    tempValue = nMax[k]
                elif value < nMin[k]:
                    tempValue = nMin[k]
                tempList.append(tempValue)
            newData.append(tempList)

        return newData

    def formata_features(self, value):
        newData = []
        if (int(value['sessionTime']) > 100) and int(value['countA']) > 0 or int(value['countB']) > 0:
            try:
                x = float(value['timeA'])/float(value['countA'])
            except ZeroDivisionError:
                x = float(value['timeA'])
            try:
                y = float(value['timeB'])/float(value['countB'])
            except ZeroDivisionError:
                y = float(value['timeB'])

            value['x'] = x
            value['y'] = y
            #bucketização
            value = bucketizacao(value)
            temp = []
            for key2, value2 in value.iteritems():
                if key2 not in ["user",'rWidth','rHeight']:
                    temp.append(float(value2))
            if x > y:
                newData.append(temp)
            elif x < y:
                newData.append(temp)

        return newData
    def base_onlineLearning(self, nameFile):
        try:
            with codecs.open(nameFile, 'r', encoding='utf-8') as f:
                fileData = json.load(f)
        except:
            fileData = []

        for line in fileData:
            # data
            self.data.append(line[:len(line)-1])
            # label
            self.label.append(line[-1])

    def base_inicial(self, nameFile):
        with codecs.open(nameFile, 'r', encoding='utf-8') as f:
                    fileData = json.load(f)
        newData = []
        newLabel = []
        for line in fileData:
            # data
            newData.append(line[:len(line)-1])
            # label
            newLabel.append(line[-1])

        return newData, newLabel

def accuracy(labels, predict):
    count = 0
    for k, value in enumerate(labels):
        # acertou :)
        if value == predict[k]:
            count += 1
    return float(float(count)/float(len(labels)))

def crossValidation(images, labels, percent):
    # index já sortiados
    indexUsados = []
    # images train
    imagesTrain = []
    labelsTrain = []
    # images test
    imagesTest = []
    labelsTest = []
    # enquanto número de imagens de train for menor que o percent X images
    while len(imagesTrain) < percent*len(images):
        index = np.random.random_integers(len(images)-1)
        if index not in indexUsados:
            # train
            imagesTrain.append(images[index])
            labelsTrain.append(labels[index])
            # add index
            indexUsados.append(index)
        # copia valores que não estao no Train
        for k, value in enumerate(images):
            if k not in indexUsados:
                imagesTest.append(images[k])
                labelsTest.append(labels[k])

    return imagesTrain, labelsTrain, imagesTest, labelsTest


def bucketizacao(value):
    # click
    if value['clickA'] > 5:
        value['BA'] = 0
        value['BBA'] = 0
        value['bA'] = 1
    elif value['clickA'] >= 2:
        value['BA'] = 0
        value['BBA'] = 1
        value['bA'] = 0
    else:
        value['BA'] = 1
        value['BBA'] = 0
        value['bA'] = 0
    if value['clickB'] > 5:
        value['BB'] = 0
        value['BBB'] = 0
        value['bB'] = 1
    elif value['clickB'] >= 2:
        value['BB'] = 0
        value['BBB'] = 1
        value['bB'] = 0
    else:
        value['BB'] = 1
        value['BBB'] = 0
        value['bB'] = 0

    if value['countA'] > 15:
        value['CBA'] = 0
        value['CBBA'] = 0
        value['CbA'] = 1
    elif value['countA'] >= 7:
        value['CBA'] = 0
        value['CBBA'] = 1
        value['CbA'] = 0
    else:
        value['CBA'] = 1
        value['CBBA'] = 0
        value['CbA'] = 0
    if value['countB'] > 15:
        value['CBB'] = 0
        value['CBBB'] = 0
        value['CbB'] = 1
    elif value['countB'] >= 7:
        value['CBB'] = 0
        value['CBBB'] = 1
        value['CbB'] = 0
    else:
        value['CBB'] = 1
        value['CBBB'] = 0
        value['CbB'] = 0

    return value
