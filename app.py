from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import logging
import pymongo
import os
import traceback

logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            query = request.form['content'].replace(" ", "")
            save_directory = "images/"
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }

            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")
            soup = BeautifulSoup(response.content, "html.parser")
            image_tags = soup.find_all("img")

            del image_tags[0]
            img_data = []
            for index, image_tag in enumerate(image_tags):
                image_url = image_tag['src']
                image_data = requests.get(image_url).content
                mydict = {"Index": index, "Image": image_data}
                img_data.append(mydict)
                with open(os.path.join(save_directory, f"{query}_{index}.jpg"), "wb") as f:
                    f.write(image_data)

            # Update MongoDB connection string with new username and password
            client = pymongo.MongoClient("mongodb+srv://prince2002:prince2002@cluster0.sdehavr.mongodb.net/")
            db = client['image_scrap']
            review_col = db['image_scrap_data']
            review_col.insert_many(img_data)

            return "Images loaded"
        except Exception as e:
            logging.error(traceback.format_exc())  # Log the full traceback
            return f'Something went wrong: {e}'
    else:
        return render_template('index.html')
