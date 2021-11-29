from flask_restful import Resource, reqparse, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.face import FaceModel
from flask_login import login_required, current_user
from flask import redirect, jsonify, request
import face_recognition
import json
import numpy as np
import PIL

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_image_file(file, mode='RGB'):
    """
    Loads an image file (.jpg, .png, etc) into a numpy array

    :param file: image file name or file object to load
    :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
    :return: image contents as numpy array
    """
    im = PIL.Image.open(file)
    width, height = im.size
    try:
        #rotate accordingly
        im = PIL.ImageOps.exif_transpose(im)   
    except:
        pass

    if width > 4000 :
        new_width = 2000
        wpercent = (new_width/float(im.size[0]))
        hsize = int((float(im.size[1])*float(wpercent)))
        im = im.resize((new_width,hsize), PIL.Image.ANTIALIAS)
    elif height > 4000:
        new_height = 2000
        hpercent = (new_height/float(im.size[0]))
        wsize = int((float(im.size[1])*float(hpercent)))
        im = im.resize((new_height,wsize), PIL.Image.ANTIALIAS)
    if mode:
        im = im.convert(mode)
    return np.array(im)

def detect_faces_in_image(img):
    # Load the uploaded image file
    #img = face_recognition.load_image_file(image_file)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False

    if len(unknown_face_encodings) > 0:
        face_found = True
        result = {
        "face_found_in_image": face_found,
        "face_vectors": unknown_face_encodings[0]
        }
        return result
    # Return the result as json
    result = {
        "face_found_in_image": face_found
    }
    return result


class Face(Resource):
    @login_required
    def post(self, id=None):
        if 'image' not in request.files:
            return redirect(request.url)
        
        user_id = current_user.id

        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)

        if current_user.role == 'admin':
            pass
        if not user_id:
            return {"message": "Please login to use this feature"}, 401
        if not file or not user_id:
            return {"message": "No image received"}, 404

        face_detected=False
        if file and allowed_file(file.filename):
            image = load_image_file(file)
            result = detect_faces_in_image(image)
            face_detected = result['face_found_in_image']
        
        if face_detected and 'face_vectors' in result:
            print(result['face_vectors'])
            json_object = json.dumps(np.round(result['face_vectors'],decimals=9).tolist()) 
            data = {
                "face_vectors":json_object,
                "user_id":user_id
            }
            
            face = FaceModel(**data)
            print(face)
            try:
                face.save_to_db()
            except:
                return {"message": "An error occurred inserting the face."}, 500

            return face.json(), 201
        else:
            return {"message": "Fail to generage a face id. Please try to upload a clear photo"}, 500

    @login_required
    def delete(self, id):
        if not id:
            return {'message': 'No face id specified'}, 404
        user_id = current_user.id

        face = FaceModel.find_by_id(id)
        face_json = face.json()

        if face:
            if current_user.role == 'admin' or user_id == face_json['user_id']:
                face.delete_from_db()
                return {'message': 'Face deleted.'}
            else:
                return {'message': 'Admin privilege required.'}, 401
        
        return {'message': 'Face not found.'}, 404


class FaceList(Resource):
    def get(self):
        user_id = current_user.id
        if current_user.role == 'admin':
            faces = [face.json() for face in FaceModel.find_all()]
        else:
            faces = [face.json() for face in FaceModel.find_by_user_id(user_id)]
        
        if user_id:
            return {'faces': faces}, 200
        return {
            'faces': [face['id'] for face in faces],
            'message': 'More data available if you log in.'
        }, 200
        