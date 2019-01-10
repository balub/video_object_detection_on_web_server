from __future__ import division, print_function
# coding=utf-8
from function.video import *
from function.DetectionValue import *
from function.camera import VideoCamera
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Flask utils
from flask import Flask, redirect, url_for, request, render_template, Response
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

# Define a flask app
app = Flask(__name__)
camera = VideoCamera('outputs/video.mp4')
def get_file_path_and_save(request):
    # Get the file from post request
    f = request.files['file']

    # Save the file to ./uploads
    basepath = os.path.dirname(__file__)
    file_path = os.path.join(
        basepath, 'uploads', secure_filename('video.mp4'))
    f.save(file_path)
    return f.filename



@app.route('/upload', methods=['GET'])
def upload():
    return render_template('upload.html')

@app.route('/watch', methods=['GET'])
def test():
    return render_template('watch.html')


@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        file_name = get_file_path_and_save(request)
        detection = DetectionValue()
        detection.set_display(0)
        detection.set_output(1)
        detection.set_input_videos('uploads/video.mp4')
        detection.set_output_path("outputs/video.mp4")
        video(detection)
        return file_name
    return None


def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame != "":
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():

    return Response(gen(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Serve the app with gevent
    http_server = WSGIServer(('localhost', 5000), app)
    http_server.serve_forever()
