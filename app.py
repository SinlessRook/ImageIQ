from flask import Flask, render_template, request,send_from_directory,flash,jsonify
from PIL import Image
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta
import main
import uuid
import fitz
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER='uploads'
OUTPUT_FOLDER='images'
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
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True,download_name="ImageIQ_encrypted.pdf")
    
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
    create_zip("../images", 'images.zip')    
    return extracted_images
def create_zip(folder_path, zip_filename):
    # Create a Zip file
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        # Walk through the folder and add each file to the Zip file
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                # Add the file to the Zip file with its relative path
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))

# Define a Flask route for uploading a PDF file
@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'POST': # Get the uploaded PDF file and save it to the upload folder
        pdf = request.files['pdf']
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)
        pdf.save(pdf_path)

         # Extract images from each page of the PDF and save them to the image folder
        with fitz.open(pdf_path) as doc:
            for page_num in range(doc.page_count):
                images = extract_images_from_page(pdf_path, page_num)
                for img in images:
                    img_path = os.path.join(app.config['IMAGE_FOLDER'], f"{uuid.uuid4()}.png")
                    img.save(img_path)

        # Render the display_images.html template and pass the list of image filenames
        return render_template('display_images.html', images=os.listdir(app.config['IMAGE_FOLDER']))
    
    # Render the upload_pdf.html template if the request method is GET
    return render_template('upload_pdf.html')

# Define a Flask route for serving images
@app.route('/images/<path:path>')
def serve_image(path):
    return send_from_directory(app.config['IMAGE_FOLDER'], path)
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()

    doc.close()
    return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('extract_text.html', error='No file part')

        file = request.files['file']

        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template('extract_text.html', error='No selected file')

        if file and allowed_file(file.filename):
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Extract text from the PDF
            extracted_text = extract_text(file_path)

            # Render the template with the extracted text
            return render_template('extract_text.html', extracted_text=extracted_text)

    return render_template('extract_text.html')
if __name__ == '__main__':
    app.run(debug=True)
