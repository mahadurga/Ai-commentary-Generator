import numpy as np
import logging
from .pose_estimation import get_pose_features

logger = logging.getLogger(__name__)

# Define common cricket shots for classification
CRICKET_SHOTS = [
    "straight drive",
    "cover drive",
    "cut shot",
    "pull shot",
    "hook shot",
    "sweep shot",
    "defensive shot",
    "flick shot",
    "square drive",
    "on drive"
]

# Basic rules for shot classification based on pose features
# In a real implementation, this would use a trained ML model or more sophisticated logic
SHOT_RULES = {
    "straight drive": {
        "right_elbow_angle": (140, 180),
        "left_elbow_angle": (90, 140),
        "posture": "upright",
        "description": "A classic shot played with a straight bat, hitting the ball back past the bowler."
    },
    "cover drive": {
        "right_elbow_angle": (120, 160),
        "left_elbow_angle": (100, 150),
        "posture": "leaning_right",
        "description": "An elegant shot played through the off side, between mid-off and point."
    },
    "cut shot": {
        "right_elbow_angle": (90, 130),
        "left_elbow_angle": (100, 150),
        "posture": "upright",
        "description": "A horizontal bat shot played to a short, wide delivery, cutting the ball toward point."
    },
    "pull shot": {
        "right_elbow_angle": (80, 120),
        "left_elbow_angle": (70, 110),
        "posture": "leaning_back",
        "description": "A shot played to a short-pitched delivery, pulling the ball to the leg side."
    },
    "hook shot": {
        "right_elbow_angle": (70, 110),
        "left_elbow_angle": (60, 100),
        "posture": "leaning_back",
        "description": "Similar to the pull but played to a higher bouncing ball, hooking it around to the leg side."
    },
    "sweep shot": {
        "right_knee_angle": (60, 120),
        "left_knee_angle": (60, 100),
        "posture": "kneeling",
        "description": "A shot played on one knee, sweeping the ball to the leg side, usually against spin bowling."
    },
    "defensive shot": {
        "right_elbow_angle": (150, 180),
        "left_elbow_angle": (130, 170),
        "posture": "upright",
        "description": "A defensive stroke played with a straight bat to block the ball."
    },
    "flick shot": {
        "right_knee_angle": (100, 150),
        "left_knee_angle": (100, 160),
        "posture": "upright",
        "description": "A wristy shot played off the pads, flicking the ball to the leg side."
    },
    "square drive": {
        "right_elbow_angle": (110, 150),
        "left_elbow_angle": (100, 140),
        "posture": "upright",
        "description": "A drive played square of the wicket on the off side."
    },
    "on drive": {
        "right_elbow_angle": (130, 170),
        "left_elbow_angle": (100, 150),
        "posture": "leaning_left",
        "description": "A drive played through the on side, between mid-on and mid-wicket."
    }
}

def classify_shot(pose, previous_poses=[]):
    """
    Classify the cricket shot based on the player's pose.
    
    Args:
        pose (dict): Current pose with keypoints
        previous_poses (list): Previous poses for tracking movement
        
    Returns:
        str: Classified cricket shot or None if no shot detected
    """
    # Extract features from the pose
    features = get_pose_features(pose)
    
    # Determine posture based on features
    posture = determine_posture(features)
    
    # Calculate motion if previous poses are available
    motion = calculate_motion(pose, previous_poses) if previous_poses else None
    
    # Simple rule-based classification for demonstration
    # In a real implementation, this would use a trained ML model
    
    shot_scores = {}
    
    for shot_name, shot_rules in SHOT_RULES.items():
        score = 0
        
        # Check angle conditions
        for angle_name, (min_angle, max_angle) in shot_rules.items():
            if angle_name in features and min_angle <= features[angle_name] <= max_angle:
                score += 1
        
        # Check posture
        if "posture" in shot_rules and posture == shot_rules["posture"]:
            score += 2
        
        # Use motion information if available
        if motion and motion["is_swing"]:
            if shot_name in ["straight drive", "cover drive", "on drive"] and motion["direction"] == "forward":
                score += 2
            elif shot_name in ["cut shot", "square drive"] and motion["direction"] == "sideways":
                score += 2
            elif shot_name in ["pull shot", "hook shot"] and motion["direction"] == "backward":
                score += 2
        
        shot_scores[shot_name] = score
    
    # Find the shot with the highest score
    max_score = max(shot_scores.values()) if shot_scores else 0
    best_shots = [shot for shot, score in shot_scores.items() if score == max_score]
    
    # Only return a shot if the score is above a threshold
    if max_score >= 2 and best_shots:
        # Return the first best shot
        return best_shots[0]
    
    return None

