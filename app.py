import io
import uuid
from flask import Flask, render_template, request,send_from_directory,flash,jsonify,send_file
from PIL import Image
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta
import main
import fitz
import zipfile
import img2pdf
from pypdf import PdfReader, PdfWriter, Transformation, PaperSize

app = Flask(__name__)
UPLOAD_FOLDER='uploads'
OUTPUT_FOLDER='output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


scheduler = BackgroundScheduler()
scheduler.start()

def delete_old_files():
    # Function to delete files older than 1 hour in both upload and output folders
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if datetime.now() - file_time > timedelta(hours=1):
                os.remove(file_path)
            os.remove(file_path)

# Schedule the task to run every hour
scheduler.add_job(delete_old_files, 'interval', hours=1)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/pdf-editor')
def pdf():
    return render_template('pdf.html')

@app.route('/extract-data')
def extract():
    return render_template('extract.html')

@app.route('/edit-image')
def edit():
    return render_template('edit.html')

@app.route('/convert-format')
def format():
    return render_template('convert.html')

@app.route('/chatbot')
def chat():
    return render_template('chatbot.html')

@app.route('/help')
def help():
    return render_template('help.html')
@app.route('/merge_pdf', methods=['POST'])
def merge_pdf():
    delete_old_files()
    if 'file' not in request.files:
        return flash("No file part")

    pdf_file = request.files.getlist('file')
    file_path=[]
    for i in pdf_file:
        if i.filename == '':
            return flash("No selected file")
        filename = secure_filename(i.filename)
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        i.save(uploaded_file_path)
        file_path.append(uploaded_file_path)
    output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], 'merged_pdf.pdf')
    main.merge_pdfs(file_path, output_file_path)
    return send_from_directory(app.config["OUTPUT_FOLDER"], 'merged_pdf.pdf', as_attachment=True,download_name="ImageIQ_Merged.pdf")

@app.route('/split_pdf', methods=['POST'])
def split():
    delete_old_files()
    if 'file' not in request.files:
        return ("No file part")

    pdf_file = request.files.getlist('file')
    range=request.form.get('startPage')
    for i in pdf_file:
        if i.filename == '' :
            return ("No selected file")
        filename = secure_filename(i.filename)
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        i.save(uploaded_file_path)
        main.split_pdf(uploaded_file_path, output_file_path,range)
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True,download_name="ImageIQ_splitted.pdf")

@app.route('/encrypt_pdf', methods=['POST'])
def encrypt():
    delete_old_files()
    if 'file' not in request.files:
        return flash("No file part")

    pdf_file = request.files.getlist('file')
    psw=request.form.get('password')
    for i in pdf_file:
        if i.filename == '' :
            return flash("No selected file")
        filename = secure_filename(i.filename)
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        i.save(uploaded_file_path)
        main.encrypt_pdf(uploaded_file_path, output_file_path,psw)
        encrypted_pdf=output_file_path
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True,download_name="ImageIQ_encrypted.pdf")
@app.route('/rotate_pdf', methods=['POST'])
def rotate():
    delete_old_files()
    if 'file' not in request.files:
        return flash("No file part")

    pdf_file = request.files.getlist('file')
    angle=request.form.get('angle')
    pg_range=request.form.get('startPage')
    for i in pdf_file:
        if i.filename == '' :
            return flash("No selected file")
        filename = secure_filename(i.filename)
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        i.save(uploaded_file_path)
        main.rotate_pdf(uploaded_file_path, output_file_path,angle,pg_range)
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True,download_name="ImageIQ_rotated.pdf")

@app.route('/compress_pdf', methods=['POST'])
def compress():
    delete_old_files()
    if 'file' not in request.files:
        return flash("No file part")

    pdf_file = request.files.getlist('file')
    compression_level=request.form.get('compression_level')
    angle=request.form.get('angle')
    pg_range=request.form.get('startPage')
    for i in pdf_file:
        if i.filename == '' :
            return flash("No selected file")
        filename = secure_filename(i.filename)
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        i.save(uploaded_file_path)
        main.compress_pdf(uploaded_file_path, output_file_path,compression_level)
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True,download_name="ImageIQ_compressed.pdf")


@app.route('/extract_txt', methods=['POST'])
def extract_txt():
    delete_old_files()
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

    def extract_text(pdf_path):
        doc = fitz.open(pdf_path)
        text = ""

        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()

        doc.close()
        return text
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('extract.html', error='No file part')

        file = request.files['file']

        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template('extract.html', error='No selected file')

        if file and allowed_file(file.filename):
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Extract text from the PDF
            extracted_text = extract_text(file_path)

            # Render the template with the extracted text
            return render_template('extract.html', extracted_text=extracted_text)

    return render_template('extract.html')
