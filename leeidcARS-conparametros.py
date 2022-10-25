## test de prueba de Lectura de IDC de NCR ARS 
# Con Python. 
## Por Jorge Centeno - 3 de Octubre de 2022.
#  Lectura de Registros de  NCR ARS POS

from ast import Break, Try
from asyncore import file_wrapper
from encodings.utf_8_sig import decode
import os
import os.path
import platform
from socketserver import ThreadingUnixStreamServer

import tempfile, shutil
from os import path
import re
from colorama import Fore

import requests
import json
#from symbol import term
import sys
from difflib import get_close_matches
from xml.dom.minidom import Element
from xmlrpc.client import Boolean 
# para progress bar
from tqdm import tqdm
import time
import logging
import tkinter
from tkinter import messagebox

import textwrap

from pdf417 import encode, render_image

import webbrowser
from PyPDF4 import PdfFileWriter, PdfFileReader 
import PyPDF4
from dotenv import load_dotenv

import qrcode
from fpdf import FPDF
from turtle import pd
main_path = os.path.dirname(__file__)
queOSystem= platform.system()
ServerId=''
if queOSystem =='Linux':
    pathData="data//"
    pathLog="logs//"
    pathleerIDC="lectura//"
    pathleerJson="json//"
    pathJournal="journal//"
    ServerId='Linux'
elif queOSystem =='Darwin':  ## esto es mac
    pathData="data//"
    pathLog="logs//"
    pathleerIDC="lectura//"
    pathJson="json//"
    pathJournal="journal//"
    ServerId='MAC Darwin'
else:
    pathData="data\\"   #Windows 
    pathLog="logs\\"
    pathleerIDC="lectura\\"
    pathJson="json\\"
    pathJournal="journal\\"
    ServerId='Windows'
detalleRuta=pathData+'\n'+pathLog+'\n'+pathleerIDC+pathJournal+'\n'+pathleerIDC+'\n'

file_log = os.path.join(main_path,pathLog+"leerIdcArs.log")
logging.basicConfig(filename=file_log,level=logging.INFO,format='%(process)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s',filemode='w', datefmt='%m/%d/%Y %I:%M:%S %p', encoding='utf-8')
logging.critical('Iniciamos registro en:'+file_log)
logging.critical(ServerId)
logging.critical('se Carga los path '+detalleRuta)

load_dotenv()
# Buscando  Variables de Enviaroment.
token=os.environ.get("api-Token")
mostrar_Pdf=os.environ.get("mostrar_Pdf")
companyLicCod=os.environ.get("companyLicCod")
apiKey=os.environ.get("apiKey")
url_Pac_Proveedor=os.environ.get("url_Pac_Proveedor")
acumularDescto=os.environ.get("acumularDescto")
fileFirmaDeAgua=os.environ.get("fileFirmaDeAgua")
logoCompania=os.environ.get("logoCompania")
verFileJson=os.environ.get("verFileJson")

file_log = os.path.join(main_path,pathLog+"leerIdcArs.log")
logging.basicConfig(filename=file_log,level=logging.INFO,format='%(process)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s',filemode='w', datefmt='%m/%d/%Y %I:%M:%S %p', encoding='utf-8')

logging.warning('Iniciando, Se cargaron los Environ')
# Paramentro 1 es idc y 2= factura.
LeerTodoFileSinFactura=0
if len(sys.argv)==3:#
    # hay IDC y Factura
    fileIdcAprocesar=(sys.argv[1]) #archviso idc
    factura =(sys.argv[2])
    LeerTodoFileSinFacturas=0
    logging.info('Se enviaron 3 Paramentros:File y Transaccion')
    
elif len(sys.argv)==2:
      # solo idc
      LeerTodoFileSinFactura=1 
      fileIdcAprocesar=(sys.argv[1])
      factura ="ALL"
      logging.info('Se enviaron 2 Paramentros:Solo File')
      
else:
      print('Falta definir 2 pararmetros(IDC Y FACTURA): ejemplo: leeridcARS S_IDC001.DAT 8290')
      logging.error('Falta definir 2 pararmetros(IDC Y FACTURA): leeridcARS S_IDC001.DAT 8290')
      exit()

# Creating of pdf class to perform operations
title = 'Lector de Idc'
# Ubicacion de lectura.. file PLU