def determine_posture(features):
    """
    Determine the player's posture based on pose features.
    
    Args:
        features (dict): Features extracted from the pose
        
    Returns:
        str: Detected posture
    """
    # This is a simplified version - a real implementation would be more sophisticated
    
    # Check if the player is leaning to one side
    if "nose_x_rel" in features and "neck_x_rel" in features:
        lean = features["nose_x_rel"] - features["neck_x_rel"]
        if lean > 20:
            return "leaning_right"
        elif lean < -20:
            return "leaning_left"
    
    # Check if player is leaning back
    if "nose_y_rel" in features and "neck_y_rel" in features:
        vertical_lean = features["nose_y_rel"] - features["neck_y_rel"]
        if vertical_lean < -15:
            return "leaning_back"
    
    # Check if player is in a kneeling position
    if "right_knee_angle" in features and features["right_knee_angle"] < 90:
        return "kneeling"
    if "left_knee_angle" in features and features["left_knee_angle"] < 90:
        return "kneeling"
    
    # Default to upright posture
    return "upright"

def calculate_motion(current_pose, previous_poses, window_size=5):
    """
    Calculate motion of the player based on pose history.
    
    Args:
        current_pose (dict): Current pose with keypoints
        previous_poses (list): Previous poses for tracking movement
        window_size (int): Number of previous frames to consider
        
    Returns:
        dict: Motion information including direction and if it's a swing
    """
    # Use a limited window of previous poses
    poses_window = previous_poses[-window_size:] if len(previous_poses) > window_size else previous_poses
    
    # Track movement of hands to detect swing
    if "right_wrist" in current_pose["keypoints"] and poses_window:
        current_wrist = current_pose["keypoints"]["right_wrist"][:2]
        
        # Check if previous poses have right_wrist
        prev_wrists = []
        for prev_pose in poses_window:
            if "right_wrist" in prev_pose["keypoints"]:
                prev_wrists.append(prev_pose["keypoints"]["right_wrist"][:2])
        
        if prev_wrists:
            # Calculate total displacement
            start_wrist = prev_wrists[0]
            dx = current_wrist[0] - start_wrist[0]
            dy = current_wrist[1] - start_wrist[1]
            
            # Determine direction of movement
            direction = "none"
            if abs(dx) > 30 or abs(dy) > 30:  # Threshold for significant movement
                if abs(dx) > abs(dy):
                    direction = "sideways"
                else:
                    direction = "forward" if dy > 0 else "backward"
            
            # Check if this is a swing motion
            is_swing = False
            if len(prev_wrists) >= 3:
                # Calculate acceleration (change in velocity)
                velocities = []
                for i in range(1, len(prev_wrists)):
                    vx = prev_wrists[i][0] - prev_wrists[i-1][0]
                    vy = prev_wrists[i][1] - prev_wrists[i-1][1]
                    velocities.append((vx, vy))
                
                # Check for sign change in velocity (acceleration)
                if len(velocities) >= 2:
                    for i in range(1, len(velocities)):
                        if (velocities[i][0] * velocities[i-1][0] < 0 or 
                            velocities[i][1] * velocities[i-1][1] < 0):
                            is_swing = True
                            break
            
            return {
                "direction": direction,
                "displacement": (dx, dy),
                "is_swing": is_swing
            }
    
    return {
        "direction": "none",
        "displacement": (0, 0),
        "is_swing": False
    }
