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

