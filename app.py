from flask import Flask,render_template,jsonify,request
from pymongo import MongoClient
from datetime import datetime

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__),'.env')
load_dotenv(dotenv_path)

# Uniform Source Identifier URI referring to the resources on the internet is a string identifier
MONGODB_URI = os.environ.get("DB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/diary',methods=['GET'])
def getdiary():
    diary_packet = list(db.diary.find({},{'_id':False}))
    return jsonify({'diaries':diary_packet})

@app.route('/diary',methods=['POST'])
def postdiary():
    #sample_receive = request.form.get('sample_give')
    #print(sample_receive)
    title_receive = request.form.get('title_give')
    content_receive = request.form.get('content_give')

    # Time and date
    today = datetime.now()
    date_user_posted = today.strftime('%d-%b-%Y')

    #yang diminta om mentor korea :v
    # Jika title dan deskripsi tidak ada maka return error, image hanyalah opsional
    if not title_receive or not content_receive :
        return jsonify({'msg':'error data was incorrect'})
    else :
        # Jika image title dan profile tidak ada
        if 'profile' not in request.files and 'file_give' not in request.files:
            # --- Save deskripsi dan judul ---
            doc = {
                'date' : date_user_posted,
                'title' : title_receive,
                'content' : content_receive
            }
            # --- Kirim ke MongoDB
            db.diary.insert_one(doc)
            return jsonify({'msg':'data saved!'})
        
        # Jika hanya image title saja terupload
        elif 'profile' not in request.files :
            file_receive = request.files['file_give']
            extension = file_receive.filename.split('.')[-1]
            # Title image handler
            unique_id = today.strftime('%A-%d-%b-%Y-%H-%M-%S')
            file_name_image = f'static/img_title/upload-{unique_id}.{extension}'
            file_receive.save(file_name_image)
            # --- Save deskripsi dan judul ---
            doc = {
                'date' : date_user_posted,
                'file' : file_name_image,
                'title' : title_receive,
                'content' : content_receive
            }
            # --- Kirim ke MongoDB
            db.diary.insert_one(doc)
            return jsonify({'msg':'data saved!'})
        
        # Jika hanya profile saja yang terupload
        elif 'file_give' not in request.files :
            profile_receive = request.files['profile']
            extension_prf = profile_receive.filename.split('.')[-1]
            # Profile handler
            unique_id_prf = today.strftime('%A-%d-%b-%Y-%H-%M-%S')
            file_name_profile = f'static/profile/upload-{unique_id_prf}.{extension_prf}'
            profile_receive.save(file_name_profile)
            # --- Save deskripsi dan judul ---
            doc = {
                'date' : date_user_posted,
                'profile' : file_name_profile,
                'title' : title_receive,
                'content' : content_receive
            }
            # --- Kirim ke MongoDB
            db.diary.insert_one(doc)
            return jsonify({'msg':'data saved!'})

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)