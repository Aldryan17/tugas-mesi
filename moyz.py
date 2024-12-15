from flask import Flask, render_template_string, request, send_file
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# Homepage HTML
homepage_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pixel Compress</title>
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;
            background-color: #1e1e2f;
            color: #fff;
            margin: 0;
            text-align: center;
            padding: 50px;
            image-rendering: pixelated;
        }
        .container {
            display: inline-block;
            background: #3a3a5a;
            border: 4px solid #0056b3;
            box-shadow: 4px 4px #003366;
            padding: 30px;
            border-radius: 8px;
            width: 300px;
        }
        h1 {
            color: #66a3ff;
            font-size: 32px;
            text-transform: uppercase;
        }
        p {
            color: #cce6ff;
        }
        .btn {
            font-size: 20px;
            background-color: #0056b3;
            color: #ffffff;
            padding: 10px 20px;
            border: 2px solid #003366;
            border-radius: 4px;
            text-decoration: none;
            cursor: pointer;
            box-shadow: 2px 2px #003366;
            display: block;
            margin: 10px auto;
        }
        .btn:hover {
            background-color: #66a3ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Pixel Compress</h1>
        <p>Compress your photos in a pixelated style!</p>
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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.css" />
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;
            background-color: #1e1e2f;
            color: #fff;
            margin: 0;
            text-align: center;
            padding: 50px;
            image-rendering: pixelated;
        }
        .container {
            display: inline-block;
            background: #3a3a5a;
            border: 4px solid #0056b3;
            box-shadow: 4px 4px #003366;
            padding: 30px;
            border-radius: 8px;
            width: 300px;
        }
        h1 {
            color: #66a3ff;
            font-size: 32px;
            text-transform: uppercase;
        }
        input[type="file"] {
            display: block;
            margin: 20px auto;
            padding: 5px;
            border: 2px dashed #66a3ff;
            background-color: #3a3a5a;
            color: #cce6ff;
            width: 80%;
            text-align: center;
        }
        .btn {
            font-size: 20px;
            background-color: #0056b3;
            color: #ffffff;
            padding: 10px 20px;
            border: 2px solid #003366;
            border-radius: 4px;
            cursor: pointer;
            box-shadow: 2px 2px #003366;
        }
        .btn:hover {
            background-color: #66a3ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Compress Your Image</h1>
        <form id="cropForm" action="/compress" method="POST" enctype="multipart/form-data">
            <input type="file" id="inputImage" name="image" accept="image/*" required>
            <img id="image" src="" alt="Gambar" style="display:none;"/>
            <button class="btn" type="button" id="cropButton">Crop & Compress</button>
        </form>
    </div>

    <canvas id="canvas" style="display:none;"></canvas>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.js"></script>
    <script>
        let cropper;
        const image = document.getElementById('image');
        const inputImage = document.getElementById('inputImage');
        const cropButton = document.getElementById('cropButton');
        const canvas = document.getElementById('canvas');

        inputImage.addEventListener('change', (event) => {
            const files = event.target.files;
            const done = (url) => {
                image.src = url;
                image.style.display = 'block';
            };
            let reader;
            let file;

            if (files && files.length > 0) {
                file = files[0];

                if (URL) {
                    done(URL.createObjectURL(file));
                } else if (FileReader) {
                    reader = new FileReader();
                    reader.onload = (e) => {
                        done(reader.result);
                    };
                    reader.readAsDataURL(file);
                }
            }
        });

        image.addEventListener('load', () => {
            cropper = new Cropper(image, {
                aspectRatio: 16 / 9,
                viewMode: 1,
            });
        });

        cropButton.addEventListener('click', () => {
            const croppedCanvas = cropper.getCroppedCanvas();
            canvas.width = croppedCanvas.width;
            canvas.height = croppedCanvas.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(croppedCanvas, 0, 0);
            const croppedImage = canvas.toDataURL('image/png');

            // Create a Blob from the cropped image
            canvas.toBlob((blob) => {
                const formData = new FormData();
                formData.append('image', blob, 'cropped_image.png');

                // Send the cropped image to the server
                fetch('/compress', {
                    method: 'POST',
                    body: formData,
                })
                .then(response => response.text())
                .then(data => {
                    document.body.innerHTML = data; // Replace the body with the result
                })
                .catch(error => console.error('Error:', error));
            }, 'image/png');
        });
    </script>
</body>
</html>
'''

# Result Page HTML
result_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download Compressed Image</title>
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;
            background-color: #1e1e2f;
            color: #fff;
            margin: 0;
            text-align: center;
            padding: 50px;
            image-rendering: pixelated;
        }
        .container {
            display: inline-block;
            background: #3a3a5a;
            border: 4px solid #0056b3;
            box-shadow: 4px 4px #003366;
            padding: 30px;
            border-radius: 8px;
            width: 300px;
        }
        h1 {
            color: #66a3ff;
            font-size: 32px;
            text-transform: uppercase;
        }
        .btn {
            font-size: 20px;
            background-color: #0056b3;
            color: #ffffff;
            padding: 10px 20px;
            border: 2px solid #003366;
            border-radius: 4px;
            text-decoration: none;
            cursor: pointer;
            box-shadow: 2px 2px #003366;
        }
        .btn:hover {
            background-color: #66a3ff;
        }
    </style ```python
</head>
<body>
    <div class="container">
        <h1>Image Compressed!</h1>
        <a href="{{ url_for('download_file', filename=filename) }}" class="btn">Download Image</a>
    </div>
</body>
</html>
'''

# Report Page HTML
report_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report</title>
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;
            background-color: #1e1e2f;
            color: #fff;
            margin: 0;
            text-align: center;
            padding: 50px;
        }
        .container {
            display: inline-block;
            background: #3a3a5a;
            border: 4px solid #0056b3;
            box-shadow: 4px 4px #003366;
            padding: 30px;
            border-radius: 8px;
            width: 300px;
        }
        h1 {
            color: #66a3ff;
            font-size: 32px;
            text-transform: uppercase;
        }
        p {
            color: #cce6ff;
        }
        .btn {
            font-size: 20px;
            background-color: #0056b3;
            color: #ffffff;
            padding: 10px 20px;
            border: 2px solid #003366;
            border-radius: 4px;
            text-decoration: none;
            cursor: pointer;
            box-shadow: 2px 2px #003366;
        }
        .btn:hover {
            background-color: #66a3ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Report</h1>
        <p>Here you can display your report data or statistics.</p>
        <a href="/" class="btn">Back to Home</a>
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
            return "No file uploaded", 400

        file = request.files['image']
        if file.filename == '':
            return "No selected file", 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{file.filename}")

        file.save(filepath)
        with Image.open(filepath) as img:
            img.save(compressed_path, optimize=True, quality=50)

        return render_template_string(result_html, filename=f"compressed_{file.filename}")
    return compress_html

@app.route('/report')
def report():
    return report_html

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(COMPRESSED_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
    