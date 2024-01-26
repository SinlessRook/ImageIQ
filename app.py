from flask import Flask, render_template, request, send_file
from PIL import Image
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
import os
import pypdf

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         return "No file part"
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return "No selected file"
    
#     if file:
#         # Perform necessary operations on the image (resizing in this case)
#         img = Image.open(file)
#         img = img.rotate(90)  # Resize the image to 300x300 pixels
        
#         # Save the modified image to a BytesIO object
#         output_buffer = BytesIO()
#         img.save(output_buffer, format='PNG')
#         output_buffer.seek(0)
        
#         # Convert the BytesIO object to a base64-encoded string
#         output_data = output_buffer.getvalue()
#         output_base64 = base64.b64encode(output_data).decode('utf-8')
        
#         # Return the modified image data as a base64-encoded string
#         return render_template('index.html', img_data=output_base64)

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

@app.route("/upload", methods=['POST', 'GET'])
def edit_pdf():
    if 'file' not in request.files:
        return "no file part"

    file = request.files['file']

    if file.filename == '':
        return "no selected file"

    if file:
        file=request.files['file']
        try:
            return render_template('view_pdf.html',file_data=file)
        except Exception as e:
            return str(e)
        
    


if __name__ == '__main__':
    app.run(debug=True)
