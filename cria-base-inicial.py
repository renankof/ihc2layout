#!/bin/python
#coding: UTF-8
import json
import codecs

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

def normaliza(data):
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

def normaliza_teste(data, nMin, nMax):
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

with codecs.open('data.json', 'r', encoding='utf-8') as f:
            fileData = json.load(f)

#print len(fileData)

count = 0
countA = 0
countB = 0
countExcluido = 0
data = []
label = []
for key, value in fileData.iteritems():
    #if int(value['sessionTime']) > 100 and int(value['countA']) > 0 and int(value['countB']) > 0:
    if (int(value['sessionTime']) > 100) and int(value['countA']) > 0 or int(value['countB']) > 0:
     
        
        #print "[%sx%s] %s -> %s - %s/%s - %s/%s"%(value['rWidth'], value['rHeight'],key,value['sessionTime'], value['countA'], value['timeA'], value['countB'], value['timeB'])
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
        
        if x>y:
            countA += 1
            count += 1
            label.append("typeA")
            data.append(temp)
        elif x<y:
            countB += 1
            count += 1
            label.append("typeB")
            data.append(temp)
        else:
            countExcluido += 1
            #print "[%sx%s] %s -> %s - %s/%s - %s/%s"%(value['rWidth'], value['rHeight'],key,value['sessionTime'], value['timeA'],value['countA'],  value['timeB'],value['countB'])
    
    else:
        countExcluido += 1
        #print "[%sx%s] %s -> %s - %s/%s - %s/%s"%(value['rWidth'], value['rHeight'],key,value['sessionTime'], value['countA'], value['timeA'], value['countB'], value['timeB'])

print "Total Geral:",count+countExcluido
print "Excluido", countExcluido

print "Total:", count
print "typeA: ",countA
print "typeB: ",countB



# copia data para fileData
fileData = data[:]

# cria um array unico com data e label
for index, listValue in enumerate(fileData):
    listValue.append(label[index])

# salva fileData em json
with open('data-inicial.json',  'w') as f:
    json.dump(fileData, f)