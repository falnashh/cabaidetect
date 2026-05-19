from flask import Flask, request, jsonify
from flask_cors import CORS  # Kunci utama agar Netlify bisa akses backend
import tensorflow as tf
import numpy as np
from PIL import Image
import io

# 1. INISIALISASI FLASK
app = Flask(__name__)
CORS(app)  # Mengizinkan web Netlify kamu menembak data ke server ini

# 2. MEMUAT OTAK AI (DENSENET201)
# Flask akan membaca file .h5 yang kamu upload barengan di GitHub nanti
MODEL_PATH = 'cabaidetect_model.h5'
model = tf.keras.models.load_model(MODEL_PATH)

# Susunan kelas harus sama persis urutannya dengan folder pas training di Colab
NAMA_KELAS = ['Patek', 'Sehat', 'Virus_Kuning']

# 3. MEMBUAT RUTE (ENDPOINT) DETEKSI
@app.route('/predict', methods=['POST'])
def predict():
    # Cek apakah ada file gambar yang dikirim oleh Netlify
    if 'file' not in request.files:
        return jsonify({'error': 'Waduh Bos, gambarnya gak masuk ke server'}), 400
        
    file = request.files['file']
    
    try:
        # 4. MEMPROSES GAMBAR (Sama seperti setelan di Google Colab)
        # Membuka gambar dan memastikan formatnya RGB (bukan PNG transparan/RGBA)
        img = Image.open(io.BytesIO(file.read())).convert('RGB')
        
        # Paksa ukuran gambar jadi 224x224 piksel (Syarat mutlak DenseNet201)
        img = img.resize((224, 224))
        
        # Mengubah gambar jadi array angka dan dinormalisasi (dibagi 255.0)
        img_array = np.array(img) / 255.0
        
        # Menambahkan dimensi batch (dari [224, 224, 3] menjadi [1, 224, 224, 3])
        img_array = np.expand_dims(img_array, axis=0)
        
        # 5. AI MULAI MENEBAK
        prediksi = model.predict(img_array)
        indeks_tertinggi = np.argmax(prediksi[0])
        
        hasil_tebakan = NAMA_KELAS[indeks_tertinggi]
        skor_kepastian = float(prediksi[0][indeks_tertinggi]) # Persentase keyakinan AI
        
        # 6. MEMBERIKAN REKOMENDASI OTOMATIS
        if hasil_tebakan == 'Patek':
            rekomendasi = "Semprot tanaman dengan fungisida berbahan aktif tembaga hidroksida seminggu sekali. Buang dan bakar buah atau daun yang busuk agar tidak menular."
        elif hasil_tebakan == 'Virus_Kuning':
            rekomendasi = "Cabut tanaman yang sudah terinfeksi parah agar tidak menular lewat Kutu Kebul. Semprot vektornya pake insektisida organik atau kimia yang tepat."
        else:
            rekomendasi = "Tanaman cabai kamu aman dan sehat, Bos! Tetap jaga kebersihan lahan dan lakukan pemupukan secara berkala."

        # 7. KIRIM BALIK HASILNYA KE NETLIFY
        return jsonify({
            'status': 'success',
            'kelas': hasil_tebakan,
            'akurasi': skor_kepastian,
            'rekomendasi': rekomendasi
        })
        
    except Exception as e:
        return jsonify({'error': f'Gagal memproses gambar: {str(e)}'}), 500

# Jalankan server Flask (Hanya terpakai saat kamu test di laptop lokal)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
