from selenium import webdriver
import time
from keras import models,layers
import matplotlib.pyplot as plt
import tensorflow
import pandas as pd
import numpy as np
from keras.preprocessing.text import text_to_word_sequence
from keras.preprocessing.text import one_hot

try:
    driver=webdriver.Chrome("chromedriver.exe")
    driver.get("https://www.boletinoficial.gob.ar/#!Portada/primera/all")
    time.sleep(5)

    

    all_h2 = driver.find_elements_by_xpath("//*[@id='Primera']/h2[@class='ttlsection']")
    all_items = driver.find_elements_by_xpath("//*[@id='Primera']/div[@id='PorCadaNorma']")
    all_detalle_norma=driver.find_elements_by_xpath("//html/body/section[3]/div[2]/div[1]/section[1]/div[2]/div[1]/div")
    h2index=range(1,len(all_h2)+1)
    h3indexahref=range(1,len(all_items)+1)
    all_detalle_norma_rango=len(all_detalle_norma)
    
    print("=====================================================================================")
    listarubro=[]#LISTA DE RUBROS
    print("=====================================================================================")
    #INSERTAR ELEMENTOS A LISTA DE RUBROS
    for i in h2index:
        span=driver.find_element_by_xpath("/html/body/section[3]/div[2]/div[1]/div[6]/h2[{}]/span[1]".format(i))
        listarubro.append(span.text)
    #===========================================FIN INSERT

    print("=====================================================================================")
    listanorma=[]#LISTA DE NORMAS
    print("=====================================================================================")
    #INSERTAR ELEMENTOS A LISTA DE NORMAS
    for i in h3indexahref:
        ahref=driver.find_element_by_xpath("/html/body/section[3]/div[2]/div[1]/div[6]/div[{}]/div/h3/a".format(i))
        listanorma.append(ahref.text)
        
        
    #========================================FIN INSERT
        
    #=====================================================================
    #CREACION DE LISTA CON TODOS LOS ELEMENTOS DE PRIMERA SECCION
    divprimera=driver.find_element_by_xpath('//*[@id="Primera"]')
    divprimertext=divprimera.text
    listprimer=[]
    #=====================================================================FIN CREACION
    
    #LIMPIEZA E INSERSION DE DATOS A LISTA DE PRIMERA SECCION
    listprimer.append(divprimertext.split("\n"))
    primerlen=len(listprimer[0])
    #===========================================================FIN LIMPIEZA

    #=======================================================================
    #CREACION DE LISTA CON RUBRO Y DETALLENORMA ADENTRO FORMATO = 'RUBRO',[DETALLENORMA],'RUBRO',[DETALLENORMA]
    listaseparacion=[]
    for i in listprimer[0]:
        if i in listarubro:
            listaseparacion.append(i)
        if i in listanorma:
            listaseparacion.append(list([i]))
    #================================================FIN LISTA 'RUBRO',['DETALLENORMA']

    #==========================================================
    #CREACION DE DICCIONARIO {'RUBRO':[DETALLENORMA PERTENECIENTE A CADA RUBRO]}
    diccionarie={}
    def agregar_key(dictio):
        for i in listarubro:
            dictio[i]=[]
        keys=[]
        keys.extend(diccionarie.keys())
        key=keys[0]
        for i in listaseparacion:
            if i in keys:
                key=i
            else:
                diccionarie[key].extend(i)
        return dictio
            
    agregar_key(diccionarie)
    #====================================================FIN DICCIONARIO{'RUBRO':[DETALLENORMA]}
except:
    raise
finally:
    driver.close()

#### a partir de esta celda se encuentra los pasos para la creacion del Dataset con los datos de rubro,norma
#### que se actualizan si hay mas rubros,normas disponibles cada vez que ejecutamos el codigo anterior

#creacion del dataframe a partir del diccionario creado anteriormente, con un reset de indices para un mejor manejo
datos=pd.DataFrame.from_dict(diccionarie,orient="index").reset_index()

