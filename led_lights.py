import cv2

THRESHOLD_LOW_RED = (90, 100, 200);
THRESHOLD_HIGH_RED = (150, 155, 255);
THRESHOLD_LOW_GREEN = (100, 150, 0);
THRESHOLD_HIGH_GREEN = (150, 255, 90);


# Minimum required radius of enclosing circle of contour
MIN_RADIUS = 1
frame=1

def img_binary(img,THRESHOLD_LOW,THRESHOLD_HIGH):
    return cv2.inRange(img, THRESHOLD_LOW, THRESHOLD_HIGH)

def mask_maker(img,org_binary,iterations,color):
    img_binary=cv2.dilate(org_binary, None, iterations)
    img_contours = img_binary.copy()
    contours = cv2.findContours(img_contours, cv2.RETR_EXTERNAL, \
                                cv2.CHAIN_APPROX_SIMPLE)[-2]

    # Find the largest contour and use it to compute the min enclosing circle
    center = None
    radius = 0
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M["m00"] > 0:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius < MIN_RADIUS:
                center = None

    # Draw a green circle around the largest enclosed contour
    if center != None:
        cv2.circle(img, center, int(round(radius)), color)
    return x,y

while True:

    # Get image from camera
    img = cv2.imread('new_images/frame{:>05}.jpg'.format(frame))
    frame += 1
    # Blur image to remove noise
    img_filter = cv2.GaussianBlur(img.copy(), (3, 3), 0)

    img_binary_green =img_binary(img_filter.copy(), THRESHOLD_LOW_GREEN, THRESHOLD_HIGH_GREEN)
    img_binary_red = img_binary(img_filter.copy(), THRESHOLD_LOW_RED, THRESHOLD_HIGH_RED)

    if img_binary_green.any():
        x,y=mask_maker(img,img_binary_green,1,(0,255,0))
        cv2.putText(img, 'Go', (int(x) + 5, int(y) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    elif img_binary_red.any():
        x,y = mask_maker(img, img_binary_red, 1,(0,0,255))
        cv2.putText(img, 'Stop', (int(x) + 5, int(y) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # Show image windows
    cv2.imshow('webcam', img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    cv2.waitKey(1)
