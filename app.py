from flask import Flask, render_template, request,send_from_directory,flash,jsonify
from PIL import Image
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta
import main

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



if __name__ == '__main__':
    app.run(debug=True)
