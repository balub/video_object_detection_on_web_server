### Object Detection in Video and Streaming Web Server

In this article, I will present how I managed to use Tensorflow Object-detection API to perform both real-time (webcam) and video post-processing. I used OpenCV with python3 multiprocessing and multi-threading libraries. And This article is dedicated to streaming, an interesting feature that gives Flask applications the ability to provide large responses efficiently partitioned in small chunks, potentially over a long period of time. To illustrate the topic I'm going to show you how to build a live video streaming server!

####  What is Streaming?
Streaming is a technique in which the server provides the response to a request in chunks. I can think of a couple of reasons why this might be useful:
Very large responses. Having to assemble a response in memory only to return it to the client can be inefficient for very large responses. An alternative would be to write the response to disk and then return the file with flask.send_file(), but that adds I/O to the mix. Providing the response in small portions is a much better solution, assuming the data can be generated in chunks.
Real time data. For some applications a request may need to return data that comes from a real time source. A pretty good example of this is a real time video or audio feed. A lot of security cameras use this technique to stream video to web browsers.
