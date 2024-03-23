import base64
import io
from flask import Flask, render_template, request, redirect, url_for
from googleapiclient.discovery import build


app = Flask(__name__)

YOUTUBE_API_KEY = 'AIzaSyAz9zGXWONczvHClj1i-YrRqbVV5glRQL8'  # Replace with your actual API key

@app.route('/')
def quiz():
    return render_template('quiz.html')

@app.route('/submit', methods=['POST'])
def submit():
    score = 0
    answers = {
        'question1': '56',
        'question2': '9',
        'question3': 'library',
        'question4': 'joyful',
        'question5': 'Nile',
        'question6': 'Thomas Edison'
    }
    for question, answer in answers.items():
        if request.form.get(question) == answer:
            score += 1

    grade = None
    if score >= 5:
        grade = "5"
    elif score >= 3:
        grade = "4"
    else:
        grade = "4"  # Default to Grade 3

    return redirect(url_for('videos', grade=grade, score=score))



@app.route('/videos/<grade>/<score>')
def videos(grade, score):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # Define keywords for different subjects
    math_keywords = "mathematics lesson"
    english_keywords = "english lesson"
    gk_keywords = "general knowledge for kids"

    # Use subject-specific keywords based on grade level
    if grade == "5":
        search_query = math_keywords + " grade 5"
    elif grade == "4":
        search_query = english_keywords + " grade 4"
    else:
        search_query = gk_keywords + " grade 3"

    search_response = youtube.search().list(
        q=search_query,
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
    return render_template('videos.html', videos=videos, score=score)

if __name__ == '__main__':
    app.run(debug=True)
