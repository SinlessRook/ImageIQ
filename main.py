from pypdf import PdfReader, PdfWriter,Transformation
import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas


def merge_pdfs(input_paths, output_path):
    new_file=PdfWriter()
    for i in input_paths:
        old_file=PdfReader(i)
        for pages in old_file.pages:
            new_file.add_page(pages)
        os.remove(i)
    with open(output_path, 'wb') as f:
        new_file.write(f)
def split_pdf(input_path, output_path,range_given):
    if range_given.partition("-")[1]=="":
        range_orginal=range_given.split(',')
        for i in range(len(range_orginal)):
            range_orginal[i]=int(range_orginal[i])-1
    else:
        range_orginal=[]
        for i in range(int(range_given.partition("-")[0])-1,int(range_given.partition("-")[2])):
            range_orginal.append(i)
    file=PdfReader(input_path)
    new_file=PdfWriter()
    for i in range_orginal:
        new_file.add_page(file.pages[i])
    with open(output_path, 'wb') as f:
        new_file.write(f)
    os.remove(input_path)

def encrypt_pdf(input_path, output_path, password):
    file=PdfReader(input_path)
    new_file=PdfWriter()
    for pages in file.pages:
        new_file.add_page(pages)
    new_file.encrypt(password, algorithm="AES-256")
    with open(output_path, 'wb') as f:
        new_file.write(f)
    os.remove(input_path)

def rotate_pdf(input_path, output_path, rotation_angle,pg_range):
    with open(input_path, 'rb') as file:
        pdf_reader = PdfReader(input_path)
        pdf_writer = PdfWriter()
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num].rotate(int(rotation_angle))
            pdf_writer.add_page(page)

        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
    os.remove(input_path)
def compress_pdf(input_path, output_path,compression_value):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    for page in writer.pages:
        for img in page.images:
            img.replace(img.image, quality=int(compression_value))

    for page in writer.pages:
        page.compress_content_streams()  # This is CPU intensive!
    
   

    with open(output_path, "wb") as f:
        writer.write(f)
    os.remove(input_path)
def watermark_pdf(input_path, output_path, watermark_path):
    stamp = PdfReader(watermark_path).pages[0]
    writer = PdfWriter(clone_from=input_path)
    for page in writer.pages:
        page.merge_page(stamp, over=False)  # here set to False for watermarking

    writer.write(output_path)
    
def convert_image(input_path, output_path, output_format):
    image = Image.open(input_path)
    image = image.convert("RGB")
    image.save(output_path, format=output_format)
    return output_path


def generate_image(text):
    img = Image.new('RGB', (400, 200), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 20)
    d.text((10,10), text, fill=(0,0,0), font=font)
    img_path = "static/generated_image.png"
    img.save(img_path)
    return img_path