@app.route('/extract_img', methods=['POST'])
def extract_imgs():
    def extract_text(pdf_path):
        doc = fitz.open(pdf_path)
        text = ""

        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()

        doc.close()
        return text
    def pdf_imgs():
        a4inpt = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
        layout_fun = img2pdf.get_layout_fun(a4inpt)
        with open(f"{app.config['OUTPUT_FOLDER']}/name.pdf","wb") as f:
            f.write(img2pdf.convert(imgs,layout_fun=layout_fun))


        reader = PdfReader(f"{app.config['OUTPUT_FOLDER']}/name.pdf")

        # Create a destination file, and add a blank page to it
        writer = PdfWriter()

        # # Copy source page to destination page, several times

        for i in range(0,len(reader.pages),x_y_number**2):
            destpage = writer.add_blank_page(width=PaperSize.A4.width, height=PaperSize.A4.height)
            img_no=i
            for x in range(x_y_number):
                for y in range(x_y_number):
                    try:
                        sourcepage = reader.pages[img_no]
                        sourcepage.scale_by(x_y_number/(x_y_number**2))
                        destpage.merge_transformed_page(
                            sourcepage,
                            Transformation().translate(
                                x * sourcepage.mediabox.width,
                                y * sourcepage.mediabox.height,
                            ),
                        )
                        img_no+=1
                    except:
                        continue
        with open("output/All Images.pdf", "wb") as fp:
            writer.write(fp)
        os.remove(f"{app.config['OUTPUT_FOLDER']}/name.pdf")
        return send_from_directory(app.config["OUTPUT_FOLDER"], 'All Images.pdf', as_attachment=True,download_name="ImageIQ_extracted.pdf")

    def create_zip(folder_path, zip_filename):
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, folder_path))

    # Define a function to extract images from a PDF page
    def extract_images_from_page(pdf_path, page_num):
        doc = fitz.open(pdf_path)  # Open the PDF file using fitz
        page = doc.load_page(page_num) # Load the page and get all images on the page
        images = page.get_images(full=True)
        extracted_images = []

        # Loop through each image and extract it
        for img in images:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Save the image bytes to a PIL.Image object
            img = Image.open(io.BytesIO(image_bytes))
            extracted_images.append(img)   
        return extracted_images
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('extract.html', error='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('extract.html', error='No selected file')
        pdf = request.files['file']
        opt=request.form.get('extract_opt')
        x_y_number = int(request.form['images_per_page'])
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)
        pdf.save(pdf_path)
        if opt=='image':
            imgs=[]
            # Extract images from each page of the PDF and save them to the image folder
            with fitz.open(pdf_path) as doc:
                for page_num in range(doc.page_count):
                    images = extract_images_from_page(pdf_path, page_num)
                    for img in images:
                        img_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{uuid.uuid4()}.png")
                        img.save(img_path)
                        imgs.append(img_path)
            pdf_imgs()            
            # Render the display_images.html template and pass the list of image filenames
            folder_path = 'output'  # Specify the path to your folder
            zip_filename = 'ImageIQ_extracted_imgs.zip'
            create_zip(folder_path, zip_filename)
            try:
            # Check if the file exists
                if not os.path.exists(zip_filename):
                    raise FileNotFoundError(f"File '{zip_filename}' not found.")

            # Provide the zip file for download
                return send_file(zip_filename, as_attachment=True, download_name=zip_filename)
        
            except FileNotFoundError as e:
                return str(e)
        else:
            # Extract text from the PDF
            extracted_text = extract_text(pdf_path)
            # Render the template with the extracted text
            return render_template('extract.html', extracted_text=extracted_text)

        # Render the upload_pdf.html template if the request method is GET
    return render_template('extract.html')


@app.route('/edit-upload', methods=['POST'])
def edit_upload():
    delete_old_files()
    if 'file' not in request.files:
        return flash("No file part")

    img_file = request.files.getlist('file')
    for i in img_file:
        if i.filename == '' :
            return flash("No selected file")
        filename = secure_filename(i.filename)
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        i.save(uploaded_file_path)
        return render_template('edit.html')
        
    
@app.route('/convert_image', methods=['POST'])
def convert_image_route():
    if 'input_image' not in request.files:
        return jsonify({'error': 'No file part'})

    input_image = request.files['input_image']
    output_format = request.form['output_format']

    if input_image.filename == '':
        return jsonify({'error': 'No selected file'})

    if input_image:
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_image.filename)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'converted_{input_image.filename}')

        input_image.save(input_path)

        converted_path = main.convert_image(input_path, output_path, output_format)

        # Clean up: remove the uploaded image after conversion
        os.remove(input_path)

        return jsonify({
            'input_path': input_path,
            'output_path': converted_path
        })

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form['text']
    image_path = main.generate_image(text)
    return send_file(image_path, mimetype='image/png')
if __name__ == '__main__':
    app.run(debug=True)