filePluLocal='M_HSHPLU.DAT'

logging.debug('Path del app'+main_path)
logging.debug('Path del dataPLU:'+pathData)
logging.debug('Archivos PLU:'+filePluLocal)

fileprocess =fileIdcAprocesar  #"S_IDC001.DAT" 

try:
    file_idc = os.path.join(main_path,pathleerIDC+fileprocess )
except ValueError:
    logging.debug(ValueError)  

fileIdcExiste = os.path.exists(file_idc)
logging.error('revisando si existe el file IDC:'+file_idc)
if not fileIdcExiste:
    logging.error('No se encuentra el Archivos IDC:'+file_idc)
    logging.error(os.path.exists(file_idc))
    logging.error('bye bye'+fileprocess)
    print("Falta file IDC")
    exit()
logging.debug('Existe el file,procesando:'+file_idc)
file_path = os.path.join(main_path,pathData+filePluLocal)

filePluExiste = os.path.exists(file_path)
if filePluExiste:
     with open(file_path,encoding='windows-1254') as f:
        datafile = f.readlines()
        logging.info('lectura de '+file_path)
else:
    logging.error('No se encuentra file PLU: '+file_path)
    logging.error('Adios'+file_path)
    exit() 
thislist =[]
listReg_F=[]
listReg_S=[]
listReg_H=[]
listReg_W=[]
listReg_W=[]
listReg_T=[]
listReg_V=[]
listReg_U=[]
listReg_K=[]
listReg_a=[]
listReg_j=[]
listReg_C=[]
List_Trn=[]
new_listS =[]
listReg_c_filtro=[]
listItemsJson=[]
# Diccionarion de tabulacion de registro S
#012345678901234567890123456789012345678901234567890123456789012345678901234567890
#0202:009:220223:160412:1673:002:S:101:0001:    842135000599+00010010*000000219
#   1   2      3      4    5   6 7 8   9    10               11       12     
punteroTrans=""
global fileJsonWebPos
global fileJson
fileJsonWebPos=""
# The notifier function
def put_watermark(input_pdf, output_pdf, watermark): 
    watermark_instance = PdfFileReader(watermark) 
    watermark_page = watermark_instance.getPage(0) 
    pdf_reader = PdfFileReader(input_pdf) 
    pdf_writer = PdfFileWriter() 
    for page in range(pdf_reader.getNumPages()): 
        page = pdf_reader.getPage(page) 
        page.mergePage(watermark_page) 
        pdf_writer.addPage(page) 
    with open(output_pdf, 'wb') as out: 
        pdf_writer.write(out) 
def notify(title, subtitle, message):
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    os.system('terminal-notifier {}'.format(' '.join([m, t, s])))

def text_to_pdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')
    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)
    pdf.output(filename, 'F')
 # funcion de adicionar registros.  
def add_registro(linea,lista):
       lista.append(linea)
def ver_lista(lista):
    return print(lista)
def closeMatches(patterns, word): 
     return get_close_matches(word, patterns) 
def remove(string):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', string)
def buscar(elemento_de_interes, l,code):
    for index, element in enumerate(l):
        tienda_  =(element[0:4])
        terminal_=(element[5:8])
        fecha_   =(element[9:15])
        hora_    =(element[17:22])
        transa_  =(element[23:27])
        puntero_= tienda_+terminal_+fecha_+transa_+code
        if puntero_ == elemento_de_interes:
            return index
    return -1
def detalle(elemento_de_interes, list_proces,code):
    new_listS.clear()
    for x in list_proces:
        tienda_  =(x[0:4])
        terminal_=(x[5:8])
        fecha_   =(x[9:15])
        hora_    =(x[17:22])
        transa_  =(x[23:27])
        _puntero= tienda_+terminal_+fecha_+transa_+code
        if _puntero == elemento_de_interes:
            new_listS.append(x)
def check(searchplu):
    global found
    global PluMaster
    found = False
    for line in datafile:
        if searchplu in line:
            found = True
            PluMaster=line
