import random
import logging

logger = logging.getLogger(__name__)

# Commentary templates for different cricket events
COMMENTARY_TEMPLATES = {
    "boundary": {
        "four": [
            "That's a beautiful shot! The ball races away to the boundary for FOUR!",
            "What a stroke! That's FOUR runs as the ball reaches the boundary rope.",
            "Expertly placed! The fielder has no chance as the ball speeds to the boundary for FOUR.",
            "That'll be FOUR! Perfectly timed and placed to the boundary.",
            "The batsman finds the gap and gets FOUR runs for that shot."
        ],
        "six": [
            "MASSIVE HIT! That's gone all the way for SIX!",
            "The batsman has really got hold of that one! SIX runs!",
            "Up, up, and away! That's a huge SIX over the boundary!",
            "What a strike! The ball sails over the boundary for SIX!",
            "The crowd is on their feet! That's a magnificent SIX!"
        ]
    },
    "wicket": {
        "bowled": [
            "BOWLED HIM! The stumps are shattered!",
            "The ball hits the timber! He's BOWLED!",
            "Clean bowled! The batsman has to go!",
            "The stumps are in disarray! That's a brilliant delivery to get the wicket!",
            "The ball sneaks through the gate and hits the stumps! He's out!"
        ],
        "caught": [
            "CAUGHT! The fielder takes a good catch and the batsman has to walk!",
            "Up goes the ball... and it's CAUGHT! What a take by the fielder!",
            "That's a catch! The batsman is disappointed as he walks back to the pavilion.",
            "The ball goes straight to the fielder, who makes no mistake! CAUGHT!",
            "A simple catch but an important wicket! The batsman is out!"
        ],
        "lbw": [
            "That looks plumb! The umpire raises the finger for LBW!",
            "Appeal for LBW... and he's given! The batsman has to go!",
            "Struck on the pads, and the umpire agrees with the appeal! LBW!",
            "A huge appeal for LBW, and the umpire doesn't hesitate! He's out!",
            "The ball strikes the pad in line with the stumps. LBW! He's gone!"
        ],
        "run_out": [
            "The fielder hits the stumps directly! That's a RUN OUT!",
            "There was never a run there! The batsman is RUN OUT!",
            "Quick work by the fielder! The batsman is well short of his ground. RUN OUT!",
            "The throw is accurate, and the batsman is RUN OUT!",
            "Brilliant fielding! The batsman is caught short of the crease. RUN OUT!"
        ],
        "stumped": [
            "The batsman is out of his crease, and the keeper whips off the bails! STUMPED!",
            "Clever work by the wicketkeeper! The batsman is STUMPED!",
            "The batsman overbalances, and the keeper is quick to remove the bails! STUMPED!",
            "Sharp stumping by the keeper! The batsman has to go!",
            "The batsman is caught short of his ground, and the keeper completes the stumping!"
        ]
    },
    "shot_played": {
        "straight drive": [
            "That's a classic straight drive! A classic shot played with a straight bat, hitting the ball back past the bowler.",
            "The batsman plays a lovely straight drive. Well-timed and executed.",
            "Excellent execution of the straight drive!",
            "Textbook straight drive from the batsman!",
            "The batsman demonstrates a perfect straight drive. The hallmark of good technique."
        ],
        "cover drive": [
            "That's a classic cover drive! An elegant shot played through the off side, between mid-off and point.",
            "The batsman plays a lovely cover drive. Pure elegance on display.",
            "Excellent execution of the cover drive!",
            "Textbook cover drive from the batsman!",
            "The batsman demonstrates a perfect cover drive. As elegant as they come."
        ],
        "cut shot": [
            "That's a classic cut shot! A horizontal bat shot played to a short, wide delivery, cutting the ball toward point.",
            "The batsman plays a lovely cut shot. Taking advantage of the width offered.",
            "Excellent execution of the cut shot!",
            "Textbook cut shot from the batsman!",
            "The batsman demonstrates a perfect cut shot. Using the pace of the ball well."
        ],
        "pull shot": [
            "That's a classic pull shot! A shot played to a short-pitched delivery, pulling the ball to the leg side.",
            "The batsman plays a lovely pull shot. Swiveling well to get on top of the bounce.",
            "Excellent execution of the pull shot!",
            "Textbook pull shot from the batsman!",
            "The batsman demonstrates a perfect pull shot. Great control against the short ball."
        ],
        "hook shot": [
            "That's a classic hook shot! Similar to the pull but played to a higher bouncing ball, hooking it around to the leg side.",
            "The batsman plays a lovely hook shot. Taking on the bouncer with confidence.",
            "Excellent execution of the hook shot!",
            "Textbook hook shot from the batsman!",
            "The batsman demonstrates a perfect hook shot. Handling the short ball with aplomb."
        ],
        "sweep shot": [
            "That's a classic sweep shot! A shot played on one knee, sweeping the ball to the leg side, usually against spin bowling.",
            "The batsman plays a lovely sweep shot. Good use of the feet against the spinner.",
            "Excellent execution of the sweep shot!",
            "Textbook sweep shot from the batsman!",
            "The batsman demonstrates a perfect sweep shot. Countering the spin effectively."
        ],
        "defensive shot": [
            "That's a classic defensive shot! A defensive stroke played with a straight bat to block the ball.",
            "The batsman plays a solid defensive shot. Showing good technique.",
            "Excellent execution of the defensive shot!",
            "Textbook defensive technique from the batsman!",
            "The batsman demonstrates perfect defensive technique. Safety first."
        ],
        "flick shot": [
            "That's a classic flick shot! A wristy shot played off the pads, flicking the ball to the leg side.",
            "The batsman plays a lovely flick shot. Elegant use of the wrists.",
            "Excellent execution of the flick shot!",
            "Textbook flick shot from the batsman!",
            "The batsman demonstrates a perfect flick shot. Turning a straight ball to the leg side."
        ],
        "generic": [
            "The batsman plays a good shot there.",
            "Well played by the batsman.",
            "That's good batting technique on display.",
            "The batsman gets into position nicely to play that shot.",
            "A confident stroke from the batsman."
        ]
    }
}

