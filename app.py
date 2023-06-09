from flask import Flask, render_template, request
import soundfile as sf
import cv2
import numpy as np
import base64
import os
from pydub import AudioSegment

app = Flask(__name__)

# Set folder untuk menyimpan file yang diolah
UPLOAD_FOLDER = "uploads"
RESIZED_FOLDER = "resized"
COMPRESSED_FOLDER = "compressed"

# Membuat folder jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESIZED_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

app.static_folder = "static"


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/gambar", methods=["GET", "POST"])
def gambar():
    if request.method == "POST":
        # Menerima file gambar dari form
        width = int(request.form["width"])
        uploaded_file = request.files["image"]

        # Baca gambar menggunakan OpenCV
        image = cv2.imdecode(
            np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR
        )

        dimensi = image.shape
        d_height = dimensi[0]
        d_width = dimensi[1]

        # Resize gambar
        scale = d_width / d_height
        widthScale = width
        heightScale = width / scale
        dimensi_image_resize = (
            int(widthScale),
            int(heightScale),
        )

        resized_image = cv2.resize(image, dimensi_image_resize)

        # Konversi gambar ke dalam format base64
        _, img_encoded = cv2.imencode(".jpg", resized_image)
        resized_image_base64 = base64.b64encode(img_encoded).decode("utf-8")

        # menyimpan gambar
        resized_image_path = "static/resized_image.jpg"
        cv2.imwrite(resized_image_path, resized_image)

        # Tampilkan halaman HTML dengan gambar yang diresize
        return render_template(
            "index.html",
            resized_path=resized_image_path,
            resized_image=resized_image_base64,
        )
    # Tampilkan halaman HTML untuk unggah gambar


@app.route("/audio", methods=["GET", "POST"])
def audio():
    if request.method == "POST":
        # Ambil file audio yang diunggah
        uploaded_file = request.files["audio"]

        # Buat file sementara untuk menyimpan file audio yang diunggah
        temp_file_path = os.path.join(UPLOAD_FOLDER, "uploaded_audio.mp3")
        uploaded_file.save(temp_file_path)

        # Baca file audio menggunakan PyDub
        audio = AudioSegment.from_file(temp_file_path)

        # Kompresi audio dengan mengurangi bitrate
        compressed_audio = audio.set_frame_rate(16000)

        # Simpan audio hasil kompresi dalam file sementara
        compressed_audio_path = "static/compressed_audio.mp3"
        compressed_audio.export(compressed_audio_path, format="mp3")

        # Menghitung ukuran file sebelum dan sesudah kompresi
        original_file_size = os.path.getsize(temp_file_path)
        compressed_file_size = os.path.getsize(compressed_audio_path)

        ori_size_kb = original_file_size / 1000000
        compress_size_kb = compressed_file_size / 1000000

        # Mengirimkan file sementara dan informasi ukuran file sebagai respons
        return render_template(
            "index.html",
            compressed=compressed_audio,
            compressed_audio=compressed_audio_path,
            original_size=ori_size_kb,
            compressed_size=compress_size_kb,
        )
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
