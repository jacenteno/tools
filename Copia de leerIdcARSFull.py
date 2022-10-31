# Lectura de IDC de NCR ARS 
# Con Python. 
# Por Jorge Centeno - 3 de Octubre de 2022.
#  Lectura de Registros de  NCR ARS POS
#
from ast import Break, Global, Try
from asyncio import current_task
import mmap
import base64

from syslog import LOG_WARNING
from time import sleep
import datetime
from asyncore import ExitNow, file_wrapper
from concurrent.futures import thread
from encodings.utf_8_sig import decode
import os
import os.path
from pickle import FALSE
import platform
from socketserver import ThreadingUnixStreamServer
from sre_constants import BRANCH

import tempfile, shutil
from os import path
import re
import threading
from urllib.parse import parse_qsl
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
from correr import background_calculation
from pdf417 import encode, render_image
from random import random
import threading
import time
import webbrowser
from PyPDF4 import PdfFileWriter, PdfFileReader 
import PyPDF4
from dotenv import load_dotenv
import qrcode
from fpdf import FPDF
from turtle import pd

global pathLog
global pathData
global detalleRuta

global url_Pac_Proveedor
global fileJsonWebPos
global filePdfTicket
global fileJson
global file_pathTicketPdfFirma

global acumularDescto
global thislist
global listItemsJson
global listReg_c_filtro
global fileFirmaDeAgua

global pathleerIDC
global fileIdcExiste

def listas():
    global new_listS
    global listReg_H
    global listReg_F 
    global listReg_C 
    global listReg_W
    global listReg_S
    global listReg_V
    global listReg_T 
    global listReg_U 
    global listReg_K 
    global thislist
    global new_listS
    global listReg_c_filtro
    global listItemsJson
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
def SistemaOperativo():
    global pathData
    global pathLog
    global pathleerIDC
    global pathleerJson
    global pathJournal
    global ServerId
    global detalleRuta
    global pathJson
    global pathIdcProcesado
    global pathQr
    if queOSystem =='Linux':
        pathData="data//"
        pathLog="logs//"
        pathleerIDC="lectura//"
        pathleerJson="json//"
        pathJournal="journal//"
        ServerId='Linux'
        pathJson="json//"
        pathIdcProcesado="idcprocesado//"
        pathQr="qr//"
    elif queOSystem =='Darwin':  ## esto es mac
        pathData="data//"
        pathLog="logs//"
        pathleerIDC="lectura//"
        pathJson="json//"
        pathJournal="journal//"
        ServerId='MAC Darwin'
        pathIdcProcesado="idcprocesado//"
        pathQr="qr//"
    else:
        pathData="data\\"   #Windows 
        pathLog="logs\\"
        pathleerIDC="lectura\\"
        pathJson="json\\"
        pathJournal="journal\\"
        ServerId='Windows'
        pathIdcProcesado="idcprocesado\\"
        pathQr="qr\\"
    detalleRuta=pathData+'\n'+pathLog+'\n'+pathleerIDC+pathJournal+'\n'+pathleerIDC+'\n'
    
def cargarVariableEntorno():
    global mostrar_Pdf
    global verFileJson
    global companyLicCod
    global apiKey
    global url_Pac_Proveedor
    global fileFirmaDeAgua
    global logoCompania
    global verFileJson
    global acumularDescto
    global branch
    global poscod
    global defaultEmail
    global defaultDireccion
    global LecturaIdc
    load_dotenv()
    # Buscando  Variables de Groment.
    token=os.environ.get("api-Token")
    mostrar_Pdf=os.environ.get("mostrar_Pdf")
    companyLicCod=os.environ.get("companyLicCod")
    apiKey=os.environ.get("apiKey")
    url_Pac_Proveedor=os.environ.get("url_Pac_Proveedor")
    acumularDescto=os.environ.get("acumularDescto")
    fileFirmaDeAgua=os.environ.get("fileFirmaDeAgua")
    logoCompania=os.environ.get("logoCompania")
    verFileJson=os.environ.get("verFileJson")

    branch= os.environ.get("branch")
    poscod= os.environ.get("poscod")
    
    defaultEmail=os.environ.get("defaultEmail")
    defaultDireccion=os.environ.get("defaultDireccion")
    LecturaIdc=os.environ.get("LecturaIdc")
    
 
