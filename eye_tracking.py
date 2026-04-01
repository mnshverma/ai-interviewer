import time
import base64
import json
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass, field, asdict

try:
    import cv2
    import mediapipe as mp
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    mp = None
    np = None
    CV2_AVAILABLE = False


@dataclass
class GazeEvent:
    timestamp: str
    direction: str
    duration: float
    strike_number: int
    screenshot_b64: Optional[str] = None


@dataclass
class EyeTrackingState:
    is_calibrated: bool = False
    baseline_x: float = 0.0
    baseline_y: float = 0.0
    tolerance_x: float = 0.15
    tolerance_y: float = 0.12
    strikes: int = 0
    last_warning_time: float = 0.0
    current_gaze_start: Optional[float] = None
    is_looking_away: bool = False
    events: List[GazeEvent] = field(default_factory=list)
    compliance_score: float = 100.0
    total_tracking_time: float = 0.0
    away_time: float = 0.0
    is_active: bool = False
    is_paused: bool = False
    recalibration_requested: bool = False
    break_approved: bool = False
    break_start_time: Optional[float] = None
    break_duration: float = 60.0


class EyeTracker:
    def __init__(self):
        if not CV2_AVAILABLE:
            self.face_mesh = None
            self.mp_face_mesh = None
            self.mp_drawing = None
            self.mp_drawing_styles = None
            self.left_eye_indices = []
            self.right_eye_indices = []
            self.left_iris_idx = 0
            self.right_iris_idx = 0
            self.blink_counter = 0
            self.blink_start = None
            self.is_blinking = False
            self.consecutive_away_frames = 0
            self.min_away_duration = 1.5
            self.frames_for_away = 45
            self.calibration_samples = []
            self.calibration_frames_needed = 30
            self.ambient_light_threshold = 0.6
            self.last_light_check = time.time()
            self.current_brightness = 1.0
            self.state = EyeTrackingState()
            return
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.state = EyeTrackingState()
        
        self.left_eye_indices = [33, 133, 160, 158, 153, 144, 385, 380, 373, 362]
        self.right_eye_indices = [362, 263, 387, 391, 249, 374, 473, 468, 471, 477]
        self.left_iris_idx = 468
        self.right_iris_idx = 473
        
        self.blink_counter = 0
        self.blink_start = None
        self.is_blinking = False
        
        self.consecutive_away_frames = 0
        self.min_away_duration = 1.5
        self.frames_for_away = 45
        
        self.calibration_samples = []
        self.calibration_frames_needed = 30
        
        self.ambient_light_threshold = 0.6
        self.last_light_check = time.time()
        self.current_brightness = 1.0
        
    def calculate_gaze_ratio(self, eye_points, iris_point, frame_width: int, frame_height: int) -> Tuple[float, float]:
        if not CV2_AVAILABLE:
            return 0.0, 0.0
            
        eye_left = np.array([eye_points[0].x * frame_width, eye_points[0].y * frame_height])
        eye_right = np.array([eye_points[3].x * frame_width, eye_points[3].y * frame_height])
        iris = np.array([iris_point.x * frame_width, iris_point.y * frame_height])
        
        eye_center = (eye_left + eye_right) / 2
        eye_width_vec = eye_right - eye_left
        eye_width = np.linalg.norm(eye_width_vec)
        
        if eye_width < 1e-6:
            return 0.0, 0.0
        
        iris_offset = iris - eye_center
        gaze_x = np.dot(iris_offset, eye_width_vec) / (eye_width * eye_width)
        gaze_x = np.clip(gaze_x, -1.0, 1.0)
        
        vertical_points = [(eye_points[1].x * frame_width, eye_points[1].y * frame_height),
                          (eye_points[5].x * frame_width, eye_points[5].y * frame_height)]
        eye_top = np.array(vertical_points[0])
        eye_bottom = np.array(vertical_points[1])
        eye_height_vec = eye_bottom - eye_top
        eye_height = np.linalg.norm(eye_height_vec)
        
        if eye_height > 1e-6:
            gaze_y = np.dot(iris_offset, eye_height_vec) / (eye_height * eye_height)
            gaze_y = np.clip(gaze_y, -1.0, 1.0)
        else:
            gaze_y = 0.0
        
        return gaze_x, gaze_y
    
    def detect_blink(self, left_eye, right_eye) -> bool:
        if not CV2_AVAILABLE:
            return False
        
        def get_eye_aspect(eye):
            vertical_1 = np.linalg.norm(np.array([eye[1].x - eye[5].x, eye[1].y - eye[5].y]))
            vertical_2 = np.linalg.norm(np.array([eye[2].x - eye[4].x, eye[2].y - eye[4].y]))
            horizontal = np.linalg.norm(np.array([eye[0].x - eye[3].x, eye[0].y - eye[3].y]))
            ear = (vertical_1 + vertical_2) / (2 * horizontal)
            return ear
        
        left_ear = get_eye_aspect(left_eye)
        right_ear = get_eye_aspect(left_eye)
        
        ear = (left_ear + right_ear) / 2
        
        if ear < 0.2:
            if not self.is_blinking:
                self.is_blinking = True
                self.blink_start = time.time()
            return True
        else:
            if self.is_blinking:
                self.blink_counter += 1
                self.is_blinking = False
                self.blink_start = None
            return False
    
    def check_lighting_condition(self, frame) -> bool:
        if not CV2_AVAILABLE:
            return True
            
        current_time = time.time()
        if current_time - self.last_light_check > 2.0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.current_brightness = np.mean(gray) / 255.0
            self.last_light_check = current_time
        return self.current_brightness >= self.ambient_light_threshold
    
    def process_frame(self, frame) -> Dict:
        if not CV2_AVAILABLE or self.face_mesh is None:
            return {"status": "unavailable", "looking_at": "center", "gaze_x": 0, "gaze_y": 0}
        
        if self.state.is_paused or self.state.break_approved:
            if self.state.break_approved and self.state.break_start_time is None:
                self.state.break_start_time = time.time()
            return {"status": "paused", "looking_at": "center", "gaze_x": 0, "gaze_y": 0}
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        if not results.multi_face_landmarks:
            return {"status": "no_face", "looking_at": "unknown", "gaze_x": 0, "gaze_y": 0}
        
        face_landmarks = results.multi_face_landmarks[0]
        h, w = frame.shape[:2]
        
        left_eye = [face_landmarks.landmark[i] for i in self.left_eye_indices]
        right_eye = [face_landmarks.landmark[i] for i in self.right_eye_indices]
        left_iris = face_landmarks.landmark[self.left_iris_idx]
        right_iris = face_landmarks.landmark[self.right_iris_idx]
        
        is_blinking = self.detect_blink(left_eye, right_eye)
        
        gaze_x_left, gaze_y_left = self.calculate_gaze_ratio(left_eye, left_iris, w, h)
        gaze_x_right, gaze_y_right = self.calculate_gaze_ratio(right_eye, right_iris, w, h)
        
        gaze_x = (gaze_x_left + gaze_x_right) / 2
        gaze_y = (gaze_y_left + gaze_y_right) / 2
        
        if self.state.is_calibrated:
            return self._evaluate_gaze(gaze_x, gaze_y, frame, is_blinking)
        else:
            return {"status": "calibrating", "looking_at": "center", "gaze_x": gaze_x, "gaze_y": gaze_y, "is_calibrating": True}
    
    def _evaluate_gaze(self, gaze_x: float, gaze_y: float, frame, is_blinking: bool) -> Dict:
        offset_x = gaze_x - self.state.baseline_x
        offset_y = gaze_y - self.state.baseline_y
        
        looking_at = "center"
        
        if abs(offset_x) > self.state.tolerance_x:
            looking_at = "left" if offset_x < 0 else "right"
        
        current_time = time.time()
        
        if looking_at != "center" and not is_blinking:
            if not self.state.is_looking_away:
                self.state.is_looking_away = True
                self.state.current_gaze_start = current_time
                self.consecutive_away_frames = 1
            else:
                self.consecutive_away_frames += 1
        else:
            if self.state.is_looking_away and self.consecutive_away_frames > 0:
                gaze_duration = current_time - self.state.current_gaze_start
                if gaze_duration >= self.min_away_duration and self.consecutive_away_frames >= self.frames_for_away:
                    self._trigger_warning(looking_at, frame)
                self.state.is_looking_away = False
                self.state.current_gaze_start = None
                self.consecutive_away_frames = 0
            self.consecutive_away_frames = 0
        
        if self.state.is_active:
            self.state.total_tracking_time += 0.1
            if looking_at != "center":
                self.state.away_time += 0.1
        
        return {
            "status": "tracking",
            "looking_at": looking_at,
            "gaze_x": gaze_x,
            "gaze_y": gaze_y,
            "offset_x": offset_x,
            "offset_y": offset_y,
            "is_blinking": is_blinking,
            "is_looking_away": self.state.is_looking_away
        }
    
    def calibrate(self, frame) -> bool:
        if not CV2_AVAILABLE or self.face_mesh is None:
            return True
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        if not results.multi_face_landmarks:
            return False
        
        face_landmarks = results.multi_face_landmarks[0]
        h, w = frame.shape[:2]
        
        left_eye = [face_landmarks.landmark[i] for i in self.left_eye_indices]
        right_eye = [face_landmarks.landmark[i] for i in self.right_eye_indices]
        left_iris = face_landmarks.landmark[self.left_iris_idx]
        right_iris = face_landmarks.landmark[self.right_iris_idx]
        
        gaze_x_left, gaze_y_left = self.calculate_gaze_ratio(left_eye, left_iris, w, h)
        gaze_x_right, gaze_y_right = self.calculate_gaze_ratio(right_eye, right_iris, w, h)
        
        gaze_x = (gaze_x_left + gaze_x_right) / 2
        gaze_y = (gaze_y_left + gaze_y_right) / 2
        
        self.calibration_samples.append((gaze_x, gaze_y))
        
        if len(self.calibration_samples) >= self.calibration_frames_needed:
            avg_x = np.mean([s[0] for s in self.calibration_samples])
            avg_y = np.mean([s[1] for s in self.calibration_samples])
            
            self.state.baseline_x = avg_x
            self.state.baseline_y = avg_y
            self.state.is_calibrated = True
            self.calibration_samples = []
            return True
        
        return False
    
    def _trigger_warning(self, direction: str, frame):
        current_time = time.time()
        
        if current_time - self.state.last_warning_time < 3.0:
            return
        
        self.state.strikes += 1
        self.state.last_warning_time = current_time
        
        if CV2_AVAILABLE:
            _, buffer = cv2.imencode('.jpg', frame)
            screenshot_b64 = base64.b64encode(buffer).decode('utf-8')
        else:
            screenshot_b64 = None
        
        event = GazeEvent(
            timestamp=datetime.now().isoformat(),
            direction=direction,
            duration=1.5,
            strike_number=self.state.strikes,
            screenshot_b64=screenshot_b64
        )
        self.state.events.append(event)
        
        if self.state.strikes >= 4:
            self._terminate_interview()
    
    def _terminate_interview(self):
        self.state.is_active = False
        event = GazeEvent(
            timestamp=datetime.now().isoformat(),
            direction="terminated",
            duration=0,
            strike_number=4,
            screenshot_b64=None
        )
        self.state.events.append(event)
    
    def calculate_compliance_score(self) -> float:
        if self.state.total_tracking_time > 0:
            compliance_ratio = 1.0 - (self.state.away_time / self.state.total_tracking_time)
            self.state.compliance_score = max(0, min(100, compliance_ratio * 100))
        return self.state.compliance_score
    
    def request_recalibration(self):
        self.state.recalibration_requested = True
        self.state.is_calibrated = False
        self.calibration_samples = []
    
    def request_break(self, duration_seconds: int = 60):
        return {
            "break_requested": True,
            "duration": duration_seconds,
            "reason": "User requested break"
        }
    
    def approve_break(self, duration_seconds: int = 60):
        self.state.break_approved = True
        self.state.break_start_time = time.time()
        self.state.break_duration = float(duration_seconds)
    
    def end_break(self):
        if self.state.break_approved and self.state.break_start_time:
            elapsed = time.time() - self.state.break_start_time
            if elapsed >= self.state.break_duration:
                self.state.break_approved = False
                self.state.break_start_time = None
    
    def generate_report(self) -> Dict:
        self.calculate_compliance_score()
        
        return {
            "is_calibrated": self.state.is_calibrated,
            "strikes": self.state.strikes,
            "compliance_score": round(self.state.compliance_score, 2),
            "total_tracking_time": round(self.state.total_tracking_time, 2),
            "away_time": round(self.state.away_time, 2),
            "total_events": len(self.state.events),
            "events": [asdict(e) for e in self.state.events],
            "break_approved": self.state.break_approved
        }
    
    def reset(self):
        self.state = EyeTrackingState()
        self.calibration_samples = []
        self.consecutive_away_frames = 0
        self.blink_counter = 0
    
    def get_warning_info(self) -> Optional[Dict]:
        if self.state.strikes == 0:
            return None
        
        warnings = {
            1: {
                "message": "Please keep your eyes on the screen. This is your first warning.",
                "icon": "⚠️",
                "sound": "soft_chime"
            },
            2: {
                "message": "Warning: Looking away from the screen is considered cheating. One more violation and your interview may be terminated.",
                "icon": "🚨",
                "sound": "louder_alert"
            },
            3: {
                "message": "Final Warning Detected. If you look away from the screen again, your interview will be immediately stopped and your session will be permanently terminated. No further chances will be given.",
                "icon": "🛑",
                "sound": "harsh_buzzer"
            },
            4: {
                "message": "Interview Terminated. You have been flagged for repeated eye-tracking violations.",
                "icon": "❌",
                "sound": "termination"
            }
        }
        
        return warnings.get(self.state.strikes, None)
