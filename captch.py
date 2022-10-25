from turtle import width
from PIL import Image

from captcha.audio import AudioCaptcha
from captcha.image import ImageCaptcha
import string
import random

N = 7

audio = AudioCaptcha()
#res = ''.join(random.choices(string.ascii_uppercase+string.digits,k =N))
res = '4250277'
str1 = str(res)
data = audio.generate(res)
audio.write(res,'Sample_Cap.wav')

audiofile = AudioCaptcha()
image = ImageCaptcha(width = 300, height = 90)
captcha_text = str1
data = image.generate(captcha_text)
image.write(captcha_text,"captcha_1.png")
Image.open('captcha_1.png')

