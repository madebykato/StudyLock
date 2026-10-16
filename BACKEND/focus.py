import cv2
import time
import threading
import os
from datetime import datetime
import mediapipe as mp
from BACKEND.sessions import SessionsManager

class FocusDetector:
    MODES = {
        "soft": 15, # after 15s, alarm
        "normal": 10, #after 10s, alarm
        "hard": 5 #after 5s, alarm
    }

    def __init__(
        self,
        camera_index=0,
        mode="normal",
        blink_threshold=0.45,
        blink_grace_seconds=0.8,
        model_path="face_landmarker.task"
    ):
        self.camera_index = camera_index
        self.mode = mode.lower()
        self.blink_threshold = blink_threshold
        self.blink_grace_seconds = blink_grace_seconds
        self.model_path = model_path
        self.stop_requested = False

        if self.mode not in self.MODES:
            self.mode = "normal"

        self.alarm_after_seconds = self.MODES[self.mode]

        self.sessions_manager = SessionsManager()

        self.alarm_active = False
        self.alarm_thread = None

    def request_stop(self):
        self.stop_requested = True
        self.stop_alarm()

    def set_mode(self, mode):
        mode = mode.lower()

        if mode not in self.MODES:
            raise ValueError("Mode must be soft, normal, or hard.")

        self.mode = mode
        self.alarm_after_seconds = self.MODES[mode]

    def find_model_path(self):
        possible_paths = [
            self.model_path,
            os.path.join(os.getcwd(), self.model_path),
            os.path.join(os.path.dirname(__file__), self.model_path),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), self.model_path)
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        raise FileNotFoundError(
            "face_landmarker.task not found. Put it in the main StudyLock folder."
        )

    def get_blendshape_score(self, blendshapes, name):
        for category in blendshapes:
            if category.category_name == name:
                return category.score
        return 0

    def check_focus_status(self, result):
        if not result.face_landmarks or not result.face_blendshapes:
            return False, "No face detected", 0

        blendshapes = result.face_blendshapes[0]

        left_blink = self.get_blendshape_score(blendshapes, "eyeBlinkLeft")
        right_blink = self.get_blendshape_score(blendshapes, "eyeBlinkRight")

        average_blink = (left_blink + right_blink) / 2

        if average_blink >= self.blink_threshold:
            return False, "Eyes closed", average_blink

        return True, "Focused", average_blink

    def start_alarm(self):
        if self.alarm_active:
            return

        self.alarm_active = True
        self.alarm_thread = threading.Thread(
            target=self.alarm_loop,
            daemon=True
        )
        self.alarm_thread.start()

    def stop_alarm(self):
        self.alarm_active = False

    def alarm_loop(self):
        while self.alarm_active:
            try:
                import winsound
                winsound.Beep(1000, 500)
            except Exception:
                print("\a", end="")

            time.sleep(0.2)

    def create_landmarker(self):
        model_path = self.find_model_path()

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_faces=1,
            output_face_blendshapes=True
        )

        return FaceLandmarker.create_from_options(options)

    def run_focus_session(
        self,
        user_id,
        duration_minutes=None,
        keep_on_top=False
    ):
        if user_id is None:
            raise ValueError("User ID is required.")

        landmarker = self.create_landmarker()
        camera = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

        if not camera.isOpened():
            landmarker.close()
            raise RuntimeError("Camera could not be opened.")

        window_name = "StudyLock Focus Mode"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        started_at = datetime.now()
        start_time = time.time()
        last_frame_time = start_time

        focused_seconds = 0
        distracted_seconds = 0
        continuous_distraction_start = None

        last_timestamp_ms = 0

        try:
            self.stop_requested = False
            
            while True:
                if self.stop_requested:
                    break

                success, frame = camera.read()

                if not success:
                    break

                now = time.time()
                delta = now - last_frame_time
                last_frame_time = now

                elapsed_seconds = now - start_time

                if duration_minutes is not None:
                    if elapsed_seconds >= duration_minutes * 60:
                        break

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame
                )

                timestamp_ms = int(elapsed_seconds * 1000)

                if timestamp_ms <= last_timestamp_ms:
                    timestamp_ms = last_timestamp_ms + 1

                last_timestamp_ms = timestamp_ms

                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                focused, status, blink_score = self.check_focus_status(result)

                if focused:
                    focused_seconds += delta
                    continuous_distraction_start = None
                    self.stop_alarm()
                    color = (0, 255, 0)
                    warning = "Locked in"

                else:
                    if continuous_distraction_start is None:
                        continuous_distraction_start = now

                    continuous_distraction_time = now - continuous_distraction_start

                    is_normal_blink = (
                        status == "Eyes closed"
                        and continuous_distraction_time < self.blink_grace_seconds
                    )

                    if is_normal_blink:
                        focused_seconds += delta
                        color = (0, 255, 255)
                        warning = "Blink detected"
                    else:
                        distracted_seconds += delta
                        color = (0, 0, 255)

                        warning = (
                            f"Distracted: {int(continuous_distraction_time)}s "
                            f"/ Alarm: {self.alarm_after_seconds}s"
                        )

                        if continuous_distraction_time >= self.alarm_after_seconds:
                            self.start_alarm()

                total_tracked_seconds = focused_seconds + distracted_seconds

                if total_tracked_seconds == 0:
                    live_focus_score = 0
                else:
                    live_focus_score = round(
                        (focused_seconds / total_tracked_seconds) * 100,
                        1
                    )

                cv2.putText(
                    frame,
                    f"Mode: {self.mode.upper()}",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    status,
                    (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    color,
                    2
                )

                cv2.putText(
                    frame,
                    warning,
                    (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )

                cv2.putText(
                    frame,
                    f"Blink: {blink_score:.2f}",
                    (30, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Focus score: {live_focus_score}%",
                    (30, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Press ESC to end session",
                    (30, frame.shape[0] - 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(window_name, frame)

                if keep_on_top:
                    try:
                        cv2.setWindowProperty(
                            window_name,
                            cv2.WND_PROP_TOPMOST,
                            1
                        )
                    except Exception:
                        pass

                key = cv2.waitKey(1) & 0xFF

                if key == 27:
                    break

        finally:
            ended_at = datetime.now()
            self.stop_alarm()
            camera.release()
            landmarker.close()
            cv2.destroyAllWindows()

        total_seconds = focused_seconds + distracted_seconds

        if total_seconds == 0:
            final_focus_score = 0
        else:
            final_focus_score = round((focused_seconds / total_seconds) * 100, 1)

        duration_seconds = time.time() - start_time
        saved_duration_minutes = max(round(duration_seconds / 60), 1)

        distracted_seconds = round(distracted_seconds, 1)

        session_id = self.sessions_manager.add_focus_session(
            user_id=user_id,
            duration_minutes=saved_duration_minutes,
            focus_score=final_focus_score,
            distracted_seconds=distracted_seconds,
            started_at=started_at.strftime("%Y-%m-%d %H:%M:%S"),
            ended_at=ended_at.strftime("%Y-%m-%d %H:%M:%S"),
            session_date=started_at.strftime("%Y-%m-%d")
        )

        return {
            "session_id": session_id,
            "mode": self.mode,
            "duration_minutes": saved_duration_minutes,
            "focus_score": final_focus_score,
            "distracted_seconds": distracted_seconds,
            "alarm_after_seconds": self.alarm_after_seconds
        }