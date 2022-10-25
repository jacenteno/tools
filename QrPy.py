from tkinter import Scale
import pyqrcode
url = pyqrcode.create('https://twitter.com/jacenteno')
url.svg('QRjac.svg',scale =6)