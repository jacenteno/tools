# PDF a  Audio.
# By, JCenteno 2022.

import pyttsx3
import pdfplumber as pp 

engine = pyttsx3.init()
#"""VOICE"""
#voices = engine.getProperty('voices')       #getting details of current voice
#engine.setProperty('voice', voices[1].id)
all_data=''
with pp.open('python-para-todos.pdf') as book:
    for page_no, page in enumerate(book.pages,start=1):
        data = page.extract_text()
        if page_no >= 7 and page_no<=9:
           all_data += data
        if page_no == 10:
            break
engine.save_to_file(all_data,'audio_pdf.mp3')  
engine.runAndWait()
engine.stop()
  