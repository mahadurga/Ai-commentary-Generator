import numpy as np
import logging
import cv2
from collections import deque

logger = logging.getLogger(__name__)

# Define cricket field regions
FIELD_REGIONS = {
    "boundary": {
        "description": "The outer edge of the cricket field"
    },
    "pitch": {
        "description": "The central strip where the ball is bowled"
    },
    "stumps": {
        "description": "The three vertical posts that form the wicket"
    },
    "crease": {
        "description": "The lines marking the batsman's safe ground"
    }
}

class BallTracker:
    """Class to track the cricket ball and detect events"""
    
    def __init__(self, max_history=30):
        self.positions = deque(maxlen=max_history)
        self.velocities = deque(maxlen=max_history-1)
        self.accelerations = deque(maxlen=max_history-2)
        self.last_event = None
        self.last_event_frame = -100  # Avoid multiple detections
    
    def update(self, ball_position, frame_num):
        """
        Update ball tracking with a new position.
        
        Args:
            ball_position (tuple): x, y coordinates of the ball
            frame_num (int): Current frame number
        """
        if ball_position:
            self.positions.append((ball_position, frame_num))
            
            # Calculate velocity if we have at least two positions
            if len(self.positions) >= 2:
                p1, f1 = self.positions[-2]
                p2, f2 = self.positions[-1]
                
                # Calculate displacement
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                
                # Calculate frame difference
                df = f2 - f1
                
                # Calculate velocity (pixels per frame)
                vx = dx / df if df > 0 else 0
                vy = dy / df if df > 0 else 0
                
                self.velocities.append((vx, vy, f2))
            
            # Calculate acceleration if we have at least two velocities
            if len(self.velocities) >= 2:
                v1, _, f1 = self.velocities[-2]
                v2, _, f2 = self.velocities[-1]
                
                # Calculate velocity change
                dvx = v2[0] - v1[0]
                dvy = v2[1] - v1[1]
                
                # Calculate frame difference
                df = f2 - f1
                
                # Calculate acceleration (velocity change per frame)
                ax = dvx / df if df > 0 else 0
                ay = dvy / df if df > 0 else 0
                
                self.accelerations.append((ax, ay, f2))
    
    def detect_events(self, frame, objects, current_frame, timestamp):
        """
        Detect cricket events based on ball tracking and other objects.
        
        Args:
            frame (numpy.ndarray): Current video frame
            objects (list): Detected objects in the frame
            current_frame (int): Current frame number
            timestamp (float): Current timestamp in seconds
            
        Returns:
            list: Detected events
        """
        events = []
        
        # Check if we have enough data for event detection
        if len(self.positions) < 5:
            return events
        
        # Skip if too close to last event
        if self.last_event_frame is not None and current_frame - self.last_event_frame < 30:
            return events
        
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # Extract ball positions
        recent_positions = [pos for pos, _ in self.positions]
        
        # Check for boundary event
        if self.is_boundary(recent_positions, width, height):
            events.append({
                'type': 'boundary',
                'subtype': 'four' if self.is_along_ground(recent_positions) else 'six',
                'confidence': 0.8,
                'timestamp': timestamp,
                'frame': current_frame
            })
            self.last_event = 'boundary'
            self.last_event_frame = current_frame
        
        # Check for wicket event
        stumps_objects = [obj for obj in objects if obj['class'] == 'stumps']
        if stumps_objects and self.is_wicket(recent_positions, stumps_objects):
            events.append({
                'type': 'wicket',
                'subtype': 'bowled',  # Simplified - real system would classify different types
                'confidence': 0.7,
                'timestamp': timestamp,
                'frame': current_frame
            })
            self.last_event = 'wicket'
            self.last_event_frame = current_frame
        
        # Check for a played shot event
        if self.is_shot_played(recent_positions):
            events.append({
                'type': 'shot_played',
                'subtype': 'generic',  # The shot classifier would provide the specific type
                'confidence': 0.6,
                'timestamp': timestamp,
                'frame': current_frame
            })
            self.last_event = 'shot_played'
            self.last_event_frame = current_frame
        
        return events
    
    def is_boundary(self, positions, width, height):
        """
        Check if the ball has reached the boundary.
        
        Args:
            positions (list): Recent ball positions
            width (int): Frame width
            height (int): Frame height
            
        Returns:
            bool: True if boundary event detected
        """
        # Define boundary region (near edges of frame)
        boundary_margin = 50  # pixels from edge
        
        # Check if ball position is near the boundary
        latest_pos = positions[-1]
        if (latest_pos[0] < boundary_margin or 
            latest_pos[0] > width - boundary_margin or
            latest_pos[1] < boundary_margin or
            latest_pos[1] > height - boundary_margin):
            
            # Check if the ball was moving toward the boundary
            if len(positions) >= 3:
                direction_x = positions[-1][0] - positions[-3][0]
                direction_y = positions[-1][1] - positions[-3][1]
                
                # Calculate distance to nearest edge
                distance_to_left = latest_pos[0]
                distance_to_right = width - latest_pos[0]
                distance_to_top = latest_pos[1]
                distance_to_bottom = height - latest_pos[1]
                
                min_distance = min(distance_to_left, distance_to_right, 
                                  distance_to_top, distance_to_bottom)
                
                # Check if ball was moving toward the nearest edge
                if (min_distance == distance_to_left and direction_x < 0) or \
                   (min_distance == distance_to_right and direction_x > 0) or \
                   (min_distance == distance_to_top and direction_y < 0) or \
                   (min_distance == distance_to_bottom and direction_y > 0):
                    return True
        
        return False
    
    def is_along_ground(self, positions):
        """
        Check if the ball was traveling along the ground (for four) or in the air (for six).
        
        Args:
            positions (list): Recent ball positions
            
        Returns:
            bool: True if ball was along ground, False if in air
        """
        # This is a simplified implementation
        # A real system would use 3D tracking or estimate based on trajectory
        
        # Check vertical component of trajectory
        if len(positions) >= 5:
            # Get y-coordinates
            y_values = [pos[1] for pos in positions[-5:]]
            
            # Check if y values are relatively stable (along ground)
            y_var = np.var(y_values)
            return y_var < 100  # Threshold for variance
        
        return True  # Default to four if not enough data
    
    def is_wicket(self, positions, stumps_objects):
        """
        Check if a wicket event has occurred.
        
        Args:
            positions (list): Recent ball positions
            stumps_objects (list): Detected stumps objects
            
        Returns:
            bool: True if wicket event detected
        """
        if not stumps_objects:
            return False
        
        # Get stumps location
        stumps = stumps_objects[0]
        stumps_bbox = stumps['bbox']
        stumps_center = ((stumps_bbox[0] + stumps_bbox[2]) / 2, 
                         (stumps_bbox[1] + stumps_bbox[3]) / 2)
        
        # Check if ball trajectory intersects with stumps
        if len(positions) >= 3:
            # Get recent positions
            p1, p2, p3 = positions[-3:]
            
            # Calculate direction vector
            dx = p3[0] - p1[0]
            dy = p3[1] - p1[1]
            
            # Check if ball is moving toward stumps
            vector_to_stumps = (stumps_center[0] - p3[0], stumps_center[1] - p3[1])
            dot_product = dx * vector_to_stumps[0] + dy * vector_to_stumps[1]
            
            # Ball is moving toward stumps
            if dot_product > 0:
                # Check distance to stumps
                distance_to_stumps = np.sqrt(vector_to_stumps[0]**2 + vector_to_stumps[1]**2)
                
                # Check if ball is close to stumps
                return distance_to_stumps < 50  # Threshold in pixels
        
        return False
    
    def is_shot_played(self, positions):
        """
        Check if a shot has been played (ball direction changed suddenly).
        
        Args:
            positions (list): Recent ball positions
            
        Returns:
            bool: True if shot event detected
        """
        if len(positions) >= 5:
            # Get recent positions
            p1, p2, p3, p4, p5 = positions[-5:]
            
            # Calculate direction vectors
            v1 = (p2[0] - p1[0], p2[1] - p1[1])
            v2 = (p5[0] - p4[0], p5[1] - p4[1])
            
            # Calculate angle between vectors
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            mag_v1 = np.sqrt(v1[0]**2 + v1[1]**2)
            mag_v2 = np.sqrt(v2[0]**2 + v2[1]**2)
            
            # Avoid division by zero
            if mag_v1 > 0 and mag_v2 > 0:
                cos_angle = dot_product / (mag_v1 * mag_v2)
                cos_angle = min(1.0, max(-1.0, cos_angle))  # Ensure valid range
                angle = np.arccos(cos_angle) * 180 / np.pi
                
                # Check if angle indicates a significant direction change
                return angle > 30  # Threshold in degrees
        
        return False

# Global ball tracker instance
ball_tracker = BallTracker()

def detect_events(frame, objects, poses, ball_positions, frame_num, timestamp):
    """
    Detect cricket events in the current frame.
    
    Args:
        frame (numpy.ndarray): Current video frame
        objects (list): Detected objects in the frame
        poses (list): Detected player poses
        ball_positions (list): Recent ball positions with timestamps
        frame_num (int): Current frame number
        timestamp (float): Current timestamp in seconds
        
    Returns:
        list: Detected events
    """
    events = []
    
    # Extract the latest ball position
    latest_ball = None
    if ball_positions and len(ball_positions) > 0:
        latest_ball = ball_positions[-1]['position']
    
    # Update ball tracker
    ball_tracker.update(latest_ball, frame_num)
    
    # Detect events based on ball tracking
    ball_events = ball_tracker.detect_events(frame, objects, frame_num, timestamp)
    if ball_events:
        events.extend(ball_events)
    
    # Additional event detection logic could be added here
    # For example, detecting runs based on player movements
    
    return events