main_path = os.path.dirname(__file__)
queOSystem= platform.system()
ServerId=''

SistemaOperativo()
listas()
cargarVariableEntorno()

file_log = os.path.join(main_path,pathLog+"leerIdcArs.log")
logging.basicConfig(filename=file_log,level=logging.INFO,format='%(process)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s',filemode='w', datefmt='%m/%d/%Y %I:%M:%S %p', encoding='utf-8')
logging.critical('Iniciamos registro en:'+file_log)
logging.critical(ServerId)
logging.critical('se Carga los path '+detalleRuta)

file_log = os.path.join(main_path,pathLog+"leerIdcArs.log")
logging.basicConfig(filename=file_log,level=logging.INFO,format='%(process)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s',filemode='w', datefmt='%m/%d/%Y %I:%M:%S %p', encoding='utf-8')

logging.warning('Iniciando, Se cargaron los Environ')
# Paramentro 1 es idc y 2= factura.
LeerTodoFileSinFactura=0
title = 'Lector de Idc'
filePluLocal='M_HSHPLU.DAT'

logging.debug('Path del app'+main_path)
logging.debug('Path del dataPLU:'+pathData)
logging.debug('Archivos PLU:'+filePluLocal)
#el plu va en pathdata
file_path = os.path.join(main_path,pathData+filePluLocal)

filePluExiste = os.path.exists(file_path)
global ListPlu
ListArticulos=[]
if filePluExiste:
     with open(file_path,encoding='windows-1254') as f:
        datafile = f.readlines()
        for line in datafile:
            lineaPlu=line
            if lineaPlu[37:38].isalpha():
                ListArticulos.append(lineaPlu)
              
        ListArticulos.sort()
        f.close()   
else:
    logging.error('No se encuentra file PLU: '+file_path)
# Diccionarion de tabulacion de registro S/F
#012345678901234567890123456789012345678901234567890123456789012345678901234567890
#12345678901234567890123456789012345678901234567890123456789012345678901234567890
#0202:001:221005:075320:8201:121:F:100:0090:                :00+00027+000005306
#0202:009:220223:160412:1673:002:S:101:0001:    842135000599+00010010*000000219
#   1   2      3      4    5   6 7 8   9    10               11       12     
punteroTrans=""
fileJsonWebPos=""

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
def escribirTicketTxt(FileTxt,ListTicketTxt):
    
    pass
def check_2(searchplu):
    
    global foundPlu
    global PluMaster
    foundPlu = False
    PluMaster=''
    for line in ListArticulos:
        lecturaPlu=line
        if lecturaPlu.find(searchplu) != -1:
            foundPlu = True
            PluMaster=line
    return foundPlu

def check(searchplu):
    
    global foundPlu
    global PluMaster
    foundPlu = False
    PluMaster=''
    for line in datafile:
        lecturaPlu=line
        if lecturaPlu.find(searchplu) != -1:
        #if searchplu in line:
            foundPlu = True
            PluMaster=line
            break
    return foundPlu

                     
