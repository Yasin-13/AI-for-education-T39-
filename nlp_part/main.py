from flask import Flask, render_template, request
import os
import pytesseract
from PIL import Image
from googletrans import Translator
from gtts import gTTS

app = Flask(__name__)

# Function to extract text from the image

def extract_text_from_image(image_path):
    try:
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img)
            return text
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to translate text into a specified language
def translate_text(text, lang_code):
    translator = Translator()
    translation = translator.translate(text, dest=lang_code)
    return translation.text

# Function to convert text to speech
def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    tts.save("static/output.mp3")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if request.method == 'POST':
        image = request.files['image']
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

            return render_template('translation_result.html', 
                                    original_text=extracted_text, 
                                    translated_text=translation,
                                    translated_language=translated_language)
        else:
            return "Invalid language selection"

if __name__ == '__main__':
    app.run(debug=True)
