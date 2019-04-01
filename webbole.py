from selenium import webdriver
import time,re

try:
    driver=webdriver.Chrome("chromedriver.exe")
    driver.get("https://www.boletinoficial.gob.ar/#!Portada/primera/all")
    time.sleep(5)

    

    all_h2 = driver.find_elements_by_xpath("//*[@id='Primera']/h2[@class='ttlsection']")
    all_items = driver.find_elements_by_xpath("//*[@id='Primera']/div[@id='PorCadaNorma']")
    h2index=range(1,len(all_h2)+1)
    h3indexahref=range(1,len(all_items)+1)
    print(max(h2index),max(h3indexahref))
    
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
    print(diccionarie)
    """
    keys=[]
    keys.extend(diccionarie.keys())
    key=keys[0]
    for i in listaseparacion:
        if i in keys:
            key=i
        else:
            diccionarie[key].extend(i)
    print(diccionarie)
    """

except:
    raise
finally:
    driver.close()

