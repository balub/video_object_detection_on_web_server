### Object Detection in Video and Streaming Web Server

In this article, I will present how I managed to use Tensorflow Object-detection API to perform both real-time (webcam) and video post-processing. I used OpenCV with python3 multiprocessing and multi-threading libraries. And This article is dedicated to streaming, an interesting feature that gives Flask applications the ability to provide large responses efficiently partitioned in small chunks, potentially over a long period of time. To illustrate the topic I'm going to show you how to build a live video streaming server!

####  What is Streaming?
Streaming is a technique in which the server provides the response to a request in chunks. I can think of a couple of reasons why this might be useful:
Very large responses. Having to assemble a response in memory only to return it to the client can be inefficient for very large responses. An alternative would be to write the response to disk and then return the file with flask.send_file(), but that adds I/O to the mix. Providing the response in small portions is a much better solution, assuming the data can be generated in chunks.
Real time data. For some applications a request may need to return data that comes from a real time source. A pretty good example of this is a real time video or audio feed. A lot of security cameras use this technique to stream video to web browsers.

Implementing Streaming With Flask
Flask provides native support for streaming responses through the use of generator functions. A generator is a special function that can be interrupted and resumed. Consider the following function:

                  def gen():
                      yield 1
                      yield 2
                      yield 3
                      
This is a function that runs in three steps, each returning a value. Describing how generator functions are implemented is outside the scope of this article, but if you are a bit curious the following shell session will give you an idea of how generators are used:

                  >>> x = gen()
                  >>> x
                  <generator object gen at 0x7f06f3059c30>
                  >>> x.next()
                  1
                  >>> x.next()
                  2
                  >>> x.next()
                  3
                  >>> x.next()
                  Traceback (most recent call last):
                    File "<stdin>", line 1, in <module>
                  StopIteration
                  
You can see in this simple example that a generator function can return multiple results in sequence. Flask uses this characteristic of generator functions to implement streaming.
The example below shows how using streaming it is possible to generate a large data table, without having to assemble the entire table in memory:
  
                from flask import Response, render_template
                from app.models import Stock

                def generate_stock_table():
                    yield render_template('stock_header.html')
                    for stock in Stock.query.all():
                        yield render_template('stock_row.html', stock=stock)
                    yield render_template('stock_footer.html')

                @app.route('/stock-table')
                def stock_table():
                    return Response(generate_stock_table())
In this example you can see how Flask works with generator functions. A route that returns a streamed response needs to return a Response object that is initialized with the generator function. Flask then takes care of invoking the generator and sending all the partial results as chunks to the client.
For this particular example if you assume Stock.query.all() returns the result of a database query as an iterable, then you can generate a potentially large table one row at a time, so regardless of the number of elements in the query the memory consumption in the Python process will not grow larger and larger due to having to assemble a large response string.

#### Multipart Responses
The table example above generates a traditional page in small portions, with all the parts concatenated into the final document. This is a good example of how to generate large responses, but something a little bit more exciting is to work with real time data.
An interesting use of streaming is to have each chunk replace the previous one in the page, as this enables streams to "play" or animate in the browser window. With this technique you can have each chunk in the stream be an image, and that gives you a cool video feed that runs in the browser!
The secret to implement in-place updates is to use a multipart response. Multipart responses consist of a header that includes one of the multipart content types, followed by the parts, separated by a boundary marker and each having its own part specific content type.
There are several multipart content types for different needs. For the purpose of having a stream where each part replaces the previous part the multipart/x-mixed-replace content type must be used. To help you get an idea of how this looks, here is the structure of a multipart video stream:

        HTTP/1.1 200 OK
        Content-Type: multipart/x-mixed-replace; boundary=frame

        --frame
        Content-Type: image/jpeg

        <jpeg data here>
        --frame
        Content-Type: image/jpeg

        <jpeg data here>
        ...
        
As you see above, the structure is pretty simple. The main Content-Type header is set to multipart/x-mixed-replace and a boundary string is defined. Then each part is included, prefixed by two dashes and the part boundary string in their own line. The parts have their own Content-Type header, and each part can optionally include a Content-Length header with the length in bytes of the part payload, but at least for images browsers are able to deal with the stream without the length.

