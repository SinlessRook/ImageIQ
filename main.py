from PIL import Image
import os
img=Image.open(r"C:\Users\Admin\Downloads\ImageIQ2\ImageIQ\static\assets\pdf.jpg")
img.convert("RGB").save(r"C:\Users\Admin\Downloads\ImageIQ2\ImageIQ\static\assets\pdf.png")
os.remove(r"C:\Users\Admin\Downloads\ImageIQ2\ImageIQ\static\assets\pdf.jpg")