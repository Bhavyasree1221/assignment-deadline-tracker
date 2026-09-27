 ## Live Demo 
 https://assignment-deadline-tracker-7tvv.onrender.com

# Assignment Deadline Tracker with Priority

A student-friendly web application for managing academic assignments, tracking deadlines, and organizing tasks based on priority.

## Project Overview

The Assignment Deadline Tracker with Priority helps students manage multiple assignments in an organized way. It allows users to add assignment details, track deadlines, set difficulty levels, estimate completion time, and view assignments according to priority.

The project combines Programming, Data Structures, and Communicative English concepts with a Python-based web application.

## Features

- Add assignments
- View all assignments
- Edit assignment details
- Delete assignments
- Search and filter assignments
- Track assignment deadlines
- Calculate remaining days
- Set assignment difficulty
- Estimate completion time
- Generate priority scores
- Display priority-based assignment list
- Use Stack for recent activity/history
- Use Heap/Priority Queue for priority management
- AI/LLM-based priority suggestion layer
- SQLite database for storing assignments
- Student-friendly web interface

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

## Data Structures Used

### List / Array

Python Lists are used to store and process assignment records.

### Stack

A Stack follows the LIFO (Last In, First Out) principle and is used for recent activity or action history.

### Heap / Priority Queue

A Heap/Priority Queue is used to organize assignments based on their priority.

## Priority Calculation

The project uses a project-defined priority calculation model.

### Difficulty Score

- Easy = 1
- Medium = 2
- Hard = 3

### Deadline Urgency Score

- Overdue / 0 days = 5
- 1–2 days = 4
- 3–5 days = 3
- 6–7 days = 2
- More than 7 days = 1

### Priority Score

Priority Score = Difficulty Score + Deadline Urgency Score

For example:

Hard assignment + 2 days remaining

3 + 4 = 7

This results in a high-priority assignment in the project.

> Note: This priority formula is defined specifically for this academic project and is not an official industry standard.

## AI / LLM Priority Suggestion

The project includes an AI/LLM priority suggestion layer that can consider:

- Assignment difficulty
- Remaining days
- Estimated completion time
- Assignment status

When an actual LLM API is configured, the AI layer can provide a natural-language priority suggestion and explanation.

## Database

The project uses SQLite to store assignment information.

Main assignment fields include:

- Assignment ID
- Assignment Name
- Subject
- Description
- Difficulty
- Deadline
- Estimated Completion Hours
- Status
- Created Date

## Project Structure

```text
assignment-deadline-tracker/
│
├── app.py
├── ai_priority.py
├── console.py
├── data_structures.py
├── database.py
├── priority.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── database/
│
├── static/
│   ├── css/
│   └── js/
│
└── templates/

## How to Run
1. Clone the repository
git clone https://github.com/Bhavyasree1221/assignment-deadline-tracker.git
2. Open the project folder
cd assignment-deadline-tracker
3. Install dependencies
pip install -r requirements.txt
4. Run the application
python app.py
5. Open in browser
http://127.0.0.1:5000

## Academic Subject Integration

## Programming
Python programming, functions, conditions, loops, database connectivity, and Flask are used to develop the application.

## Data Structures
Lists/Arrays, Stack, and Heap/Priority Queue are used for assignment management and priority handling.

## Communicative English
Technical writing concepts are used for assignment descriptions, system messages, labels, documentation, and user-friendly content.

# Team Members
B. Bhavyasree
M. Premalatha
N. Srija
A. Aashritha

## Project Outcome
The project provides a simple platform for students to organize assignments, monitor deadlines, and identify higher-priority tasks using programming and data structure concepts.

## Future Enhancements
Email deadline reminders
Push notifications
Calendar integration
Mobile application
Cloud database
Personalized task planning
Advanced AI-based planning
Multi-user support

## License
This project is developed as an academic mini-project.


