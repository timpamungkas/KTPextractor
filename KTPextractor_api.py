import os
import uuid
import urllib.request
import ocr_text_extractor as ocr
import ktp_entity_extractor as extractor
from flask import Flask, request, Response, flash, render_template, redirect
from werkzeug.utils import secure_filename

UPLOAD_DIR = 'UPLOADS' + os.path.sep

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/ping', methods=['POST'])
@app.route('/health')
def hello_world():
   return 'OK'

@app.route('/upload_ktp')
@app.route('/')
def upload_form():
    return render_template('upload_ktp.html')

@app.route('/upload_ktp', methods=['POST'])
def upload_ktp_file():
    if 'file' not in request.files:
        flash('No KTP file uploaded')
        return redirect(request.url)
	
    file = request.files['file']
    
    if file.filename == '':
        flash('No KTP file uploaded')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        # temporary file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid1()) + '.' + file.filename.rsplit('.', 1)[1].lower())
        file.save(filename)
        npy_filename = ocr.process_ocr(filename)
        extracted = extractor.process_extract_entities(npy_filename)

        flash(extracted)
        return redirect(request.url)
    else:
        flash('Allowed file types are ' + str(ALLOWED_EXTENSIONS))
        return redirect(request.url)

@app.route('/ktp', methods=['POST'])
def api_ktp():
    if 'file' not in request.files:
        return 'No file uploaded', 400
	
    file = request.files['file']
    
    if file.filename == '':
        return 'No file uploaded', 400
    if file and allowed_file(file.filename):
        # temporary file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid1()) + '.' + file.filename.rsplit('.', 1)[1].lower())
        file.save(filename)
        npy_filename = ocr.process_ocr(filename)
        extracted = extractor.process_extract_entities(npy_filename)
        return Response(response=extracted, status=200, content_type="application/json")
    else:
        return 'Allowed file types are ' + str(ALLOWED_EXTENSIONS), 400

if __name__ == '__main__':
    app.run(port=9090)