#convertimos los datos a strings para el manejo de los nonetype values y que no nos tire error 
x=datos.astype('str')

X=x.iloc[:,0:1]
X=X.values

#Convertimos el dataFrame de pandas en un ndarray de numpy para el manejo de los valores
Y=x.iloc[:,1:]
Y=Y.values
#lo mismo del anterior paso

"""
Con esta funcion  separamos los datos test- train %25 %75 respectivamente 
( aunque los datos sean pocos esta seria una buena practica del manejo de los mismos)
luego utilizamos la funcion one_hot de keras para generar de las palabras enteros que utilizaremos para 
convertirlos a arrays, tambien se crea get_id un diccionario que se utiliza para asignarle id(estos enteros)
a las palabras correspondientes

"""
def one_encoding(data):
    words=set(text_to_word_sequence(str(data),filters="!”#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t'\n"))
    size=len(words)
    result = one_hot(str(data), round(size*1.3))
    label=[]
    train_data=[]
    test_data=[]
    get_id={}
    for i in words :
        a=one_hot(str(i),round(size*1.3))
        b=i
        label.extend([a])
        get_id[b]=str(a)
    for i in range(round(len(label)*0.75)):
        train_data.append(i)
    for i in range(round(len(label)*0.25)):
        test_data.append(i)
    return train_data,test_data

#la funcion nos devuelve 2 parametros (listas)

x_train_data,x_test_data=one_encoding(X)
train_labels,test_labels=one_encoding(Y)

#con esta funcion vamos a vectorizar los enteros a numpy arrays
def vectorizar(sequences,dimension=1000):
    results=np.zeros((len(sequences),dimension))
    for i,sequence in enumerate(sequences):
        results[i,sequence]=1.
        return results
y_labels_train=vectorizar(x_train_data)
y_label_test=vectorizar(x_test_data)
x_train=vectorizar(train_labels)
x_test=vectorizar(test_labels)

y_labels_train=np.asarray(train_labels).astype('float32')
y_labels_test=np.asarray(test_labels).astype('float32')

#utilizamos col en vez de un valor fijo para input_shape, para que el codigo tenga un poco mas de flexibilidad
col=x_train.shape[1]

### a partir de esta celda se encuentra la creacion del modelo con keras (tensorflow backend)

#creacion del modelo con keras(tensorflow backend)
model=models.Sequential()
model.add(layers.Dense(3,activation='relu',input_shape=(col,)))
model.add(layers.Dense(3,activation='relu'))
model.add(layers.Dense(1,activation='sigmoid'))
#utilizaremos un modelo secuencial para un mejor manejo de secuencias(palabras)

model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])
#compilamos el modelo con algoritmo de optimizacion adam,de perdida binary_crossentropy (manejo de inputs binarios)

history=model.fit(x_train[:7],y_labels_train[:7],epochs=20,batch_size=1,validation_data=(x_train[7:15],y_labels_test[7:15]))
#entrenamiento de nuestro modelo

# se ve horrible ya que tiene muy pocos ejemplos
history_dict=history.history
history_dict.keys()

### utilizaremos las dict keys para generar graficos con matplotlib.pytplot

acc=history.history['acc']
val_acc=history.history['val_acc']
loss=history.history['loss']
val_loss=history.history['val_loss']
epochs=range(1,len(acc)+1)
plt.plot(epochs,loss,'bo',label='Training loss')
plt.plot(epochs,val_loss,'b',label="Validation loss")
plt.title('Training and accuracy')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.show()

plt.clf()#figura limpia
acc_values=history_dict['acc']
val_acc_values=history_dict['val_acc']


"""bo es por blue dot"""
plt.plot(epochs,acc,'bo',label='Training acc')
"""b es por solid blue line"""
plt.plot(epochs,val_acc,'b',label="Validation acc")
plt.title('validation accuracy and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.show()
