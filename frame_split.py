import cv2
import threading

def frame(win, chars):
    while not flag.is_set() and cap.isOpened():
        rv, frame = cap.read()
        if rv:
            cv2.imshow(win, frame)
            for c in chars: print(c)
        if cv2.waitKey(1) & 0xff == 27: break
    flag.set() # terminate other threads as well

cap = cv2.VideoCapture(0)
flag = threading.Event()

t1 = threading.Thread(target=frame, args=('win1','a'))
t1.start()
t2 = threading.Thread(target=frame, args=('win2',('b','c')))
t2.start()

t1.join()
t2.join()

cap.release()