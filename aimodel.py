from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
CORS(app)

# Load model
model = tf.keras.models.load_model('models/pest_model.h5')

# Class definitions
CLASSES = {
    0: {
        'name': 'Sehat',
        'description': 'Tanaman dalam kondisi sehat',
        'handling': 'Lakukan perawatan rutin dan pencegahan secara berkala',
        'pesticide': 'Tidak diperlukan',
        'icon': '🌿'
    },
    1: {
        'name': 'Kutu Daun (Aphids)',
        'description': 'Hama kecil berwarna hijau atau hitam yang mengisap cairan daun',
        'handling': 'Semprot dengan larutan air sabun atau minyak neem. Lakukan 2-3 kali seminggu',
        'pesticide': 'Pestisida nabati (ekstrak tembakau atau daun pepaya)',
        'icon': '🐛'
    },
    2: {
        'name': 'Thrips',
        'description': 'Hama kecil berwarna kuning atau hitam yang menyebabkan daun keriting',
        'handling': 'Gunakan perangkap kuning dan semprot dengan insektisida berbahan aktif imidakloprid',
        'pesticide': 'Imidakloprid 200 SL (1 ml/liter air)',
        'icon': '🦟'
    },
    3: {
        'name': 'Tungau (Mites)',
        'description': 'Hama mikroskopis yang menyebabkan daun menguning dan keriting',
        'handling': 'Semprot dengan akarisida dan jaga kelembaban tanaman',
        'pesticide': 'Akarisida berbahan aktif abamektin',
        'icon': '🕷️'
    },
    4: {
        'name': 'Bercak Daun (Leaf Spot)',
        'description': 'Penyakit jamur yang menyebabkan bercak coklat pada daun',
        'handling': 'Buang daun terserang dan semprot dengan fungisida',
        'pesticide': 'Fungisida berbahan aktif mankozeb atau klorotalonil',
        'icon': '🍂'
    }
}

def preprocess_image(image):
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize to 224x224
    image = image.resize((224, 224))
    
    # Convert to array and normalize
    image_array = np.array(image) / 255.0
    
    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)
    
    return image_array

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get image from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Preprocess
        processed_image = preprocess_image(image)
        
        # Make prediction
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class]) * 100
        
        # Get class info
        pest_info = CLASSES[predicted_class]
        
        # Return result
        return jsonify({
            'success': True,
            'prediction': {
                'class': predicted_class,
                'name': pest_info['name'],
                'confidence': round(confidence, 2),
                'description': pest_info['description'],
                'handling': pest_info['handling'],
                'pesticide': pest_info['pesticide'],
                'icon': pest_info['icon']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)