## proces de leer transcioones una
# o todas el file
def enviarAlApi():
    fileDiccionario= file_pathJson
    logging.info('Procesando file Diccionario'+ fileDiccionario)
    #url_Pac_Proveedor provee los de Webpos por ahora
    rutaWebPos=url_Pac_Proveedor+fileDiccionario
    logging.critical('haciendo el llamado al api \n'+rutaWebPos)
    x = requests.post(rutaWebPos)
    with open(fileDiccionario, "rb") as a_file:
                file_dict = {fileDiccionario: a_file}
                response = requests.post(rutaWebPos, files=file_dict)
                if response:
                    logging.warning('Respuesta OK del API ')
                    logging.info(response.status_code)
                else:
                    logging.error('Falla de Respuesta del API ')
                    logging.error(response.status_code)
                    logging.info(response.text)
                    logging.critical(x.text)
    #messagebox.showwarning("Respuesta",response.text)
                    
def procesarTrx(h):
    global fileJsonWebPos
    global filePdfTicket
    global fileJson
    global file_pathTicketPdfFirma
    global file_pathJson
    secuenc =(h[28:31])
    puntero= tienda+terminal+fecha+transa+"F"
    ## Valores de code1=
         #0 = Money trans. 
         #1 = Sale trans.
         #2 = Receipt abort 
        #3 = Training
        #4 = Re-entry
        #5 = Stock-count 6 = Transfers
        #7 = Layaways
        #8 = Suspend
        #9 = Reset mode
      
        # Valores de code2=
        #0 = Normal data entry
        #5 = Preselect Transaction Return 
        #6 = Preselect Transaction Void
        #8 = Transaction Return/Void
        
        # valores de code3 =
        #0 = Without surcharge
        #2 = Invoice on Charge tender
        #4 = With surcharge (e.g. delivery)
        
    code1   =(h[34:35])
    code2   =(h[35:36])
    code3   =(h[36:37])
    opera   =(h[39:42])
    adicional=(h[44:60])
    accode   =(h[60:79])
    hayf   =buscar(puntero,listReg_F,"F")
    codetrx=code1+code2+code3
    # Escribe en json el tienda:
    #print(encabezadoH)
    listItemsJson.clear
    if codetrx == "100":
        logging.info('Sólo código '+codetrx)
        if ( hayf >0):
                logging.info('Procesando  '+'H'+'Con factura'+transa)
                logging.info('hay registro '+'F indicativo que es una Ventas con H y F')
                 #Formatos de file de Salida.
                tipoFileJsonInicio ="FE-14c-"
                tipoFileTxtIncio ="ARS-POS"
                tipoFileJsonFinal="-ConsumidorFinal.json"
                tipoFileTxtFinal="-Journal.txt"
                tipoFilePdfFinal=".pdf"
                patronFile =tienda+terminal+fecha+hora+"-"+transa
                fileJson = tipoFileJsonInicio+patronFile+tipoFileJsonFinal
                filePosTicket =tipoFileTxtIncio+patronFile+tipoFileTxtFinal
                filePdfTicket =tipoFileTxtIncio+patronFile+tipoFilePdfFinal
                filePdfTicketFirma="POS-"+terminal+"-"+patronFile+tipoFilePdfFinal
                logging.info('Borrando file pdf,json y txt')
                
                file_pathJson          =os.path.join(main_path,pathJson+fileJson)
                file_pathTicket        =os.path.join(main_path,pathJournal+filePosTicket)
                file_pathTicketPdf     =os.path.join(main_path,pathJournal+filePdfTicket)
                file_pathTicketPdfFirma=os.path.join(main_path,pathJournal+filePdfTicketFirma)
                
                if os.path.exists(file_pathJson):
                    os.remove(file_pathJson)
                    logging.info('se borro file:'+file_pathJson)
                else:
                    logging.error('No se Encontro file:'+file_pathJson)
                if os.path.exists(file_pathTicket):
                    os.remove(file_pathTicket)
                    logging.info('se borro file :'+file_pathTicket)
                else:
                    logging.error('No se Encontro file:'+file_pathTicket)
                path = r'tools'

                fileJsonWebPos = open(file_pathJson, "w")
                logging.info('se abre el file json:'+file_pathJson)
                fileTickNcrArs = open(file_pathTicket, "w")
                logging.info('se abre el file txt: '+file_pathTicket)
                fileJsonWebPos.write("{ ")
                fileJsonWebPos.write('"fiscalDoc": { \n')
                
                fileJsonWebPos.write('"companyLicCod":"'+companyLicCod+'", \n')
                fileJsonWebPos.write('"apiKey":"'+apiKey+'", \n')
                fileJsonWebPos.write('"branchCod": "'+tienda+'",\n')
                fileJsonWebPos.write('"posCod": "'+terminal+'",\n')

                if code1 =="1" and code2==0:
                        fileJson.write('"docType":"F",\n')
                        logging.info('se escribe doc Type =F Facturas')
                else:
                    if code1 =="1" and code2==6 or code2==8:
                        fileJsonWebPos.write('"docType":"C",\n')
                        logging.info('se escribe doc Type =C Nocta de Credito')
                fileJsonWebPos.write('"docNumber": "'+transa+'",\n')
                fileJsonWebPos.write('"customerName":"Cliente Genérico",\n')
                fileJsonWebPos.write('"customerRUC":"",\n')
                ##07 es consumidor final, hay que ver los otros caso.
                fileJsonWebPos.write('"customerType": "07",\n')
                fileJsonWebPos.write('"customerAddress":"",\n')
                fileJsonWebPos.write('"email":"jcc@webpospanama.com",\n')
                fileJsonWebPos.write('"addInfo":[\n')
                fileJsonWebPos.write('{"id":1,"value":"Numero de pedido: 12345" },\n')
                a='{"id":2,"value":"Entrega en sitio" \n}'
                fileJsonWebPos.write(a)
                fileJsonWebPos.write('],\n')
                #items
                fileJsonWebPos.write('"items":[\n')
                encabezadoF =listReg_F[hayf]
                cajero =encabezadoF[38:42]
                countItem=encabezadoF[62:68]
                total=encabezadoF[68:79]
               
                #print(encabezadoF)
                logging.info('se escribe en file txt: '+file_pathTicket)
                
                encabezado1="Tienda:"+tienda+" Term:"+terminal+" Fecha:"+fecha+" Hora:"+hora+" Op"+cajero+'\n'
                encabezado2="Fact:"+transa+" Sec:"+secuenc+"AC:"+code1+code2+code3+" Trx:"+opera+'\n'
                encabezado3="------------------------------------------------\n"
                
                fileTickNcrArs.write(encabezado1)
                fileTickNcrArs.write(encabezado2)
                fileTickNcrArs.write(encabezado3)
                
                #print("adicional:"+adicional+"--"+accode)
                fileTickNcrArs.write("ARTICULOS :"+str(int(countItem))+'\n')
                fileTickNcrArs.write("T O T A L :"+str(float(total)/100)+'\n')
                puntero= tienda+terminal+fecha+transa+"S"
                puntero_c= tienda+terminal+fecha+transa+"C"
                detalle(puntero,listReg_S,"S")
                puntero_v= tienda+terminal+fecha+transa+"V"
                puntero_t= tienda+terminal+fecha+transa+"T"
                puntero_u= tienda+terminal+fecha+transa+"U"
                # presento solo pos S de esa transaccion
                largoListRegS=  len(new_listS)
                for idx, hh in enumerate(new_listS):
                    logging.info('Procesando registro S de transaccion:'+transa)
                    plu = (hh[44:59])
                    pluJson =plu.lstrip()
                    qty = (hh[60:68])
                    signo = qty[0:1]
                    qtyI = int((qty[1:4]))
                    if qtyI ==0:
                        qtyI=1
                    deciI=(qty[4:5])
                    amount=(hh[70:80])
                    #buscamos detalles del registro K para ver si tiene detalles de plu  promo
                    puntero_k= tienda+terminal+fecha+transa+"K"+plu
                    # buscar descripcion en hshPlu
                    fileTickNcrArs.write(""+str(idx+1)+" "+plu+" "+str(qtyI)+" "+str(int(amount)/100)+'\n')
                   
                    check(plu)
                    logging.info('Se busca el PLU:'+plu)
                    descripcion='DPT'
                    tax='0'
                    if found == True:
                        tax =PluMaster[24:25]
                        if tax=="0":
                            taxcode="E"
                        elif tax =="1" or tax =="2" or tax =="3" :
                             taxcod="G"
                        descripcion=PluMaster[36:57]
                        fileTickNcrArs.write('['+taxcode+']'+'    '+descripcion+'\n')
                        logging.info('Se encontro PLU:'+descripcion)                   
                    else:
                        fileTickNcrArs.write('Upc?\n')
                        logging.info('Plu no Encontrado en Hash')                   
                  
                    hayDectos=False 
                    desctok2 ='0'   
                    
                    for k in listReg_K:  
                        #print(k)
                        tienda_k  =(k[0:4])
                        terminal_k=(k[5:8])
                        fecha_k   =(k[9:15])
                        hora_k    =(k[17:22])
                        transa_k  =(k[23:27]) 
                        plu_k     =(k[44:59])
                        puntero_filtrok= tienda_k+terminal_k+fecha_k+transa_k+"K"+plu_k
                      
                        if puntero_k == puntero_filtrok: 
                            
                            desctok= str(int(k[68:79])/100)   
                            desctok2=str(abs(int(k[68:79])/100))
                            fileTickNcrArs.write('              promo:'+desctok+'\n')
                            hayDectos= True
                    #  
                     #{ "id":1,"qty":10.00,"code":"P001","desc":"Producto ITBMS 7%","price":10.0000,"tax":1,"comments":"La propiedad price es precio unitario","dperc":"10%","damt":0 },                
                    if (idx+1) == largoListRegS:
                        fileJsonWebPos.write('{ "id":'+str(idx+1)+',"qty":'+str(float(qtyI))+',"code":"'+pluJson+'","desc":"'+descripcion+'","price":'+str(float(amount)/100)+',"tax":'+tax+',"comments":"precio expresado en unid",'+'"dperc":"00%",'+'"damt":'+desctok2+'}\n')  
                    else:
                         fileJsonWebPos.write('{ "id":'+str(idx+1)+',"qty":'+str(float(qtyI))+',"code":"'+pluJson+'","desc":"'+descripcion+'","price":'+str(float(amount)/100)+',"tax":'+tax+',"comments":"precio expresado en unid",'+'"dperc":"00%",'+'"damt":'+desctok2+'},\n')  
                fileJsonWebPos.write(' ],\n') 
                #descuentos
                fileJsonWebPos.write('"discount":{\n') 
                # Filtar todos los registro C para esta transaccion:
                # Preesento los C(Promocion ) de esa transaccion
                listReg_c_filtro.clear
                anyPromototal= 0
                totaldescto=0
                for c in listReg_C:
                        encabezadoC=c
                        #print(encabezadoC)
                        tienda_c  =(c[0:4])
                        terminal_c=(c[5:8])
                        fecha_c   =(c[9:15])
                        hora_c    =(c[17:22])
                        transa_c  =(c[23:27])
                        puntero_filtro= tienda_c+terminal_c+fecha_c+transa_c+"C"
                        
                        if puntero_c == puntero_filtro:
                             listReg_c_filtro.append(c)
                             dp_detalle =c[43:59]
                             dp_detalle =(remove(dp_detalle))
                             signo =c[68:69]
                             descto =(float(c[69:78])/100)
                             if acumularDescto=="1":
                                 totaldescto = totaldescto + (float(c[69:78])/100)
                                 logging.info('Procesando Descuento acumualdo '+ str(totaldescto))
                             else:
                                 fileJsonWebPos.write('   "perc":"0%","amt":'+str(round(totaldescto, 2))+'\n')
                             fileTickNcrArs.write("T.Desc:"+dp_detalle+signo+str(descto)+'\n')
                             anyPromototal=1
                             logging.info('Procesando Promos '+"T.Desc:"+dp_detalle+signo+str(descto))
                fileTickNcrArs.write("================================================="+'\n')
                
                if anyPromototal==0:
                     fileJsonWebPos.write('   "perc":"0%","amt":0\n')
                     #si el parametros de detalla descuento en Json
                elif acumularDescto =="1" and totaldescto>0:
                     fileJsonWebPos.write('   "perc":"0%","amt":'+str(round(totaldescto, 2))+'\n')
                fileJsonWebPos.write('},\n'  )    
                #registros V 
                fileJsonWebPos.write('"payments":[\n'  )
                for v in listReg_V:  
                        #print(k)
                        tienda_v  =(v[0:4])
                        terminal_v=(v[5:8])
                        fecha_v   =(v[9:15])
                        hora_v    =(v[17:22])
                        transa_v  =(v[23:27]) 
                        puntero_filtrov= tienda_v+terminal_v+fecha_v+transa_v+"V"
                      
                        if puntero_v == puntero_filtrov: 
                            idtax_detalle= (v[44:59]) 
                            idtax_counter = str(int(v[63:68])) 
                            idtax_amount  = str(float(v[70:78])/100)   
                            fileTickNcrArs.write(idtax_detalle+" Art "+idtax_counter+" Tot:"+idtax_amount+'\n')
                fileTickNcrArs.write("T O T A L: "+str(float(total)/100)+'\n')
                logging.info('Procesando Impuestos ')
                
                for t in listReg_T:  
                        #print(k)
                        tienda_t  =(t[0:4])
                        terminal_t=(t[5:8])
                        fecha_t   =(t[9:15])
                        hora_t    =(t[17:22])
                        transa_t  =(t[23:27]) 
                        puntero_filtrot= tienda_t+terminal_t+fecha_t+transa_t+"T"
                        contador =0
                        descripPago="Otros"
                        if puntero_t == puntero_filtrot: 
                            idpago= (t[60:62])
                            idpagoCounter = str(int(t[63:68]))
                            idpagoAmount  = str(float(t[69:79])/100)
                            idpagosigno  =(t[68:69])
                              #{ "id":1,"type":"01","amt":500.00,"desc1":"EFECTIVO" }
                                    #type: tipo de pago
                                    #Tipos:
                                    #01= Efectivo,
                                    #02=CREDIT CARD,
                                    #03=DEBIT CARD, 04=CHEQUE, 05=Otro,
                                    #06=Otro,
                                    #07=Nota de crédito,
                                    #08=Credito (No se recibe pago), 09=Otro
                               
                            if idpago =="01":
                                descripPago="EFECTIVO"
                            else:
                                 if idpago=="02":
                                    descripPago="TARJ.CREDITO"
                                
                            if idpagosigno =="+":
                                    fileTickNcrArs.write("--- PAGO   "+idpago+" "+idpagoCounter+" Monto "+idpagoAmount+'\n')
                                    contador +=1
                                    fileJsonWebPos.write('{"id":'+str(contador)+',"type":"'+idpago+'","amt":'+idpagoAmount+',"desc1":"'+descripPago+'"}\n'  )
                            else:
                                if idpagosigno =="-":
                                    idpagoAmount = idpagoAmount  
                                    fileTickNcrArs.write("--- CAMBIO "+idpago+' '+idpagoCounter+" Monto "+idpagoAmount+'\n')
                logging.info('Procesando forma de pagos')
               
                fileJsonWebPos.write('],\n')
                fileJsonWebPos.write('"trailer": [\n')
                contadorTrailer=0
                listTrailer=[]
                for u in listReg_U:  
                        #print(k)
                        tienda_u  =(u[0:4])
                        terminal_u=(u[5:8])
                        fecha_u   =(u[9:15])
                        hora_u    =(u[17:22])
                        transa_u  =(u[23:27]) 
                        puntero_filtrou= tienda_u+terminal_u+fecha_u+transa_u+"U"
                     
                        if puntero_u == puntero_filtrou: 
                            contadorTrailer+=1
                            idDetalle= (u[43:51])
                            idU= (u[60:77])
                            fileTickNcrArs.write(idDetalle+" "+idU+'\n')
                            listTrailer.append('{"id":'+str(contadorTrailer)+',"value":"'+idDetalle+' '+idU+'"},\n')
                            #{ "id":1,"value":"Información al final" },
	                        #{ "id":2,"value":"Información al final" 
                totalLineaTrailer =len(listTrailer)
                #print(totalLineaTrailer)
                #for idx, hh in enumerate(new_listS):
                for fila,tt in enumerate(listTrailer):
                    fileJsonWebPos.write(tt)
                    if fila == totalLineaTrailer-1:       
                        pInicio=(tt.find("{"))
                        pFin  =(tt.find("}"))
                        fileJsonWebPos.write(tt[pInicio:pFin+1])
                    #breakpoint    
                logging.info('Procesando trailer ')
                fileTickNcrArs.write(encabezado1)
                fileTickNcrArs.write(encabezado2)
                fileTickNcrArs.write(encabezado3)
                
                fileJsonWebPos.write(']\n')
                fileJsonWebPos.write('}\n')
                fileJsonWebPos.write('}\n')
                
                fileJsonWebPos.close()
                fileTickNcrArs.close()
                
                #Genera un Pdf de ticket procesado.
                title = encabezado1
                pdf = FPDF()
                pdf.set_title("QR Codes")
                pdf.add_page()
                pdf.alias_nb_pages()
                
                pdf.set_font('helvetica', '', 11.0)
                pdf.set_xy(105.0, 8.0)
                pdf.cell(ln=0, h=22.0, align='C', w=75.0, txt=tienda, border=0)
                pdf.image('logo.png', 20.0, 17.0, link='', type='', w=50.0, h=20.0)
                pdf.set_font('arial', 'B', 16.0)
                pdf.set_xy(95.0, 18.0)
                pdf.set_font('arial', '', 8.0)
                pdf.set_xy(105.0, 21.0)
                pdf.cell(ln=0, h=4.0, align='C', w=75.0, txt='Tienda', border=0)
                pdf.set_font('arial', 'B', 7.0)
                pdf.set_xy(125.0, 21.5)
                pdf.cell(ln=0, h=4.5, align='C', w=10.0, txt='Copia', border=0)
                pdf.set_font('arial', 'B', 14.0)
                pdf.set_xy(136.0, 25.5)
                pdf.cell(ln=0, h=9.5, align='L', w=60.0, txt=transa, border=0)
                pdf.set_xy(125.0, 27.5)
                pdf.cell(ln=0, h=5.5, align='L', w=10.0, txt='N\xba: ', border=0)
                pdf.set_font('arial', 'B', 12.0)
                pdf.set_xy(22.0, 44.5)
                pdf.cell(ln=0, h=5.0, align='L', w=98.0, txt='Cliente:', border=0)
                
                pdf.set_xy(22.0, 46.5)
                pdf.cell(ln=0, h=5.0, align='L', w=98.0, txt='___________________________', border=0)
                
                pdf.set_font('arial', '', 12.0)
                pdf.set_xy(119.0, 33.0)
                pdf.cell(ln=0, h=7.0, align='L', w=60.0, txt='Fecha:', border=0)
                pdf.set_xy(133.0, 33.0)
                pdf.cell(ln=0, h=7.0, align='L', w=40.0, txt=fecha, border=0)
                pdf.set_font('times', '', 10.0)
                pdf.set_xy(17.0, 59.0)
                pdf.code39(transa,152,28)
                with open(file_pathTicket) as file:
                    pdf.set_font('courier', '', 10.0)
                    for i in file:
                        pdf.set_line_width(0.0)
                        pdf.cell(130,10,txt=i,ln =1,align="C")
                
                pdf.output(file_pathTicketPdf)
                logging.info('se exporte el  pdf '+filePdfTicket)  
                logging.info('preparando la fimar de agua '+filePdfTicket)
                PyPDF4.PdfFileReader(file_pathTicketPdf)
                put_watermark( 
                  input_pdf=file_pathTicketPdf,  
                  output_pdf=file_pathTicketPdfFirma,  
                  watermark=fileFirmaDeAgua) 
                if os.path.exists(file_pathTicketPdf):
                   os.remove(file_pathTicketPdf)
                   logging.critical('Elimiando file: '+file_pathTicketPdf)
                else:
                    logging.error('No existe '+file_pathTicketPdf)
        logging.error('El Registro H no tiene un Registro F.. por lo tano no es una venta o NC')
    logging.error('Existe esa transaccion en el IDC')
    logging.error('Pero no representa una Venta o NC: Operacion:'+codetrx)
                        
