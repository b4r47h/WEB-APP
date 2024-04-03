from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import cv2
import os
import uuid
import ocr

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hardcoded user credentials
USERS = {
    'user1': 'password1',
    'user2': 'password2'
}

class LicensePlateDetectorApp:
    def __init__(self):
        self.frame = None
        self.harcascade = "model/haarcascade_russian_plate_number.xml"
        self.min_area = 500
        self.data = {'UUID': [], 'Image_Path': [], 'Plate_Text': []}

    def detect_and_highlight_plates(self):
        plates = self.detect_plates()
        for (x, y, w, h) in plates:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Extract the plate region
            plate_region = self.frame[y:y+h, x:x+w]
            # Perform OCR on the plate region
            plate_text = ocr.perform_ocr(plate_region)
            # Display the extracted text on the frame
            cv2.putText(self.frame, plate_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    def detect_plates(self):
        plate_cascade = cv2.CascadeClassifier(self.harcascade)
        img_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)
        return plates

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[-1]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app.detector = LicensePlateDetectorApp()
        app.detector.frame = cv2.imread(file_path)
        app.detector.detect_and_highlight_plates()
        cv2.imwrite(file_path, app.detector.frame)
        return render_template('result.html', file_path=file_path)
    else:
        flash('Invalid file format', 'error')
        return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)
