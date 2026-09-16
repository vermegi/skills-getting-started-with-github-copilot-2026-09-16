"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "waitlist": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "waitlist": []
    },
    "Soccer Team": {
        "description": "Practice soccer skills and compete in school matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": [],
        "waitlist": []
    },
    "Basketball Team": {
        "description": "Develop basketball skills and play competitive games",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": [],
        "waitlist": []
    },
    "Art Club": {
        "description": "Explore drawing, painting, and other visual art techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": [],
        "waitlist": []
    },
    "Drama Club": {
        "description": "Act, perform, and create productions for the school community",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": [],
        "waitlist": []
    },
    "Debate Club": {
        "description": "Build argumentation skills and discuss important ideas",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": [],
        "waitlist": []
    },
    "Science Club": {
        "description": "Conduct experiments and explore the world of science",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": [],
        "waitlist": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Check if the student is already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Check if the student is already waiting for a spot
    if email in activity["waitlist"]:
        raise HTTPException(status_code=400, detail="Student already on the waitlist for this activity")

    # If the activity is full, place the student on the waitlist
    if len(activity["participants"]) >= activity["max_participants"]:
        activity["waitlist"].append(email)
        return {
            "message": f"{activity_name} is full. Added {email} to the waitlist at position {len(activity['waitlist'])}",
            "status": "waitlisted",
            "waitlist_position": len(activity["waitlist"]),
        }

    # Add student
    activity["participants"].append(email)
    return {
        "message": f"Signed up {email} for {activity_name}",
        "status": "registered",
    }


@app.delete("/activities/{activity_name}/unregister")
def unregister_participant(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if email not in activity["participants"]:
        # Allow a waitlisted student to withdraw their request
        if email in activity["waitlist"]:
            activity["waitlist"].remove(email)
            return {
                "message": f"Removed {email} from the waitlist for {activity_name}",
                "status": "removed_from_waitlist",
            }

        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    activity["participants"].remove(email)

    # Auto-enroll the first waitlisted student, if any
    promoted = None
    if activity["waitlist"]:
        promoted = activity["waitlist"].pop(0)
        activity["participants"].append(promoted)

    message = f"Unregistered {email} from {activity_name}"
    if promoted:
        message += f". {promoted} was moved from the waitlist into the activity"

    return {
        "message": message,
        "status": "unregistered",
        "promoted": promoted,
    }
