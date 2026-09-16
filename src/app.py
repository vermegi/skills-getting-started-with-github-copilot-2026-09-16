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


def get_activity(activity_name: str):
    """Return the activity or raise a 404 when it does not exist"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


def is_participant(activity, email: str) -> bool:
    return email in activity["participants"]


def is_waitlisted(activity, email: str) -> bool:
    return email in activity["waitlist"]


def activity_is_full(activity) -> bool:
    return len(activity["participants"]) >= activity["max_participants"]


def add_to_activity(activity, email: str) -> None:
    activity["participants"].append(email)


def remove_from_activity(activity, email: str) -> None:
    activity["participants"].remove(email)


def add_to_waitlist(activity, email: str) -> None:
    activity["waitlist"].append(email)


def remove_from_waitlist(activity, email: str) -> None:
    activity["waitlist"].remove(email)


def promote_first_waitlisted(activity):
    """Move the first waitlisted student into the activity and return them"""
    if not activity["waitlist"]:
        return None

    promoted = activity["waitlist"].pop(0)
    add_to_activity(activity, promoted)
    return promoted


def signed_up_message(activity_name: str, email: str):
    return {
        "message": f"Signed up {email} for {activity_name}",
        "status": "registered",
    }


def waitlisted_message(activity, activity_name: str, email: str):
    position = activity["waitlist"].index(email) + 1
    return {
        "message": f"{activity_name} is full. Added {email} to the waitlist at position {position}",
        "status": "waitlisted",
        "waitlist_position": position,
    }


def unregistered_message(activity_name: str, email: str, promoted):
    message = f"Unregistered {email} from {activity_name}"
    if promoted:
        message += f". {promoted} was moved from the waitlist into the activity"

    return {
        "message": message,
        "status": "unregistered",
        "promoted": promoted,
    }


def removed_from_waitlist_message(activity_name: str, email: str):
    return {
        "message": f"Removed {email} from the waitlist for {activity_name}",
        "status": "removed_from_waitlist",
    }


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity, or add them to its waitlist when full"""
    activity = get_activity(activity_name)

    if is_participant(activity, email):
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    if is_waitlisted(activity, email):
        raise HTTPException(status_code=400, detail="Student already on the waitlist for this activity")

    if activity_is_full(activity):
        add_to_waitlist(activity, email)
        return waitlisted_message(activity, activity_name, email)

    add_to_activity(activity, email)
    return signed_up_message(activity_name, email)


@app.delete("/activities/{activity_name}/unregister")
def unregister_participant(activity_name: str, email: str):
    """Remove a student from an activity or its waitlist"""
    activity = get_activity(activity_name)

    if not is_participant(activity, email):
        if is_waitlisted(activity, email):
            remove_from_waitlist(activity, email)
            return removed_from_waitlist_message(activity_name, email)

        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    remove_from_activity(activity, email)
    promoted = promote_first_waitlisted(activity)
    return unregistered_message(activity_name, email, promoted)
