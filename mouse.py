import cv2
import mediapipe as mp
import pyautogui

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

prev_x, prev_y = 0, 0
smooth_factor = 2.5
TIP_IDS = [4, 8, 12, 16, 20]

def count_raised_fingers(landmarks):
    fingers = []
    
    # الإبهام
    if landmarks[TIP_IDS[0]].x < landmarks[TIP_IDS[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)
        
    for tip_id in TIP_IDS[1:]:
        if landmarks[tip_id].y < landmarks[tip_id - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
            
    return fingers

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = hand_landmarks.landmark
            fingers = count_raised_fingers(landmarks)
            total_fingers = sum(fingers)
            
            index_finger = landmarks[8]
            
            if fingers[1] == 1 and total_fingers == 1:
                target_x = int(index_finger.x * screen_w)
                target_y = int(index_finger.y * screen_h)
                
                curr_x = prev_x + (target_x - prev_x) / smooth_factor
                curr_y = prev_y + (target_y - prev_y) / smooth_factor
                
                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y
                cv2.putText(frame, "Mode: Moving Mouse", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            elif fingers[1] == 1 and fingers[2] == 1 and total_fingers == 2:
                pyautogui.click()
                cv2.putText(frame, "Action: CLICK", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            elif total_fingers == 4:
                pyautogui.scroll(150)
                cv2.putText(frame, "Action: SCROLL UP", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            elif total_fingers == 5:
                pyautogui.scroll(-150)
                cv2.putText(frame, "Action: SCROLL DOWN", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 2)

    cv2.imshow("Simplified Gesture Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
