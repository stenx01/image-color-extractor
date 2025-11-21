from flask import Flask, render_template, request, send_from_directory
import numpy as np
import cv2
from collections import Counter
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def rgb_to_hex(rgb):
    return '#{:02X}{:02X}{:02X}'.format(*rgb)

def get_top_colors(image_path, top_n=10):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (200, 200), interpolation=cv2.INTER_AREA)

    pixels = img.reshape(-1, 3)
    counts = Counter(map(tuple, pixels))

    top_colors = counts.most_common(top_n)
    result = []

    for color, count in top_colors:
        # Convert uint8 to int to prevent overflow
        r, g, b = map(int, color)
        hex_color = rgb_to_hex((r, g, b))
        brightness = (r*299 + g*587 + b*114) / 1000
        text_color = '#000000' if brightness > 186 else '#FFFFFF'
        result.append({
            'hex': hex_color,
            'text_color': text_color
        })
    return result

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/", methods=["GET", "POST"])
def index():
    colors = []
    image_url = None
    if request.method == "POST":
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            image_url = f"/uploads/{filename}"
            colors = get_top_colors(path)
    return render_template("index.html", colors=colors, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)
