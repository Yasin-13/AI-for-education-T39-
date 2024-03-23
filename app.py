import base64
from distutils.command import build
import io
import json
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
import pytesseract
from googletrans import Translator
from gtts import gTTS
import os
from googleapiclient.discovery import build
import requests
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


app = Flask(__name__)

# Dummy data for users
users = {'user1': 'password1', 'user2': 'password2'}

# Function to extract text from the image
def extract_text_from_image(image_path):
    try:
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img)
            return text.strip()  # Strip any leading or trailing whitespace
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""  # Return an empty string or handle the error as needed

# Function to translate text into a specified language
def translate_text(text, lang_code):
    try:
        if text:
            translator = Translator()
            translation = translator.translate(text, dest=lang_code)
            return translation.text
        else:
            return ""  # Return empty string if no text to translate
    except Exception as e:
        print(f"Translation error: {e}")
        return ""  # Return an empty string or handle the error as needed

# Function to convert text to speech
def text_to_speech(text, lang_code):
    try:
        if text:
            tts = gTTS(text=text, lang=lang_code)
            tts.save("static/output.mp3")
    except Exception as e:
        print(f"Text-to-speech error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            # Redirect to the dashboard page after successful login
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password. Please try again.")
    return render_template('login.html')

def perform_clustering(student_data):
    # Step 2: Feature Engineering
    # No feature engineering required for this example

    # Step 3: Clustering
    # Determine the optimal number of clusters
    max_clusters = min(len(student_data) - 1, 5)  # Limiting max clusters to avoid error
    best_score = -1
    best_n_clusters = 2
    for n_clusters in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=n_clusters)
        cluster_labels = kmeans.fit_predict(student_data)
        silhouette_avg = silhouette_score(student_data, cluster_labels)
        if silhouette_avg > best_score:
            best_score = silhouette_avg
            best_n_clusters = n_clusters

    # Perform clustering with the optimal number of clusters
    kmeans = KMeans(n_clusters=best_n_clusters)
    cluster_labels = kmeans.fit_predict(student_data)

    # Step 5: Collaborative Filtering
    # Use nearest neighbors for collaborative filtering
    pca = PCA(n_components=2)
    student_data_pca = pca.fit_transform(student_data)
    
    # Plotting
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(student_data_pca[:, 0], student_data_pca[:, 1], c=cluster_labels, cmap='viridis')
    ax.set_title('Clustering of Student Performance')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Cluster')

    # Convert plot to image
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url




@app.route('/plot')
def plot1():
    # Sample student performance data (replace this with your actual data)
    student_data = np.array([
        [90, 85, 80],  # Student 1: Grades in [Math, Science, English]
        [70, 75, 80],  # Student 2
        [50, 60, 65],  # Student 3
        [50, 61, 62],  # Student 4 
        [90, 90, 90],  # Student 5
        [25, 34, 45],  # Student 6
        [90, 85, 80],  # Student 7 
        # Add more students...
    ])
    # Perform clustering and get the plot URL
    plot_url = perform_clustering(student_data)
    return render_template('plot.html', plot_url=plot_url)

@app.route('/plot')
def plot():
    return render_template('plot.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            # Redirect to the login page after successful registration
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="Username already exists. Please choose a different one.")
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/test_portal.html')
def test_portal():
    return render_template('test_portal.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/translate', methods=['POST'])
def translate():
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('translate.html', error="No file part.")

        image = request.files['image']

        if image.filename == '':
            return render_template('translate.html', error="No selected file.")

        image_path = "static/uploaded_image.jpg"
        image.save(image_path)

        # Extract text from the uploaded image
        extracted_text = extract_text_from_image(image_path)

        # Language codes for translation services
        target_languages = {
            'hi': 'Hindi',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'ur': 'Urdu',
            # Add more target languages as needed
        }

        selected_language = request.form['language']

        # Translate the extracted text into the selected language
        if selected_language in target_languages:
            translation = translate_text(extracted_text, selected_language)
            translated_language = target_languages[selected_language]

            # Convert translated text to speech
            text_to_speech(translation, selected_language)

            return render_template('translated_page.html', 
                                    original_text=extracted_text, 
                                    translated_text=translation,
                                    translated_language=translated_language)
        else:
            return render_template('translate.html', error="Invalid language selection.")

@app.route('/translate.html')
def translated_page():
    return render_template('translate.html')

def read_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def train_chatbot(training_data):
    responses = {}
    for item in training_data:
        user_input = item['user_input'].lower()
        response = item['response']
        responses[user_input] = response
    return responses

def get_response(user_input, responses):
    if user_input.lower() in responses:
        return responses[user_input.lower()]
    else:
        return "Sorry, I don't understand that."



@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['user_input']
    response = get_response(user_input, responses)
    return response



YOUTUBE_API_KEY = 'AIzaSyCqF6YLucG2WjE2mGTzY1HcKws9GowzjA4' 

@app.route('/submit', methods=['POST'])
def submit():
    score = 0
    answers = {
        'question1': '4',
        'question2': '6',
        'question3': 'apple',
        'question4': 'bat',
        'question5': 'Paris',
        'question6': '7'
    }
    for question, answer in answers.items():
        if request.form.get(question) == answer:
            score += 1

    grade = None
    if score >= 5:
        grade = "3"
    elif score >= 3:
        grade = "2"
    else:
        grade = "1"

    return redirect(url_for('videos', grade=grade))

@app.route('/videos/<grade>')
def videos(grade):
    youtube = build('youtube', 'v3', developerKey='AIzaSyAz9zGXWONczvHClj1i-YrRqbVV5glRQL8')
    search_response = youtube.search().list(
        q='Grade {} educational videos'.format(grade),
        part='id,snippet',
        maxResults=5
    ).execute()
    videos = []
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append({
                'title': search_result['snippet']['title'],
                'video_id': search_result['id']['videoId']
            })
    return render_template('videos.html', videos=videos)

@app.route('/quiz')
def quiz():
    # You can perform any necessary actions here before rendering the quiz template
    return render_template('quiz.html')

app.route('/submit', methods=['POST'])
def submit():
    try:
        grade11_math_score = int(request.form['grade11_math'])
        grade11_science_score = int(request.form['grade11_science'])
        grade12_math_score = int(request.form['grade12_math'])
        grade12_science_score = int(request.form['grade12_science'])
    except ValueError:
        # Handle the case where non-numeric values are passed
        return "Error: Please select a choice for each question."

    grade11_lowest_score = min(grade11_math_score, grade11_science_score)
    grade12_lowest_score = min(grade12_math_score, grade12_science_score)

    grade11_video = get_video(11, grade11_lowest_score)
    grade12_video = get_video(12, grade12_lowest_score)

    return render_template('video1.html', grade11_video=grade11_video, grade12_video=grade12_video)

def get_video(grade, score):
    subject = 'math' if score == request.form[f'grade{grade}_math'] else 'science'
    query = f"Grade {grade} {subject} tutorials"

    url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&part=snippet&type=video&maxResults=1&q={query}"

    response = requests.get(url)
    data = json.loads(response.text)

    if 'items' in data:
        video_id = data['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        return "No video found"
    
@app.route('/quiz1')
def quiz1():
    # You can perform any necessary actions here before rendering the quiz template
    return render_template('quiz1.html')
    

if __name__ == "__main__":
    file_path = 'training_data.json'
    try:
        training_data = read_json_data(file_path)
    except FileNotFoundError:
        print(f"Error: Unable to find the file '{file_path}'. Make sure the file exists and try again.")
        exit()

    responses = train_chatbot(training_data)
    app.run(debug=True)
    
      

