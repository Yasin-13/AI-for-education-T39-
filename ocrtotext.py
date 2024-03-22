import pytesseract
from PIL import Image
from googletrans import Translator
from gtts import gTTS
import os

# Function to convert image to text using OCR
def image_to_text(image_path):
    # Open image using PIL
    img = Image.open(image_path)
    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(img)
    return text

# Function to translate text to Hindi
def translate_to_hindi(text):
    translator = Translator()
    translated_text = translator.translate(text, dest='hi').text
    return translated_text

# Function to translate text to Marathi
def translate_to_marathi(text):
    translator = Translator()
    translated_text = translator.translate(text, dest='mr').text
    return translated_text

# Function to convert text to speech
def text_to_speech(text, language):
    tts = gTTS(text=text, lang=language)
    tts.save("output.mp3")
    os.system("mpg123 output.mp3")  # Adjust this line for your operating system if needed

# Example usage
image_path = "D:/bridgethegap/ML/2.jpg"
detected_text = image_to_text(image_path)
print("Detected Text (English):", detected_text)

translated_text_hindi = translate_to_hindi(detected_text)
print("Translated Text (Hindi):", translated_text_hindi)
text_to_speech(translated_text_hindi, 'hi')

translated_text_marathi = translate_to_marathi(detected_text)
print("Translated Text (Marathi):", translated_text_marathi)
text_to_speech(translated_text_marathi, 'mr')