def procesarTrx(h):
    global file_pathJson          
    global file_pathTicket        
    global file_pathTicketPdf     
    global file_pathTicketPdfFirma
    global ListTicketTxt
    #file_pathJson="Hola"
    ListTicketTxt= []            
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
    logging.info('Code1 '+(h[34:35]))
    logging.info('Code2 '+(h[35:36]))
    logging.info('Code3 '+(h[36:37]))             
    logging.info('Puntero'+puntero)
    #logging.info(listReg_F)
    
    hayf   =buscar(puntero,listReg_F,"F")
    #logging.info('Hay '+str(hayf)+" Registro F")
       
    codetrx=code1+code2+code3
    # Escribe en json el tienda:
    #print(encabezadoH)
    listItemsJson.clear
    if codetrx == "100" or codetrx == "150" or codetrx == "160" or  codetrx == "180" :
        logging.info('Procesando solo Transacciones de Ventas:'+codetrx)
        logging.info('Hay '+str(hayf)+" Registro F")
       
        if ( hayf >=0):
                logging.info('registro F y H = Facturas')
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
                
                file_pathJson          =os.path.join(main_path,pathJson+fileJson)
                file_pathTicket        =os.path.join(main_path,pathJournal+filePosTicket)
                file_pathTicketPdf     =os.path.join(main_path,pathJournal+filePdfTicket)
                file_pathTicketPdfFirma=os.path.join(main_path,pathJournal+filePdfTicketFirma)
             
                if os.path.exists(file_pathJson):
                    os.remove(file_pathJson)
                else:
                    pass
                if os.path.exists(file_pathTicket):
                    os.remove(file_pathTicket)
                else:
                    pass
                path = r'tools'

                fileJsonWebPos = open(file_pathJson, "w")
                fileTickNcrArs = open(file_pathTicket, "w")
                
                fileJsonWebPos.write("{ ")
                fileJsonWebPos.write('"fiscalDoc": { \n')
                
                fileJsonWebPos.write('"companyLicCod":"'+companyLicCod+'", \n')
                fileJsonWebPos.write('"apiKey":"'+apiKey+'", \n')
                #fileJsonWebPos.write('"branchCod": "'+tienda+'",\n')
                #fileJsonWebPos.write('"posCod": "'+terminal+'",\n')
                fileJsonWebPos.write('"branchCod": "'+branch+'",\n')
                fileJsonWebPos.write('"posCod": "'+poscod+'",\n')
                
                if code1 =="1" and code2=="0":
                        #fileJsonWebPos.write('"docType":"F",\n')
                        fileJsonWebPos.write('"docType":"F",\n')
                        logging.info('doc Type =F Facturas')
                else:
                    if code1 =="1" and (code2=="6" or code2=="8"):
                        #fileJsonWebPos.write('"docType":"C",\n')
                        fileJsonWebPos.write('"docType":"C",\n')
                        logging.info('Doc Type =C Nocta de Credito')
                fileJsonWebPos.write('"docNumber": "'+transa+'",\n')
                fileJsonWebPos.write('"customerName":"Cliente Genérico",\n')
                fileJsonWebPos.write('"customerRUC":"",\n')
                ##07 es consumidor final, hay que ver los otros caso.
                fileJsonWebPos.write('"customerType": "07",\n')
                fileJsonWebPos.write('"customerAddress":"'+defaultDireccion+'",\n')
                fileJsonWebPos.write('"email":"'+defaultEmail+'",\n')
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
                encabezado1="Tienda:"+tienda+" Term:"+terminal+" Fecha:"+fecha+" Hora:"+hora+" Op"+cajero+'\n'
                encabezado2="Fact:"+transa+" Sec:"+secuenc+"AC:"+code1+code2+code3+" Trx:"+opera+'\n'
                encabezado3="------------------------------------------------\n"
                ListTicketTxt.append(encabezado1)
                fileTickNcrArs.write(encabezado1)
                
                fileTickNcrArs.write(encabezado2)
                ListTicketTxt.append(encabezado2)
                
                fileTickNcrArs.write(encabezado3)
                ListTicketTxt.append(encabezado3)
                
                fileTickNcrArs.write("ARTICULOS :"+str((countItem))+'\n')
                ListTicketTxt.append("ARTICULOS :"+str((countItem))+'\n')
                fileTickNcrArs.write("T O T A L :"+str(float(total)/100)+'\n')
                ListTicketTxt.append("T O T A L :"+str(float(total)/100)+'\n')
                
                puntero= tienda+terminal+fecha+transa+"S"
                puntero_c= tienda+terminal+fecha+transa+"C"
                detalle(puntero,listReg_S,"S")
                puntero_v= tienda+terminal+fecha+transa+"V"
                puntero_t= tienda+terminal+fecha+transa+"T"
                puntero_u= tienda+terminal+fecha+transa+"U"
                # presento solo pos S de esa transaccion
                largoListRegS=  len(new_listS)
                taxcode="G"
                for idx, hh in enumerate(new_listS):
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
                    ListTicketTxt.append(""+str(idx+1)+" "+plu+" "+str(qtyI)+" "+str(int(amount)/100)+'\n')
               
                    #check(plu)
                    busqueda=check_2(pluJson)
                    #logging.info('--buscando plu:'+'*'+pluJson+'*')
                    descripcion='DEPTO'
                    tax='0' 
                    if busqueda:
                        tax =PluMaster[24:25]
                        if tax=="0":
                            taxcode="E"
                        elif tax =="1" or tax =="2" or tax =="3" :
                             taxcode="G"
                        descripcion=PluMaster[36:57]
                        #print(PluMaster[36:57])
                        fileTickNcrArs.write('['+taxcode+']'+'    '+descripcion+'\n')
                        ListTicketTxt.append('['+taxcode+']'+'    '+descripcion+'\n')
               
                    else:
                        fileTickNcrArs.write('DPT-\n')
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
                fileTickNcrArs.write("================================================="+'\n')
                
                if anyPromototal==0:
                     fileJsonWebPos.write('   "perc":"0%","amt":0\n')
                     #si el parametros de detalla descuento en Json
                elif acumularDescto =="1" and totaldescto>0:
                     fileJsonWebPos.write('   "perc":"0%","amt":'+str(round(totaldescto, 2))+'\n')
                fileJsonWebPos.write('},\n'  )    
                #registros V 
                fileJsonWebPos.write('"payments":[\n'  )
                fileTickNcrArs.write("------Impuestos------- "+'\n')
               
                for v in listReg_V:  
                       
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
                fileTickNcrArs.write("===================================="+'\n')
                fileTickNcrArs.write("T O T A L: "+str(float(total)/100)+'\n')
                ContadorPagos =0
                listPagos = []
                descripPago="Otros"
                for t in listReg_T:  
                       
                        tienda_t  =(t[0:4])
                        terminal_t=(t[5:8])
                        fecha_t   =(t[9:15])
                        hora_t    =(t[17:22])
                        transa_t  =(t[23:27]) 
                        puntero_filtrot= tienda_t+terminal_t+fecha_t+transa_t+"T"
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
                            elif idpago=="02":
                                descripPago="TARJ.CREDITO"
                                
                            if idpagosigno =="+":
                                    fileTickNcrArs.write("--- PAGO   "+idpago+" "+idpagoCounter+" Monto "+idpagoAmount+'\n')
                                    ContadorPagos +=1
                                    listPagos.append('{"id":'+str(ContadorPagos)+',"type":"'+idpago+'","amt":'+idpagoAmount+',"desc1":"'+descripPago+'"},\n ')
                            elif idpagosigno =="-":
                                 idpagoAmount = idpagoAmount  
                                 fileTickNcrArs.write("--- CAMBIO "+idpago+' '+idpagoCounter+" Monto "+idpagoAmount+'\n')
                # Quita a ultima comas de pagos si hay
                #for t in listPagos:
                #    print(t)
                totalLineaPagos =len(listPagos) 
                #print(totalLineaPagos)
                for fila1,pagos in enumerate(listPagos):
                    # fileJsonWebPos.write(pagos)
                     if fila1 == totalLineaPagos-1:       
                        pInicio=(pagos.find("{"))
                        pFin  =(pagos.find("}"))
                        fileJsonWebPos.write(pagos[pInicio:pFin+1])
                  
                
                fileJsonWebPos.write('],\n')
                fileJsonWebPos.write('"trailer": [\n')
                contadorTrailer=0
                listTrailer=[]
                for u in listReg_U:  
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
                           
                totalLineaTrailer =len(listTrailer)
                
                print(totalLineaTrailer)
                if totalLineaTrailer >0: 
                    #print (listTrailer)
                    for fila,tt in enumerate(listTrailer):
                        if fila == totalLineaTrailer-1:       
                            pInicio=(tt.find("{"))
                            pFin  =(tt.find("}"))
                            fileJsonWebPos.write(tt[pInicio:pFin+1])
                        else:
                            fileJsonWebPos.write(tt)
                        
                else:
                    fileJsonWebPos.write('{"id":'+"1"+',"value":"'+"Gracias por su Compra"+'"}\n')
                                 
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
                PyPDF4.PdfFileReader(file_pathTicketPdf)
                put_watermark( 
                  input_pdf=file_pathTicketPdf,  
                  output_pdf=file_pathTicketPdfFirma,  
                  watermark=fileFirmaDeAgua) 
                if os.path.exists(file_pathTicketPdf):
                   os.remove(file_pathTicketPdf)
                else:
                    pass
                print(Fore.LIGHTRED_EX+'Ti'+Fore.LIGHTCYAN_EX+'ck'+Fore.YELLOW+'et:'+Fore.LIGHTWHITE_EX+transa) 
                logging.info('Tran #:'+transa+' procesada')
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
                    bonito= json.dumps(data)      
                    fp.write(json.dumps(data))
                    #  
                    logging.critical("\n"+bonito)
                    file_nametmp = fp.name
                    #
                    shutil.copy(file_pathJson, 'beautyJson.json')
                    os.remove(file_pathJson)
                    #shutil.copy('beautyJson.json', file_pathJson)
                    shutil.copy('beautyJson.json', file_pathJson)
                   
                    os.remove(file_nametmp)
                    
                    #for i in data['fiscalDoc']:
                        #pass
                    #  logging.critical(i)
                    # Fin de enviojason
                # enviar al Api.
                fileDiccionario= file_pathJson
                logging.critical('Diccionario de ARS '+ fileDiccionario)
                #url_Pac_Proveedor provee los de Webpos por ahora
                rutaWebPos=url_Pac_Proveedor #+fileDiccionario
                logging.critical('Llamado al API \n'+rutaWebPos)
                x = requests.post(rutaWebPos)
                try:
                        with open(fileDiccionario, "rb") as a_file:
                            file_dict = {fileDiccionario: a_file}
                            headers = {'Authorization' : 'id', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
                            json_data = json.load(a_file)
                            response = requests.post(rutaWebPos, data=json.dumps(json_data), headers=headers)
                        if response:
                                logging.warning('n\'+Conexion al API = OK')
                                logging.warning(response.status_code)
                                respuesta =response.json()
                                json_formatted_str = json.dumps(respuesta)
                                logging.warning('\n'+json_formatted_str)
                                dgiResp=respuesta.get('dgiResp')
                                qrContent=respuesta.get('qrContent')
                                qrB64=respuesta.get('qrB64')
                                systemRef=respuesta.get('systemRef')
                                secNumber=respuesta.get('secNumber')
                                feNumber=respuesta.get('feNumber')
                                cufe=respuesta.get('cufe')
                                authNumber=respuesta.get('authNumber')
                                authDate=respuesta.get('authDate')
                                docDate=respuesta.get('docDate')
                                dateSentToDgi=respuesta.get('dateSentToDgi')
                                confirmationNbr=respuesta.get('confirmationNbr')
                                authNumber=respuesta.get('authNumber')
                                QrFactCufe=str(cufe)+'.png'
                                qRFile=os.path.join(main_path,pathQr+QrFactCufe)
                                image_64_decode = base64.b64decode(qrB64) 
                                image_result = open(qRFile, 'wb') # create a writable image and write the decoding result
                                image_result.write(image_64_decode)
                                creaPdfDgi(qRFile,cufe,systemRef,authNumber,secNumber,
                                           feNumber,authDate,
                                           confirmationNbr,docDate,dateSentToDgi)
                        else:
                                logging.error('Falla de Respuesta del API ')
                                logging.error(response.status_code)
                                logging.info(response.text)
                                logging.critical(x.text)
                                #messagebox.showwarning("Respuesta",response.text)
                except ValueError:
                           logging.error("Problemas con el Api")
def creaPdfDgi(qRFile,cufe,systemRef,authNumber,secNumber,feNumber,authDate,confirmationNbr,
               docDate,dateSentToDgi):
     #Genera un Pdf de ticket procesado.
    pdf = FPDF()
    pdf.set_title("DGI")
    pdf.add_page()
    pdf.alias_nb_pages()
    pdf.set_font('helvetica', '', 11.0)
    pdf.image(qRFile, 120.0, 19.0, link='', type='', w=90.0, h=90.0)
    
    pdf.set_xy(65.0, 6.0)
    pdf.set_font('arial', 'B', 11.0)
    pdf.cell(ln=0, h=22.0, align='C', w=75.0, txt='CUFE:'+cufe, border=0)
    
    pdf.set_font('arial', '', 10.0)
    pdf.set_xy(20.0, 11)
    pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Protocolo de Autorizacion:'+authNumber, border=0)
   
    pdf.set_xy(20.0, 15.0)
    pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Ref:'+systemRef, border=0)
    
    pdf.set_xy(20.0, 55.0)
    pdf.code39(transa,30,29)
    
    
    pdf.set_xy(20.0, 30)
    pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Secuencia:'+secNumber, border=0)
   
    pdf.set_xy(20.0, 35)
    pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='feNumber:'+feNumber, border=0)
   
    pdf.set_xy(20.0, 40)
    pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Fecha Autorizacion:'+authDate, border=0)
   
    pdf.set_xy(20.0, 45)
    pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='#Confirmacion:'+confirmationNbr, border=0)
   
    pdf.set_xy(20.0, 50)
    pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Fecha de Documento:'+docDate, border=0)
    
    pdf.set_xy(20.0, 55)
    pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Fecha Enviado a DGI:'+dateSentToDgi, border=0)
   
    pdf.set_xy(20.0, 85)
    with open(file_pathTicket) as file:
        pdf.set_font('courier', '', 10.0)
        for i in file:
            pdf.set_line_width(0.0)
            pdf.cell(100,10,txt=i,ln =0.5,align="C")
                
                
    pdf.output('demo.pdf')
    PyPDF4.PdfFileReader('demo.pdf')
                
                            
