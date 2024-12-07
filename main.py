from flask import Flask, request, jsonify
from models import db, Video, User
from flask_migrate import Migrate
from utils import trim_video, merge_videos
# from datetime 
import datetime
import os, jwt, datetime
from functools import wraps  # Import wraps

SECRET_KEY = 'some_secret_key'

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        token = token.split(' ')[1]
        # print('---------------------------------------->>', token)
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # print('---------------------------------------->>', data)
            user_id = data.get('user_id')
            # print('---------------------------------------->>', user_id)
            kwargs['user_id'] = user_id
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            print('---------------------------------------->>', data)
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400
    
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            SECRET_KEY,
            algorithm='HS256'
        )
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        print(' --- > > > ', token)
        return jsonify({'token': token}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/upload', methods=['POST'])
@token_required
def upload_video(*args, **kwargs):
    file = request.files.get('video')
    user = kwargs.get('user_id', None)
    print(user)
    if not file:
        return jsonify({"error": "No file provided"}), 400

    size_mb = len(file.read()) / (1024 * 1024)
    file.seek(0)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Validate video using OpenCV
    duration = validate_video(file_path)
    if not duration:
        os.remove(file_path)
        return jsonify({"error": "Invalid video format"}), 400
    print('......... >>>>>>> >>>>>>> ', user)

    new_video = Video(
        filename=file.filename,
        upload_time=datetime.datetime.utcnow(),
        size=size_mb,
        duration=duration,
        user_id= user
    )
    db.session.add(new_video)
    db.session.commit()

    return jsonify({"message": "Video uploaded successfully", "filename": file.filename}), 201
    # return jsonify('success')

@app.route('/trim', methods=['POST'])
@token_required
def trim(*args, **kwargs):
    data = request.json
    video = Video.query.filter_by(filename=data['video_name']).first()

    if not video:
        return jsonify({"error": "Video not found"}), 404

    input_path = os.path.join(UPLOAD_FOLDER, video.filename)
    output_path = os.path.join(PROCESSED_FOLDER, f"trimmed_{video.filename}")

    try:
        trim_video(input_path, output_path, data['start_time'], data['end_time'])
        return jsonify({"message": "Video trimmed successfully", "output": output_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/merge', methods=['POST'])
@token_required
def merge(*args, **kwargs):
    data = request.json
    video_paths = [os.path.join(UPLOAD_FOLDER, name) for name in data['video_names']]
    output_path = os.path.join(PROCESSED_FOLDER, "merged_video.mp4")

    try:
        merge_videos(video_paths, output_path)
        return jsonify({"message": "Videos merged successfully", "output": output_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def validate_video(file_path):
    import cv2
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frame_count / fps

if __name__ == '__main__':
    app.run(debug=True)