#### Building a Live Video Streaming Server
There's been enough theory in this article, now it is time to build a complete application that streams live video to web browsers.
There are many ways to stream video to browsers, and each method has its benefits and disadvantages. The method that works well with the streaming feature of Flask is to stream a sequence of independent JPEG pictures. This is called Motion JPEG, and is used by many IP security cameras. This method has low latency, but quality is not the best, since JPEG compression is not very efficient for motion video.
Below you can see a surprisingly simple, yet complete web application that can serve a Motion JPEG stream:

      #!/usr/bin/env python
      from flask import Flask, render_template, Response
      from camera import Camera

      app = Flask(__name__)

      @app.route('/')
      def index():
          return render_template('index.html')

      def gen(camera):
          while True:
              frame = camera.get_frame()
              yield (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

      @app.route('/video_feed')
      def video_feed():
          return Response(gen(Camera()),
                          mimetype='multipart/x-mixed-replace; boundary=frame')

      if __name__ == '__main__':
          app.run(host='0.0.0.0', debug=True)
          
This application imports a Camera class that is in charge of providing the sequence of frames. Putting the camera control portion in a separate module is a good idea in this case, this way the web application remains clean, simple and generic.
The application has two routes. The / route serves the main page, which is defined in the index.html template. Below you can see the contents of this template file:

        <html>
          <head>
            <title>Video Streaming Demonstration</title>
          </head>
          <body>
            <h1>Video Streaming Demonstration</h1>
            <img src="{{ url_for('video_feed') }}">
          </body>
        </html>
        
This is a simple HTML page with just a heading and an image tag. Note that the image tag's srcattribute points to the second route of this application, and this is where the magic happens.
The /video_feed route returns the streaming response. Because this stream returns the images that are to be displayed in the web page, the URL to this route is in the src attribute of the image tag. The browser will automatically keep the image element updated by displaying the stream of JPEG images in it, since multipart responses are supported in most/all browsers (let me know if you find a browser that doesn't like this).
The generator function used in the /video_feed route is called gen(), and takes as an argument an instance of the Camera class. The mimetype argument is set as shown above, with the multipart/x-mixed-replace content type and a boundary set to the string "frame".
The gen() function enters a loop where it continuously returns frames from the camera as response chunks. The function asks the camera to provide a frame by calling the camera.get_frame() method, and then it yields with this frame formatted as a response chunk with a content type of image/jpeg, as shown above.


Obtaining Frames from a Video Camera
Now all that is left is to implement the Camera class, which will have to connect to the camera hardware and download live video frames from it. The nice thing about encapsulating the hardware dependent part of this application in a class is that this class can have different implementations for different people, but the rest of the application remains the same. You can think of this class as a device driver, which provides a uniform implementation regardless of the actual hardware device in use.
The other advantage of having the Camera class separated from the rest of the application is that it is easy to fool the application into thinking there is a camera when in reality there is not, since the camera class can be implemented to emulate a camera without real hardware. In fact, while I was working on this application, the easiest way for me to test the streaming was to do that and not have to worry about the hardware until I had everything else running. Below you can see the simple emulated camera implementation that I used:

    from time import time

    class Camera(object):
        def __init__(self):
            self.frames = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]

        def get_frame(self):
            return self.frames[int(time()) % 3]
This implementation reads three images from disk called 1.jpg, 2.jpg and 3.jpg and then returns them one after another repeatedly, at a rate of one frame per second. The get_frame()method uses the current time in seconds to determine which of the three frames to return at any given moment. Pretty simple, right?
To run this emulated camera I needed to create the three frames. Using gimp I've made the following images:
Video processing
To manage to run the object-detection API in real-time with my webcam, I used the threading and multiprocessing python libraries. A thread is used to read the webcam stream. Frames are put into a queue to be processed by a pool of workers (in which Tensorflow object-detection is running).
For video processing purpose, it is not possible to use threading since all video's frames are read before workers are able to apply object-detection on first ones put in the input queue. Frames which are read when input queue is full are lost. Maybe using a lot of workers and huge queues may resolve the problem (with a prohibitive computational cost).
Another problem with simple queue is that frames are not published in output queue with the same order as in the input queue, due to ever-changing analysis time.
To add my video processing feature, I remove the thread to read frames. Instead, I used the following lines of codes to read frames:

      while True:
       # Check input queue is not full
       if not input_q.full():
       # Read frame and store in input queue
       ret, frame = vs.read()
       if ret: 
       input_q.put((int(vs.get(cv2.CAP_PROP_POS_FRAMES)),frame))
       
If the input queue is not full, the next frame is read from the video stream and put into the queue. Else, nothing is done while a frame is not getting from the input queue.
To address the problem of frame order, I used a priority queue as a second output queue:
1. Frames are read and put into the input queue with their corresponding frame numbers (in fact a python list object is put into the queue).
2. Then, workers take frames from the input queue, treat them and put them into the first output queue (still with their relative frame number).

      while True:
        frame = input_q.get()
      frame_rgb = cv2.cvtColor(frame[1], cv2.COLOR_BGR2RGB)
        output_q.put((frame[0], detect_objects(frame_rgb, sess, detection_graph)))
        
3. If output queue is not empty, frames are extracted and put into the priority queue with their corresponding frame number as a priority number. The size of the priority queue is set, arbitrary, to three times the size of the others queues.

      # Check output queue is not empty
      if not output_q.empty():
        # Recover treated frame in output queue and feed priority queue
        output_pq.put(output_q.get())
        
4. Finally, if output priority queue is not empty, the frame with the highest priority (smallest prior number) is taken (this is the standard priority queue working). If the prior corresponds to the expected frame number, the frame is added to the output video stream (and write if needed), else the frame is put back into the priority queue.

      # Check output priority queue is not empty
      if not output_pq.empty():
        prior, output_frame = output_pq.get()
        if prior > countWriteFrame:
          output_pq.put((prior, output_frame))
        else: 
          countWriteFrame = countWriteFrame + 1    
          # Do something with your frame
          
To stop the process, I check that all queues are empty and that all frames have been extracted from the video stream:

      if((not ret) & input_q.empty() & 
          output_q.empty() & output_pq.empty()):
        break
Start Project
Finally, we use a model to prediction and convert it string result. Than we send it back to the client.
Starting the Keras Server The Flask + Keras server can be started by running:

      $ python app.py
        Running on http://localhost:5000
  
You can now access the Prediction Flask WebApp via  http://127.0.0.1:5000
Firstly you should enter link

    http://localhost:5000/upload
you can upload video
Than you can enter link

    http://localhost:5000/watch
    
Conclusion
In this article, I present how I used web server flask to implement a real-time object-detection project with Tensorflow. I also show you how I have adapted the original python script from Dat Tran to perform video processing with multiprocessing.
I will focus on hurdles I have encountered, and what solutions I have found (or not!). The full code is on my Github.
Thanks you if you read this article from the beginning to end! As you have seen, there are lots of possible improvement with this project. Don't hesitate to give me some feedback, I'm always keen to get advices or comments.

