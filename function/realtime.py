from __future__ import print_function
from utils.app_utils import *
from utils.objDet_utils import *
import multiprocessing
from multiprocessing import Queue, Pool
import cv2

def realtime(detection):
    """
    Read and apply object detection to input real time stream (webcam)
    """

    # If display is off while no number of frames limit has been define: set diplay to on
    if((not detection.get_display()) & (detection.get_num_frames() < 0)):
        print("\nSet display to on\n")
        detection.set_display(1)

    # Set the multiprocessing logger to debug if required
    if detection.get_logger_debug():
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(multiprocessing.SUBDEBUG)

    # Multiprocessing: Init input and output Queue and pool of workers
    input_q = Queue(maxsize=detection.get_queue_size())
    output_q = Queue(maxsize=detection.get_queue_size())
    pool = Pool(detection.get_num_workers(), worker, (input_q,output_q))

    # created a threaded video stream and start the FPS counter
    vs = WebcamVideoStream(src=detection.get_input_device()).start()
    fps = FPS().start()

    # Define the output codec and create VideoWriter object
    if detection.get_output():
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('outputs/{}.avi'.format(detection.get_output_name()),
                              fourcc, vs.getFPS()/detection.get_num_workers(), (vs.getWidth(), vs.getHeight()))


    # Start reading and treating the video stream
    if detection.get_display() > 0:
        print()
        print("=====================================================================")
        print("Starting video acquisition. Press 'q' (on the video windows) to stop.")
        print("=====================================================================")
        print()

    countFrame = 0
    while True:
        # Capture frame-by-frame
        ret, frame = vs.read()
        countFrame = countFrame + 1
        if ret:
            input_q.put(frame)
            output_rgb = cv2.cvtColor(output_q.get(), cv2.COLOR_RGB2BGR)

            # write the f
            #
            # rame
            if detection.get_output():
                out.write(output_rgb)

            # Display the resulting frame
            if detection.get_display():
                ## full screen
                if detection.get_full_screen():
                    cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
                    cv2.setWindowProperty("frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.imshow("frame", output_rgb)

                fps.update()
            elif countFrame >= detection.get_num_frames():
                break

        else:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    fps.stop()
    pool.terminate()
    vs.stop()
    if detection.get_output():
        out.release()
    cv2.destroyAllWindows()

