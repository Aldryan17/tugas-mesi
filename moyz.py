from flask import Flask, render_template_string, request, send_file, abort
from werkzeug.utils import secure_filename
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# Fungsi untuk memeriksa apakah file memiliki ekstensi yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Homepage HTML
homepage_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pixel Compress</title>
    <style>
        body { font-family: 'Courier New', Courier, monospace; background-color: #1e1e2f; color: #fff; margin: 0; text-align: center; padding: 50px; }
        .container { background: #3a3a5a; padding: 30px; border-radius: 8px; width: 300px; display: inline-block; }
        h1 { color: #66a3ff; font-size: 32px; }
        .btn { background-color: #0056b3; color: #fff; padding: 10px 20px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; margin: 10px 0; }
        .btn:hover { background-color: #66a3ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Pixel Compress</h1>
        <a href="/compress" class="btn">Start Compressing</a>
        <a href="/report" class="btn">View Report</a>
    </div>
</body>
</html>
'''

# Compress Page HTML
compress_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compress Image</title>
    <style>
        body { font-family: 'Courier New', Courier, monospace; background-color: #1e1e2f; color: #fff; margin: 0; text-align: center; padding: 50px; }
        .container { background: #3a3a5a; padding: 30px; border-radius: 8px; width: 300px; display: inline-block; }
        h1 { color: #66a3ff; font-size: 32px; }
        input[type="file"] { margin: 20px 0; }
        .btn { background-color: #0056b3; color: #fff; padding: 10px 20px; border: none; border-radius: 4px; }
        .btn:hover { background-color: #66a3ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload & Compress</h1>
        <form action="/compress" method="POST" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required>
            <button class="btn" type="submit">Compress Image</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def homepage():
    return homepage_html

@app.route('/compress', methods=['GET', 'POST'])
def compress():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No file part", 400

        file = request.files['image']
        if file.filename == '':
            return "No selected file", 400

        if not allowed_file(file.filename):
            return "Invalid file type. Please upload a JPG, JPEG, or PNG file.", 400

        # Secure the filename to avoid directory traversal attack
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{filename}")

        file.save(filepath)

        with Image.open(filepath) as img:
            img.save(compressed_path, optimize=True, quality=50)

        return render_template_string(result_html, filename=f"compressed_{filename}")
    return compress_html

@app.route('/report')
def report():
    return '''
    <h1>Report</h1>
    <p>This is a placeholder for the report page.</p>
    <a href="/">Back to Home</a>
    '''

@app.route('/download/<filename>')
def download_file(filename):
    # Secure the filename and ensure file exists
    filename = secure_filename(filename)
    file_path = os.path.join(COMPRESSED_FOLDER, filename)
    
    if not os.path.exists(file_path):
        abort(404, description="File not found")
        
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
