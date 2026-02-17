# AA Tracker Streamlit

Meeting attendance and treasury tracking for AA groups.

## Features

- **Dashboard**: Attendance streak, upcoming meetings this week, treasury balance
- **Meetings**: Add/Edit/Delete meetings (CRUD)
- **Check In**: Record attendance for meetings
- **History**: View attendance history with filters
- **Treasury**: Track income/expenses, categories, monthly reports

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run streamlit_app.py
```

3. Default password: `nick123`

## GitHub Setup

To push to GitHub:

```bash
# If using SSH:
git remote add origin git@github.com:LearningEverythingFirstTIme/aa-tracker-streamlit.git
git push -u origin main

# If using HTTPS with a token:
git remote add origin https://github.com/LearningEverythingFirstTIme/aa-tracker-streamlit.git
git push -u origin main
```

## Database

The SQLite database (`aa_tracker.db`) is included with sample data. It's stored in the same directory as the app.

## Tech Stack

- Streamlit
- Pandas
- Plotly
- SQLite