def unaFactura():
    print(Fore.RED+'Transaccion #:'+Fore.BLUE+factura)
    print(Fore.GREEN+'Com'+Fore.LIGHTCYAN_EX+'ple'+Fore.YELLOW+'tada') 
    logging.info('Transaccion #:'+factura+' Compleatada')
    if mostrar_Pdf=='1':           
       webbrowser.open(r'file:///'+os.path.abspath(file_pathTicketPdfFirma)) 
    if verFileJson=='1':
        # Opening JSON file
        # create a temporary file and write some data to it
        fp = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
        fjson = open(file_pathJson)
        # returns JSON object as 
        # a dictionary
        data = json.load(fjson)
        fjson.close()
        # Iterating through the json
        #print(json.dumps(data, indent=4, sort_keys=False))       
        fp.write(json.dumps(data, indent=4, sort_keys=False))
        logging.critical(json.dumps(data, indent=4, sort_keys=False))       
        logging.info('Se puso el json Bonito tabulado')
        #  
        file_nametmp = fp.name
        #
        shutil.copy(file_pathJson, 'beautyJson.json')
        os.remove(file_pathJson)
        shutil.copy('beautyJson.json', file_pathJson)
        logging.info('copiando beautyJson.json a ' +file_pathJson)
        os.remove(file_nametmp)
        logging.info('borrando temporal'+file_nametmp)
        for i in data['fiscalDoc']:
            logging.critical(i)
           