# Commentary transition phrases
TRANSITIONS = [
    "Meanwhile, ",
    "Now, ",
    "At this stage, ",
    "Looking at the field, ",
    "The bowler prepares again. ",
    "The batsman takes guard. ",
    "The fielders adjust their positions. ",
    "The crowd is getting excited. ",
    "There's a brief discussion in the field. ",
    "The umpire checks the ball. "
]

# Match situation commentary
MATCH_SITUATION = [
    "The pressure is mounting on the batting side.",
    "The bowler seems confident after that delivery.",
    "The batsman needs to be more careful with those shots.",
    "The field placement is really testing the batsman's patience.",
    "The bowling side is looking for a breakthrough here.",
    "The batting team is looking to build a partnership.",
    "Both teams know how crucial this phase of play is.",
    "The run rate is slowly climbing up.",
    "The captain is considering a bowling change.",
    "The fielders are alert and ready for any chance."
]

def generate_commentary(events):
    """
    Generate commentary based on detected events.
    
    Args:
        events (list): Detected cricket events
        
    Returns:
        str: Generated commentary
    """
    if not events:
        return "The match continues. Waiting for the next delivery."
    
    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda x: x['timestamp'])
    
    commentary_sections = []
    last_event_type = None
    consecutive_similar = 0
    
    # Generate commentary for each event
    for event in sorted_events:
        event_type = event['type']
        event_subtype = event.get('subtype', 'generic')
        
        # Check if we have templates for this event type
        if event_type in COMMENTARY_TEMPLATES:
            templates = COMMENTARY_TEMPLATES[event_type]
            
            # Check if we have specific templates for this subtype
            if event_subtype in templates:
                subtemplates = templates[event_subtype]
                
                # Choose a random template
                template = random.choice(subtemplates)
                
                # Check if we're repeating the same event type
                if event_type == last_event_type:
                    consecutive_similar += 1
                    
                    # If we've had several similar events, add variety
                    if consecutive_similar >= 2:
                        # Add a match situation comment
                        situation = random.choice(MATCH_SITUATION)
                        template = f"{template} {situation}"
                        
                        # Reset counter
                        consecutive_similar = 0
                else:
                    # Reset counter for different event type
                    consecutive_similar = 0
                
                commentary_sections.append(template)
                last_event_type = event_type
            
            # Fallback to generic templates if subtype not found
            elif 'generic' in templates:
                commentary_sections.append(random.choice(templates['generic']))
                
        # Fallback for unknown event types
        else:
            commentary_sections.append("The action continues on the cricket field.")
    
    # Add some transitions for a more natural flow
    if not commentary_sections:
        return "The match continues. Waiting for the next delivery."
    
    # Start with the first section
    combined = commentary_sections[0]
    
    # Add transitions between sections
    for i in range(1, len(commentary_sections)):
        # Add a transition phrase occasionally
        if random.random() < 0.7:  # 70% chance to add a transition
            transition = random.choice(TRANSITIONS)
            combined += f" {transition}{commentary_sections[i].lower()}"
        else:
            combined += f" {commentary_sections[i]}"
    
    return combined
