import datetime
import time

import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

detection = False
detection_stopped_time = None
timer_started = False
motion_counter = 0
SECONDS_TO_RECORD_AFTER_DETECTION = 5

frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

_, start_frame = cap.read()
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)


while True:
    _, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)
    difference = cv2.absdiff(gray_blur, start_frame)
    threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
    start_frame = gray_blur

    if threshold.sum() > 300:
        if not detection:
            motion_counter += 1
    else:
        if motion_counter > 0:
            if not detection:
                motion_counter -= 1

    print(motion_counter)

    if motion_counter > 20:
        if detection:
            timer_started = False
        else:
            detection = True
            motion_counter = 0
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(f"{current_time}.mp4", fourcc, 15, frame_size)
            print("Started Recording!")
    elif detection:
        if timer_started:
            if (
                time.time() - detection_stopped_time
                >= SECONDS_TO_RECORD_AFTER_DETECTION
            ):
                detection = False
                timer_started = False
                out.release()
                print("Stop Recording!")
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        out.write(frame)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == ord("q"):
        break

out.release()
cap.release()
cv2.destroyAllWindows()
