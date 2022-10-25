## test de prueba de Lectura de IDC de NCR ARS 
# Con Python. 
## Por Jorge Centeno - 3 de Octubre de 2022.
#  Lectura de Registros de  NCR ARS POS

from ast import Break
from asyncore import file_wrapper
from encodings.utf_8_sig import decode
import os
import os.path
from os import path
import re
from colorama import Fore

from turtle import pd
import qrcode

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
#
import tkinter
from tkinter import messagebox

import textwrap
from fpdf import FPDF
from pdf417 import encode, render_image

import webbrowser
from PyPDF4 import PdfFileWriter, PdfFileReader 
import PyPDF4

from dotenv import load_dotenv
load_dotenv()
# Buscando  Variables de Enviaroment.
token=os.environ.get("api-Token")
mostrar_Pdf=os.environ.get("mostrar_Pdf")
companyLicCod=os.environ.get("companyLicCod")
apiKey=os.environ.get("apiKey")
url_Pac_Proveedor=os.environ.get("url_Pac_Proveedor")
acumularDescto=os.environ.get("acumularDescto")

logging.basicConfig(filename="leerIdcArs.log",level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.warning('Iniciando, Se cargaron los .env')
# Paramentro 1 es idc y 2= factura.
TodaLasTransacciones=0
if len(sys.argv)==3:#
    # hay IDC y Factura
    fileIdcAprocesar=(sys.argv[1]) #archviso idc
    factura =(sys.argv[2])
    TodaLasTransacciones=0
    logging.info('Se enviaron 3 Paramentros:File y Transaccion')
    
elif len(sys.argv)==2:
      # solo idc
      TodaLasTransacciones=1 
      fileIdcAprocesar=(sys.argv[1])
      factura ="ALL"
      logging.info('Se enviaron 2 Paramentros:Solo File')
      
else:
      print('Falta definir 2 pararmetros(IDC Y FACTURA): ejemplo: leeridcARS S_IDC001.DAT 8290')
      logging.error('Falta definir 2 pararmetros(IDC Y FACTURA): leeridcARS S_IDC001.DAT 8290')
      exit()
#print(companylicCod)
class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 12)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Helvetica', '', 10)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, 'Chapter %d : %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, name):
        # Read text file
        with open(name, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()
        # Mention in italics
        self.set_font('', 'I')
        self.cell(0, 5, '(end of excerpt)')

    def print_chapter(self, num, title, name):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(name)
#'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
  

fileprocess =fileIdcAprocesar  #"S_IDC001.DAT" 
fileIdcExiste = os.path.exists(fileprocess)
if not fileIdcExiste:
    logging.error('No se encuentra el Archivos IDC:'+fileprocess)
    logging.error('Adios'+fileprocess)
    exit()
logging.debug('procesando el file'+fileprocess)
filePluLocal='M_HSHPLU.DAT'
filePluExiste = os.path.exists(filePluLocal)
if filePluLocal:
     with open(filePluLocal,encoding='windows-1254') as f:
        datafile = f.readlines()
        logging.info('lectura de '+filePluLocal)
else:
    logging.error('No se encuentra file PLU: '+filePluLocal)
    logging.error('Adios'+filePluLocal)
    Break  
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
def procesarTrx(h):
    global fileJsonWebPos
    global filePdfTicket
    global fileJson
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
            logging.info('Solo codigo '+codetrx)
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
                filePdfTicketFirma="POS-"+terminal+patronFile+tipoFilePdfFinal
                logging.info('Borrando file pdf,json y txt')
                if os.path.exists(fileJson):
                    os.remove(fileJson)
                    logging.info('se borro file:'+fileJson)
                else:
                    logging.error('No se Encontro file:'+fileJson)
                if os.path.exists(filePosTicket):
                    
                    os.remove(filePosTicket)
                    logging.info('se borro file :'+filePosTicket)
                else:
                    logging.error('No se Encontro file:'+filePosTicket)
                #try:
                #    file = open(filePath, 'w')
                #except IOError:
                #    msg = ("Unable to create file on disk.")
                #    file.close()
                #        return
                #finally:
                #        file.write("Hello World!")
                #        file.close()
                path = r'tools'

                fileJsonWebPos = open(fileJson, "w")
                logging.info('se abre el file json:'+fileJson)
                fileTickNcrArs = open(filePosTicket, "w")
                logging.info('se abre el file txt: '+filePosTicket)
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
                logging.info('se escribe en file txt: '+filePosTicket)
                
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
                                 fileJsonWebPos.write('   "perc":"0%","amt":{descto:.2f}'+'\n')
                             fileTickNcrArs.write("T.Desc:"+dp_detalle+signo+descto+'\n')
                             anyPromototal=1
                             logging.info('Procesando Promos '+"T.Desc:"+dp_detalle+signo+descto)
                fileTickNcrArs.write("================================================="+'\n')
                
                if anyPromototal==0:
                     fileJsonWebPos.write('   "perc":"0%","amt":0\n')
                     #si el parametros de detalla descuento en Json
                elif acumularDescto =="1" and totaldescto>0:
                     fileJsonWebPos.write('   "perc":"0%","amt":{totaldescto:.2f}'+'\n')
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
                                    fileJsonWebPos.write('{"id":'+str(contador)+',"type":'+idpago+',"amt":'+idpagoAmount+',"desc1":"'+descripPago+'"}\n'  )
                            else:
                                if idpagosigno =="-":
                                    idpagoAmount = idpagoAmount  
                                    fileTickNcrArs.write("--- CAMBIO "+idpago+' '+idpagoCounter+" Monto "+idpagoAmount+'\n')
                logging.info('Procesando forma de pagos')
               
                fileJsonWebPos.write('],\n')
                fileJsonWebPos.write('"trailer": [\n')
                contadorTrailer=0
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
                            fileJsonWebPos.write('{"id":'+str(contadorTrailer)+',"value":"'+idDetalle+' '+idU+'"},\n')
                            
                            #{ "id":1,"value":"Información al final" },
	                        #{ "id":2,"value":"Información al final" 
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
                #pdf  = PDF()
                #pdf.set_title(title)
                logging.info('Creando File PDF ')
                pdf.add_page()
                pdf.set_font('helvetica', '', 11.0)
                pdf.set_xy(105.0, 8.0)
                pdf.cell(ln=0, h=22.0, align='C', w=75.0, txt=tienda, border=0)
                pdf.image('logo2.png', 20.0, 17.0, link='', type='', w=50.0, h=20.0)
                pdf.set_font('arial', 'B', 16.0)
                pdf.set_xy(95.0, 18.0)
                pdf.set_font('arial', '', 8.0)
                pdf.set_xy(105.0, 21.0)
                pdf.cell(ln=0, h=4.0, align='C', w=75.0, txt='Tienda', border=0)
                pdf.set_font('arial', 'B', 7.0)
                pdf.set_xy(125.0, 21.5)
                pdf.cell(ln=0, h=4.5, align='C', w=10.0, txt='Copia', border=0)
                pdf.set_font('arial', 'B', 14.0)
                pdf.set_xy(125.0, 25.5)
                pdf.cell(ln=0, h=9.5, align='L', w=60.0, txt=transa, border=0)
                pdf.set_xy(115.0, 27.5)
                pdf.cell(ln=0, h=5.5, align='L', w=10.0, txt='N\xba: ', border=0)
                pdf.set_font('arial', 'B', 12.0)
                pdf.set_xy(25.0, 36.5)
                pdf.cell(ln=0, h=5.0, align='L', w=98.0, txt='Cliente', border=0)
                pdf.set_font('arial', '', 12.0)
                pdf.set_xy(115.0, 33.0)
                pdf.cell(ln=0, h=7.0, align='L', w=60.0, txt='Fecha:', border=0)
                pdf.set_xy(135.0, 33.0)
                pdf.cell(ln=0, h=7.0, align='L', w=40.0, txt=fecha, border=0)
                pdf.set_font('times', '', 10.0)
                pdf.set_xy(17.0, 59.0)
                with open(filePosTicket) as file:
                    pdf.set_font('courier', '', 10.0)
                    for i in file:
                        pdf.set_line_width(0.0)
                        pdf.cell(130,10,txt=i,ln =1,align="C")
                    #img = render_image(encode(encabezado1))
                    #pdf.image(img, x=10, y=50)
                #pdf.interleaved2of5(transa, x=50, y=80, w=4, h=20)
                pdf.output(filePdfTicket)
                logging.info('se exporte el  pdf '+filePdfTicket)  
                logging.info('preparando la fimar de agua '+filePdfTicket)
                PyPDF4.PdfFileReader(filePdfTicket)
                put_watermark( 
                  input_pdf=filePdfTicket,  
                  output_pdf=filePdfTicketFirma,  
                  watermark='WaterFirma.pdf') 
                if os.path.exists(filePdfTicket):
                   os.remove(filePdfTicket)
                   logging.critical('Elimiando file: '+filePdfTicket)
                else:
                    logging.error('No existe '+filePdfTicket)
              
    
                       
def unaFactura():
    print(Fore.RED+'Transaccion #:'+Fore.BLUE+factura)
    print(Fore.GREEN+'Com'+Fore.LIGHTCYAN_EX+'ple'+Fore.YELLOW+'tada') 
    logging.info('Transaccion #:'+factura+' Compleatada')
    if mostrar_Pdf=='1':           
       webbrowser.open(r'file:///'+os.path.abspath(filePdfTicket)) 
    
#def envioJason():
    
    # hacer el request WebPos.
    #fileDiccionario="FE-14c-020200122100593224-8259-ConsumidorFinal.json"
    

# Proceso de lectura de File IDC
with open(fileprocess, encoding='utf8') as f:
    row =0
    while True:
        line = f.readline()
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
logging.info('se Procesaron '+str(row)+' del Archviso '+fileprocess)
#Fin de lectura
# Modulo Principal de Lectura   
if __name__ == "__main__":
    #factura=input(" Entre No. Factura: ")  
    logging.info('en Modulo Principal')
     
    logging.info('Se captura por paramentro procesar a:'+factura) 
    puntero =''
    listReg_H.sort()
    #Lectura de todos los registros H
    for h in tqdm (listReg_H,desc=Fore.LIGHTGREEN_EX+'Procesando...',ascii=False, ncols=75):
        time.sleep(0.01)
        encabezadoH= h
        tienda  =(h[0:4])
        terminal=(h[5:8])
        fecha   =(h[9:15])
        hora    =(h[17:22])
        transa  =(h[23:27])
        #if TodaLasTransacciones==1:
        if transa == factura and TodaLasTransacciones==0:
            print(transa, factura)
            logging.info('Se procesa la trx#:'+transa+" de la Peticionde #"+factura+' Con el File enviado')
            procesarTrx(h)
            logging.debug('en modulo UnaFactura:')
            unaFactura()
            fileDiccionario= fileJson
            logging.info('Procesando file Diccionario'+ fileDiccionario)
           
            #url_Pac_Proveedor provee los de Webpos por ahora
            rutaWebPos=url_Pac_Proveedor+fileDiccionario
            logging.critical('haciendo el llamado al api\n'+rutaWebPos)
            x = requests.post(rutaWebPos)
            with open(fileDiccionario, "rb") as a_file:
                file_dict = {fileDiccionario: a_file}
                response = requests.post(rutaWebPos, files=file_dict)
                if response:
                    logging.warning('Respuesta OK del API')
                    logging.info(response.status_code)
                else:
                    logging.error('Falla de Respuesta del API')
                    logging.error(response.status_code)
                    logging.info(response.text)
                    logging.critical(x.text)
                messagebox.showwarning("Respuesta",response.text)
   
        elif TodaLasTransacciones==1:
            logging.info('Se Procesa Trx #:'+transa)
            procesarTrx(h)
            #envioJason()
            #exit(1)
                    