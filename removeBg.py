from rembg import remove
from PIL import Image
without_bg = remove(Image.open('puppy.png'))
without_bg.save('puppy_out.png')