def unaFactura():
    logging.info('Transaccion #:'+' Compleatada')
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
def is_s3_path(path):
    return path.startswith("s3:/")
line =''
def addRegistroIDC(line):
    # Solo se filtra el registro tipo "H" Ventas
    #print(line)
    valor =0
    if line.find(":H:") != -1:
        listReg_H.append(line)
        valor =1
    elif line.find(":W:")!= -1:
        listReg_W.append(line)
        valor =2
    elif line.find(":S:") != -1:     
        listReg_S.append(line)
        valor =3
    elif line.find(":V:") !=-1:
        listReg_V.append(line)
        valor =4
    elif line.find(":T:") !=-1:
        listReg_T.append(line)
        valor =5 
    elif line.find(":F:") !=-1:
        listReg_F.append(line)
        valor =6
    elif  line.find(":K:") !=-1:
        listReg_K.append(line)
        valor =7
    elif  line.find(":U:") !=-1:
            listReg_U.append(line)
            valor =8
    elif  line.find(":C:") !=-1:
           listReg_C.append(line)
           valor =9   
    thislist.append(line) 
   
# Proceso de lectura de File IDC

def cargaInicial():
    global line
    global fileIdcAprocesar
    global fileprocess
    global  file_idc
    global  fileIdcExiste
    global  numeroRow
    #Limpia los lista []
    fileIdcAprocesar =LecturaIdc #"S_IDC001.DAT" 
    fileprocess =fileIdcAprocesar         #"S_IDC001.DAT" 
    logging.error('O'+fileIdcAprocesar)
    
    numeroRow =0
    try:
        file_idc = os.path.join(main_path,pathleerIDC+fileprocess )
        fileIdcExiste = os.path.exists(file_idc)
        logging.error('Ok existe el file IDC:'+file_idc)
        if fileIdcExiste: 
             with open(file_idc, encoding='utf8') as Lectura:
                numeroRow =0
                while True:
                    line = Lectura.readline()
                    addRegistroIDC(line)
                    numeroRow +=1 
                    if not line:
                       break
                thislist.sort()
                logging.error('Valor de numeroRow:'+str(numeroRow))
                logging.debug('file extraido para procesar:'+file_idc)
     
    except ValueError:
        #print()
        logging.error("Oops! no ha llegado el file"+fileprocess)
    logging.error("fin de lectura de File Recibido")
  