# Proceso de lectura de File IDC
def cargaInicial():
    try:
        logging.info('Procesando el file:IDC\n y metiendo los registro en Arrgelos diferente')
   
        with open(file_idc, encoding='utf8') as Lectura:
            row =0
            while True:
                line = Lectura.readline()
                # Solo se filtra el registro tipo "H" Ventas
                x = line.find(":H:")
                if x != -1:
                    add_registro(line, listReg_H)
                # Solo se filtra el registro tipo "W" Ventas
                x = line.find(":W:")
                if x != -1:
                        add_registro(line, listReg_W)  
                        # Solo se filtra el registro tipo "S" Ventas
                x = line.find(":S:")
                if x != -1:
                    add_registro(line, listReg_S)
                    # Solo se filtra el registro tipo "V" Ventas
                x = line.find(":V:")
                if x != -1:
                    add_registro(line, listReg_V)
                    # Solo se filtra el registro tipo "T" Ventas
                x = line.find(":T:")
                if x != -1:
                    add_registro(line, listReg_T)  
                    # Solo se filtra el registro tipo "F" Ventas    
                x = line.find(":F:")
                if x != -1:
                    add_registro(line, listReg_F)
                    # Solo se filtra el registro tipo "K" Ventas    
                x = line.find(":K:")
                if x != -1:
                    add_registro(line, listReg_K) 
                    # Solo se filtra el registro tipo "U" Ventas    
                x = line.find(":U:")
                if x != -1:
                    add_registro(line, listReg_U)  
                    # Solo se filtra el registro tipo "U" Ventas    
                x = line.find(":C:")
                if x != -1:
                    add_registro(line, listReg_C)    
                thislist.append(line)   # adiciono en un arreglo la linea
                row +=1 
                if not line:
                    break
        thislist.sort()
        logging.info('Ordenando el Arrego ThisList')
        logging.info('se Procesaron '+str(row)+' del Archviso :'+file_idc)
    except NameError:
        print("Algo sucedio con el file IDC")
        logging.error('Error en lectura de IDC:'+NameError)
    finally:
        print(NameError)
