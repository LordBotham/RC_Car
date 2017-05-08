import numpy as np
import cv2
import serial
import socket


class CollectTrainingData(object):
    def __init__(self):

        self.server_socket = socket.socket()
        self.server_socket.bind(('', 8000))
        self.server_socket.listen(0)

        # accept a single connection
        self.connection = self.server_socket.accept()[0].makefile('rb')

        # connect to a serial port
        #self.ser = serial.Serial('COM7', 9600, timeout=1)
        self.send_inst = True

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1
        self.temp_label = np.zeros((1, 4), 'float')

        self.collect_image()

    def collect_image(self):

        saved_frame = 0
        total_frame = 0

        # collect images for training
        print 'Start collecting images...'
        e1 = cv2.getTickCount()
        image_array = np.zeros((1, 38400))
        label_array = np.zeros((1, 4), 'float')

        # stream video frames one by one
        try:
            stream_bytes = ' '
            frame = 1
            while self.send_inst:
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find('\xff\xd8')
                last = stream_bytes.find('\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_GRAYSCALE)

                    cimg = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    circles = cv2.HoughCircles(image, cv2.cv.CV_HOUGH_GRADIENT, 1, 1000, param1=100, param2=30,
                                               minRadius=0, maxRadius=30)
                    frame += 1
                    if circles is None:
                        #cv2.imshow('Detected_circles', image)
                        vis = np.concatenate((image, image), axis=1)
                        cv2.imshow('Original and Detcted_circles', vis)
                        cv2.imwrite('training_images/frame{:>05}.jpg'.format(frame), vis)

                        continue

                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        # draw the outer circle
                        cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
                        # draw the center of the circle
                        cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)

                    #cv2.imshow('Detected_circles', cimg)
                    #cv2.imshow('Original', image)
                    image=cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    vis = np.concatenate((image, cimg), axis=1)
                    cv2.imwrite('training_images/frame{:>05}.jpg'.format(frame), vis)
                    cv2.imshow('Original and Detcted_circles', vis)
                    key = cv2.waitKey(20)
                    if key == 27:  # exit on ESC
                        break

                    frame += 1
                    total_frame += 1

        finally:
            self.connection.close()
            self.server_socket.close()


if __name__ == '__main__':
    CollectTrainingData()