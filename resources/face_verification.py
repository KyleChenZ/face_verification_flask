from flask_restful import Resource, request
from models.user import UserModel
from flask_login import login_required, current_user
from flask import redirect, request
import face_recognition
import numpy as np
import json

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_faces_in_image(image_file):
    # Load the uploaded image file
    img = face_recognition.load_image_file(image_file)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False

    if len(unknown_face_encodings) > 0:
        face_found = True
        # Return the result as json
        result = {
            "face_found_in_image": face_found,
            "face_vectors": unknown_face_encodings[0]
        }
        return result

    result = {
        "face_found_in_image": face_found,
    }
    return result

def compare(unknown,knowns):
    match_results = face_recognition.compare_faces(knowns, unknown,tolerance=0.6)
    if any(match_results):
        return True
    return False

class FaceVerification(Resource):
    @login_required
    def post(self, id=None):
        if 'image' not in request.files:
            return redirect(request.url)
        user_id = current_user.id
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        if not user_id:
            return {"message": "Please login to use this feature"}, 401
        if not file or not user_id:
            return {"message": "No image received"}, 404
        user_data = UserModel.find_by_id(current_user.id).json()
        if 'faces' not in user_data or not user_data['faces']:
            return {"message": "Please add face id before using this feature"}, 401
        known_face_encodings= []
        for f in user_data['faces']:
            face_vectors = json.loads(f['face_vectors'])
            known_face_encodings.append(face_vectors)
        face_detected=False
        result = {}
        if file and allowed_file(file.filename):
            result = detect_faces_in_image(file)
            face_detected = result['face_found_in_image']
        if face_detected and 'face_vectors' in result:
            unknown_face_encoding = result['face_vectors']
            match = compare(unknown_face_encoding,np.asarray(known_face_encodings))
            if match:
                return {"match": True}, 200
            else:
                return {"match": False}, 200
        else:
            return {"message": "Fail to detect a face for the uploaded photo. Please try to upload a clear photo"}, 500