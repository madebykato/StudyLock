import cv2
import winsound
import time
import threading

class FocusDetector:
    def __init__(self, camera_index=0, alarm_after_seconds=5):
        self.camera_index = camera_index
        self.alarm_after_seconds = alarm_after_seconds

        self.camera = None
        self.running = False
        self.eyes_detected = False
        self.eyes_missing_start = None
        self.focused_frames = 0
        self.total_frames = 0
        self.alarm_active = False
        self.alarm_thread = None
# სახის დეტექტორი
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
# თვალების დეტექტორი
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

    def alarm_loop(self):
        while self.alarm_active:
            winsound.Beep(1000, 500)
            time.sleep(0.1)

    def start_alarm(self):
        if not self.alarm_active:
            self.alarm_active = True
            self.alarm_thread = threading.Thread(
                target=self.alarm_loop,
                daemon=True
            )
            self.alarm_thread.start()

    def stop_alarm(self):
        self.alarm_active = False

    def is_user_present(self):
        return self.eyes_detected

    def get_focus_score(self):
        if self.total_frames == 0:
            return 0
        return int((self.focused_frames / self.total_frames) * 100)

    def reset_focus_score(self):
        self.focused_frames = 0
        self.total_frames = 0

    def get_total_frames(self):
        return self.total_frames

    def get_focused_frames(self):
        return self.focused_frames

    def stop_detection(self):
        self.running = False
        self.stop_alarm()

    def start_detection(self):
        self.camera = cv2.VideoCapture(self.camera_index)
        self.running = True

        while self.running:
            success, frame = self.camera.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            self.eyes_detected = False
            status = "Eyes could not be detected"

            for (x, y, w, h) in faces:
                face_gray = gray[y:y + h, x:x + w]
                face_color = frame[y:y + h, x:x + w]
                eyes = self.eye_cascade.detectMultiScale(face_gray)
                if len(eyes) >= 1:
                    self.eyes_detected = True
                    status = "Eyes are detected"

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (255, 0, 0),
                    2
                )

                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(
                        face_color,
                        (ex, ey),
                        (ex + ew, ey + eh),
                        (0, 255, 0),
                        2
                    )

            self.total_frames += 1
            if self.eyes_detected:
                self.focused_frames += 1
                self.eyes_missing_start = None
                self.stop_alarm()

            else:
                if self.eyes_missing_start is None:
                    self.eyes_missing_start = time.time()
                elapsed = time.time() - self.eyes_missing_start

                if elapsed > self.alarm_after_seconds:
                    status = "LOCK IN"
                    self.start_alarm()

            focus_score = self.get_focus_score()

            cv2.putText(
                frame,
                status,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0) if self.eyes_detected else (0, 0, 255),
                2
            )

            cv2.putText(
                frame,
                f"Focus Score: {focus_score}%",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

            cv2.imshow("StudyLock Focus Detector", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                self.stop_detection()
        self.stop_alarm()
        
        if self.camera is not None:
            self.camera.release()

        cv2.destroyAllWindows()
        cv2.waitKey(1)