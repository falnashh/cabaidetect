const API_URL = 'http://localhost:5000/predict';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const uploadBtn = document.getElementById('uploadBtn');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const changeImageBtn = document.getElementById('changeImageBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loadingSection');
const resultSection = document.getElementById('resultSection');
const resetBtn = document.getElementById('resetBtn');

let currentImageFile = null;

// Event Listeners
uploadArea.addEventListener('click', () => imageInput.click());
uploadBtn.addEventListener('click', () => imageInput.click());
changeImageBtn.addEventListener('click', () => {
    previewSection.style.display = 'none';
    uploadArea.style.display = 'block';
    currentImageFile = null;
});
analyzeBtn.addEventListener('click', analyzeImage);
resetBtn.addEventListener('click', resetDetection);
imageInput.addEventListener('change', handleImageSelect);

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--primary-green)';
    uploadArea.style.background = 'rgba(76, 175, 80, 0.05)';
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--secondary-green)';
    uploadArea.style.background = 'transparent';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file);
    }
    uploadArea.style.borderColor = 'var(--secondary-green)';
    uploadArea.style.background = 'transparent';
});

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (file.size > 5 * 1024 * 1024) {
        alert('Ukuran file terlalu besar! Maksimal 5MB.');
        return;
    }
    
    currentImageFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadArea.style.display = 'none';
        previewSection.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

async function analyzeImage() {
    if (!currentImageFile) {
        alert('Silakan pilih foto terlebih dahulu!');
        return;
    }
    
    // Show loading
    previewSection.style.display = 'none';
    loadingSection.style.display = 'block';
    resultSection.style.display = 'none';
    
    // Prepare form data
    const formData = new FormData();
    formData.append('image', currentImageFile);
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult(data.prediction);
        } else {
            throw new Error(data.error || 'Terjadi kesalahan');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Gagal menganalisis gambar. Pastikan server berjalan dan model telah dilatih.');
        resetDetection();
    }
}

function displayResult(prediction) {
    loadingSection.style.display = 'none';
    resultSection.style.display = 'block';
    
    // Update result content
    document.getElementById('resultIcon').textContent = prediction.icon;
    document.getElementById('pestName').textContent = prediction.name;
    document.getElementById('confidence').textContent = `${prediction.confidence}%`;
    document.getElementById('description').textContent = prediction.description;
    document.getElementById('handling').textContent = prediction.handling;
    document.getElementById('pesticide').textContent = prediction.pesticide;
    
    // Update confidence bar
    const confidenceFill = document.getElementById('confidenceFill');
    confidenceFill.style.width = `${prediction.confidence}%`;
    
    // Add color based on confidence
    if (prediction.confidence > 80) {
        confidenceFill.style.background = 'linear-gradient(90deg, #2e7d32, #4caf50)';
    } else if (prediction.confidence > 60) {
        confidenceFill.style.background = 'linear-gradient(90deg, #ffc107, #ff9800)';
    } else {
        confidenceFill.style.background = 'linear-gradient(90deg, #f44336, #ff5722)';
    }
}

function resetDetection() {
    // Reset all sections
    uploadArea.style.display = 'block';
    previewSection.style.display = 'none';
    loadingSection.style.display = 'none';
    resultSection.style.display = 'none';
    
    // Clear input
    imageInput.value = '';
    currentImageFile = null;
    
    // Clear preview
    previewImage.src = '';
}

// Check API health
async function checkApiHealth() {
    try {
        const response = await fetch('http://localhost:5000/health');
        if (response.ok) {
            console.log('API is healthy');
        }
    } catch (error) {
        console.warn('API not reachable. Make sure backend is running.');
    }
}

// Initialize
checkApiHealth();