#Fin de lectura
# Modulo Principal de Lectura   
if __name__ == "__main__":
    #factura=input(" Entre No. Factura: ") 
    cargaInicial() 
    logging.info('en Modulo Principal(Main)')
    puntero =''
    listReg_H.sort()
    logging.info('Procesando todo lo Registro H con Facturas y NC: '+factura) 
   
    #Lectura de todos los registros H
    logging.info('Parciando Registro H')
   
    for h in tqdm (listReg_H,desc=Fore.LIGHTGREEN_EX+'Procesando...',ascii=False, ncols=75):
        time.sleep(0.01)
        encabezadoH= h
        tienda  =(h[0:4])
        terminal=(h[5:8])
        fecha   =(h[9:15])
        hora    =(h[17:22])
        transa  =(h[23:27])
        #if TodaLasTransacciones==1:
        #logging.info('DOC A Buscar: '+factura+' en H -->:'+transa+'-> ')
        #logging.info(transa == factura)
        #logging.info(LeerTodoFileSinFactura)
        if LeerTodoFileSinFactura==0:
            if transa == factura:
                logging.info('Se encontro una factura similar al Parametro #:'+transa+" de la Peticionde #"+factura+' Con el File enviado')
                procesarTrx(h)
                logging.debug('Procesando la Factura:'+transa)
                unaFactura()
                enviarAlApi()
            else:
                logging.debug('Es un Registro H sin una F(no es una Venta)'+transa)
                  
        elif LeerTodoFileSinFactura==1:
             logging.info('Se Procesa todo el File enviando Trx #:'+transa)
             procesarTrx(h)
             enviarAlApi()
             #exit(1)
