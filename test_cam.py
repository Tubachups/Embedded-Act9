# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/set-up-usb-camera-opencv-raspberry-pi/

import cv2
import time  # <-- 1. Import the time module

video_capture = cv2.VideoCapture(0)

# 2. Used to record the time when we processed the last frame
prev_frame_time = 0
# 2. Used to record the time when we processing the current frame
new_frame_time = 0

while True:
    result, video_frame = video_capture.read()  # read frames from the video
    if result is False:
        break  # terminate the loop if the frame is not read successfully

    # --- Start of FPS Calculation ---
    # 3. Get the current time
    new_frame_time = time.time()

    # 3. Calculate the FPS
    # We check for division by zero, which can happen in the first frame
    if (new_frame_time - prev_frame_time) > 0:
        fps = 1 / (new_frame_time - prev_frame_time)
    else:
        fps = 0
        
    prev_frame_time = new_frame_time

    # 3. Convert the FPS to an integer and then a string
    fps_text = f"FPS: {int(fps)}"
    # --- End of FPS Calculation ---


    # 4. Put the FPS text on the video frame
    cv2.putText(
        video_frame,
        fps_text,
        (10, 30),  # Position (bottom-left corner)
        cv2.FONT_HERSHEY_SIMPLEX,  # Font type
        1,  # Font scale
        (0, 255, 0),  # BGR color (green)
        2,  # Line thickness
        cv2.LINE_AA  # Line type
    )

    cv2.imshow(
        "USB Camera Test", video_frame  # Display the frame with FPS
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()