from pypdf import PdfReader, PdfWriter
import os


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
    