def waitForFile(rueda):
        caracter=""
        if rueda==1:
            caracter=" | "
        elif rueda ==2:
            caracter=" / "
        elif rueda ==3:
            caracter=" \ "    
        elif rueda ==4:
            caracter=" - "   
        elif rueda ==5:
            caracter=" | "
        elif rueda ==6:
            caracter=" / "   
        elif rueda ==7:
            caracter=" - " 
        print (Fore.LIGHTRED_EX+"%s" % time.ctime()+Fore.LIGHTYELLOW_EX+caracter)
def main():
    global cuentaCuentos 
    rueda=0
    while True:
        try:
            rueda += 1
            t1 =threading.Thread(target=background_ProcesarIDC)
            t1.start()
            t1.join()
            t2 =threading.Thread(target=waitForFile(rueda))
            t2.start()
            t2.join()
            if rueda >7:
               rueda =1
            
     
        except ValueError:
              print("Error en proceso")
def moveridcprocesado():
    #file_idc = os.path.join(main_path,pathleerIDC+fileprocess )
    if fileIdcExiste:
        fileIdcLeido  = fileIdcAprocesar+'_'+datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S') 
        logging.info('moviendo '+ file_idc +' a '+fileIdcLeido)
        shutil.copy(file_idc,pathIdcProcesado+fileIdcLeido)
        os.remove(file_idc)
        logging.info('borrando '+ file_idc )
                    
def background_ProcesarIDC():
    global encabezadoH   
    global tienda  
    global terminal
    global fecha
    global hora  
    global transa  
    listas()
    cargaInicial() 
    logging.info('# de Registros del File Recibido: '+str(numeroRow))
    if numeroRow >0:
        puntero =''
        transa=''
        listReg_H.sort()
        totalH=len(listReg_H)
        #logging.info(listReg_H)
        logging.info(totalH)
        if (len(listReg_H)>0):
            for h in tqdm (listReg_H,desc=Fore.LIGHTYELLOW_EX+"Read "+Fore.WHITE+str(totalH)+Fore.LIGHTGREEN_EX+transa,ascii=False, ncols=100):
                time.sleep(0.01)
                encabezadoH= h
                tienda  =(h[0:4])
                terminal=(h[5:8])
                fecha   =(h[9:15])
                hora    =(h[17:22])
                transa  =(h[23:27])
                procesarTrx(h)
            moveridcprocesado()
    #
       
    #Fin de lectura
# Modulo Principal de Lectura   
if __name__ == "__main__":
    
        main()
        