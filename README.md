# QuizMaster (Windows-Friendly)

A multi-page Streamlit quiz platform with user authentication, category-based quizzes, admin content management, score tracking, and AI-powered quiz generation from uploaded files.

## Features

- User authentication (register/login) with hashed passwords
- Role-based access (`student` and `admin`)
- Category-based quiz gameplay with randomized question order
- Scoring, accuracy tracking, and persisted score history
- Leaderboard and personal performance analytics
- Admin panel for adding, editing, deleting, and migrating questions
- SQLite-backed data layer with `users`, `questions`, and `scores` tables
- AI assistant ("Shiva AI") chat support
- AI-generated quiz from uploaded files (`txt`, `md`, `pdf`, `docx`, `pptx`, code/text formats)

## Tech Stack

- Python 3.10+
- Streamlit
- SQLite
- Pandas
- Requests
- pypdf
- python-docx
- python-pptx

## Project Structure

```text
s6-quizmaster-windows/
|-- Home.py
|-- database.py
|-- setup_database.py
|-- requirements.txt
|-- streamlit/
|   `-- config.toml
|-- pages/
|   |-- 1_Quiz.py
|   |-- 2_Highscores.py
|   |-- 3_Categories.py
|   `-- 4_Admin.py
`-- data/
    |-- questions.json
    |-- highscores.json
    `-- quizmaster.db (auto-created)
```

## Quick Start

### 1. Clone

```bash
git clone https://github.com/shivanshmah14/Quizmaster-finalversion-microsoftfriendly-shivansh.git
cd Quizmaster-finalversion-microsoftfriendly-shivansh
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database and seed users/questions

```bash
python setup_database.py
```

### 5. Run the app

```bash
streamlit run Home.py
```

## Default Accounts

- Admin: `admin` / `admin123`
- Student: `student` / `student123`

## Core Workflows

### Student

1. Register or log in
2. Choose a category
3. Complete quiz questions
4. Review results and leaderboard stats

### Admin

1. Log in with an admin account
2. Open **Admin Panel**
3. Add/edit/delete quiz questions
4. View statistics
5. Optionally migrate questions from `data/questions.json`

## Database Notes

The app uses SQLite (`data/quizmaster.db`) with:

- `users` table for credentials and roles
- `questions` table for quiz content
- `scores` table for game outcomes

Leaderboard data is built using SQL joins between `scores` and `users`.

## Shiva AI Integration

The app includes:

- Sidebar study assistant chat
- File-to-quiz generation from uploaded documents

To use this in production, move API credentials to environment variables and never commit secrets.

## Troubleshooting

- `ModuleNotFoundError`: run commands from the project root.
- No questions available: run `python setup_database.py` or add questions in Admin Panel.
- Login issues: ensure username exists and password length is at least 6 characters.
- Admin panel unavailable: confirm the logged-in user has admin role.

## Roadmap Ideas

- Environment-based config (`.env`) for API keys
- Unit tests for database and quiz logic
- Export/import question banks from UI
- Better duplicate detection during JSON migration
- CI checks for formatting and tests

## License

Educational project for coursework and learning use.
