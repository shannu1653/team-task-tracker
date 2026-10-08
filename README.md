# Team Task Tracker API

A production-minded REST API for managing projects, project members, and tasks.

## Technology Stack

- Python 3.12
- Django 6.1.1
- Django REST Framework
- PostgreSQL
- JWT Authentication
- drf-spectacular / OpenAPI / Swagger
- Pytest / pytest-django
- Docker / Docker Compose
- Gunicorn
- GitHub Actions

---

## Features

### Authentication

- User registration
- Email/password login
- Secure password hashing
- JWT access and refresh tokens
- Refresh token rotation
- Refresh token blacklist/revocation
- Logout
- Case-insensitive email handling
- Password minimum length validation
- Consistent JSON error responses

### Projects

- Create project
- Project creator automatically becomes owner and member
- List projects available to the authenticated user
- View project details
- Add existing registered users to a project
- View project members
- Owner-only member management
- Owner-only project deletion
- Project-level authorization

### Tasks

- Create task
- View project tasks
- View individual task
- Update task
- Delete task
- Task title and description
- LOW / MEDIUM / HIGH priority
- TODO / IN_PROGRESS / DONE status
- Optional due date
- Optional project-member assignee
- Task creator tracking
- Created/updated timestamps
- Automatic `completed_at` handling

### Task Listing

Supports:

- Pagination
- Status filtering
- Priority filtering
- Assignee filtering
- Due-date range filtering
- Created-date sorting
- Due-date sorting

Pagination:

- Default page size: `10`
- Maximum page size: `50`

### Project Summary

Provides:

- Total task count
- TODO count
- IN_PROGRESS count
- DONE count
- LOW priority count
- MEDIUM priority count
- HIGH priority count

### Engineering Features

- PostgreSQL
- Database constraints
- Database indexes
- Environment-based configuration
- Consistent API error format
- OpenAPI / Swagger documentation
- Docker
- Docker Compose
- Gunicorn
- GitHub Actions CI
- Audit logging
- Automated tests

---

# Project Structure

```text
team-task-tracker/
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── projects/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── tasks/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── audit/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   └── services.py
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── exceptions.py
│   ├── settings.py
│   ├── urls.py
│   ├── utils.py
│   └── wsgi.py
│
├── tests/
│   └── ...
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .dockerignore
├── .env.example
├── .gitignore
├── AI_USAGE.md
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── README.md
```

> The real `.env` file is intentionally not committed to the repository.

---

# Local Development Setup

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd team-task-tracker
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a local `.env` file in the project root.

Use `.env.example` as the template.

Example:

```env
SECRET_KEY=your-real-secret-key
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=team_task_tracker
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Important

Never commit the real `.env` file.

The repository should contain:

```text
.env.example
```

but not:

```text
.env
```

---

# PostgreSQL Setup

Create a PostgreSQL database named:

```text
team_task_tracker
```

Configure the database credentials in `.env`.

Then run:

```bash
python manage.py makemigrations
python manage.py migrate
```

For a fresh project, all generated migration files should be committed to Git.

---

# Create Admin User

```bash
python manage.py createsuperuser
```

The Django admin is available at:

```text
http://127.0.0.1:8000/admin/
```

---

# Start Development Server

```bash
python manage.py runserver
```

Base URL:

```text
http://127.0.0.1:8000/
```

---

# API Documentation

## Swagger UI

```text
http://127.0.0.1:8000/api/docs/
```

## OpenAPI Schema

```text
http://127.0.0.1:8000/api/schema/
```

Swagger provides an interactive way to inspect and execute the API endpoints.

---

# Authentication APIs

## Register

```http
POST /auth/register/
```

Request:

```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "Password@123"
}
```

Response contains:

```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
}
```

Passwords are never returned.

---

## Login

```http
POST /auth/login/
```

Request:

```json
{
    "email": "john@example.com",
    "password": "Password@123"
}
```

The response contains:

- Access token
- Refresh token
- Authenticated user information

Use the access token for protected APIs:

```http
Authorization: Bearer <access_token>
```

---

## Logout

```http
POST /auth/logout/
```

Request:

```json
{
    "refresh": "<refresh_token>"
}
```

The refresh token is blacklisted after logout.

---

# Project APIs

## Create Project

```http
POST /projects/
```

Request:

```json
{
    "name": "Website Project",
    "description": "Team website development"
}
```

The authenticated user automatically becomes:

- Project owner
- Project member

---

## List Projects

```http
GET /projects/
```

Only projects where the authenticated user is a member are returned.

---

## Project Details

```http
GET /projects/{project_id}/
```

Only project members can access the project.

---

## Delete Project

```http
DELETE /projects/{project_id}/
```

Only the project owner can delete the project.

---

# Project Member APIs

## Add Member

```http
POST /projects/{project_id}/members/
```

Request:

```json
{
    "email": "member@example.com"
}
```

Only the project owner can add members.

The user must already be registered.

---

## List Members

```http
GET /projects/{project_id}/members/
```

Only project members can view the member list.

---

# Task APIs

## Create Task

```http
POST /projects/{project_id}/tasks/
```

Example:

```json
{
    "title": "Implement authentication",
    "description": "Create JWT authentication",
    "priority": "HIGH",
    "status": "TODO",
    "due_date": "2026-10-20T18:00:00Z",
    "assignee": 2
}
```

The assignee must already be a member of the project.

---

## List Tasks

```http
GET /projects/{project_id}/tasks/
```

Only project members can view project tasks.

---

## Get Individual Task

```http
GET /tasks/{task_id}/
```

---

## Update Task

```http
PATCH /tasks/{task_id}/
```

Example:

```json
{
    "status": "DONE"
}
```

When a task changes from a non-DONE state to `DONE`, `completed_at` is automatically set.

When a completed task is reopened, `completed_at` is cleared.

---

## Delete Task

```http
DELETE /tasks/{task_id}/
```

A task can be deleted by:

- The task creator
- The project owner

---

# Task Filtering

## Status

```http
GET /projects/{id}/tasks/?status=DONE
```

Valid values:

```text
TODO
IN_PROGRESS
DONE
```

## Priority

```http
GET /projects/{id}/tasks/?priority=HIGH
```

Valid values:

```text
LOW
MEDIUM
HIGH
```

## Assignee

```http
GET /projects/{id}/tasks/?assignee=2
```

## Due-Date Range

```http
GET /projects/{id}/tasks/?due_from=2026-10-01T00:00:00Z&due_to=2026-10-31T23:59:59Z
```

---

# Task Sorting

## Created Date Ascending

```http
GET /projects/{id}/tasks/?sort=created_at
```

## Created Date Descending

```http
GET /projects/{id}/tasks/?sort=-created_at
```

## Due Date Ascending

```http
GET /projects/{id}/tasks/?sort=due_date
```

## Due Date Descending

```http
GET /projects/{id}/tasks/?sort=-due_date
```

---

# Pagination

Default:

```text
10 tasks per page
```

Example:

```http
GET /projects/{id}/tasks/?page=2
```

Custom page size:

```http
GET /projects/{id}/tasks/?page=1&page_size=20
```

Maximum:

```text
50
```

---

# Project Summary

```http
GET /projects/{project_id}/summary/
```

Example response:

```json
{
    "project_id": 1,
    "project_name": "Website Project",
    "total_tasks": 5,
    "status_counts": {
        "TODO": 2,
        "IN_PROGRESS": 1,
        "DONE": 2
    },
    "priority_counts": {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 2
    }
}
```

Only project members can view the summary.

---

# Authorization Rules

| Operation | Permission |
|---|---|
| Register | Public |
| Login | Public |
| Create project | Authenticated user |
| View project | Project member |
| Add project member | Project owner |
| View members | Project member |
| Delete project | Project owner |
| Create task | Project member |
| View tasks | Project member |
| View individual task | Project member |
| Update task | Project member |
| Delete task | Project owner or task creator |
| Assign task | Assignee must be project member |
| View summary | Project member |

---

# Error Response Format

The API uses a consistent error structure.

Example validation error:

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request.",
        "details": {
            "email": [
                "A user with this email already exists."
            ]
        }
    }
}
```

Example authorization error:

```json
{
    "error": {
        "code": "FORBIDDEN",
        "message": "You are not a member of this project."
    }
}
```

---

# Database Design

Main entities:

```text
User
 │
 ├── Project
 │      │
 │      ├── ProjectMembership
 │      │
 │      └── Task
 │
 └── Task
```

Relationships:

```text
User 1 ──── * Project
User 1 ──── * ProjectMembership
Project 1 ──── * ProjectMembership
Project 1 ──── * Task
User 1 ──── * Task (created_by)
User 1 ──── * Task (assignee)
Project 1 ──── * AuditLog
User 1 ──── * AuditLog
Task 1 ──── * AuditLog
```

### Database Design Decisions

- PostgreSQL is used for relational data.
- Project membership is represented by a separate model because membership controls authorization.
- Unique constraints prevent duplicate project memberships.
- Indexes support common project/task filtering and sorting queries.
- Foreign keys enforce relationships between users, projects, memberships, tasks, and audit records.

---

# Audit Logging

The project includes an audit log for important actions.

Tracked actions include:

```text
PROJECT_CREATED
PROJECT_DELETED
MEMBER_ADDED
TASK_CREATED
TASK_UPDATED
TASK_DELETED
```

Audit records contain:

- User
- Action
- Project
- Task
- Additional details
- Timestamp

Audit logs are available through the Django admin.

---

# Docker

## Build Containers

```bash
docker compose build
```

## Start Application

```bash
docker compose up
```

## Run in Background

```bash
docker compose up -d
```

## Stop Application

```bash
docker compose down
```

PostgreSQL data is persisted using a Docker volume.

For Docker Compose, the PostgreSQL host should normally be:

```env
DB_HOST=db
```

because `db` is the PostgreSQL service name.

---

# Production

The application uses Gunicorn:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Collect static files:

```bash
python manage.py collectstatic --noinput
```

Apply database migrations:

```bash
python manage.py migrate
```

Production configuration should use:

```env
DEBUG=False
```

Production secrets must be provided through environment variables.

The production environment should also configure:

- Secure HTTPS
- Production `ALLOWED_HOSTS`
- Secure cookies
- PostgreSQL credentials
- Strong Django `SECRET_KEY`
- Appropriate CORS origins

---

# Testing

The project uses:

- Pytest
- pytest-django

Run the test suite with:

```bash
pytest
```

The final test suite is intended to cover:

- Registration
- Duplicate/case-insensitive email validation
- Login
- Failed login
- Authentication
- Project creation
- Project authorization
- Project membership
- Invalid task assignee
- Task creation
- Task filtering
- Task pagination
- Task updates
- Task deletion authorization
- `completed_at` behavior
- Project summary
- Validation errors

The assignment requires at least **8 meaningful automated tests**.

---

# Continuous Integration

GitHub Actions runs the backend checks automatically.

The CI workflow performs:

```text
Install dependencies
        ↓
Start PostgreSQL
        ↓
Run migrations
        ↓
Run Django system check
        ↓
Run pytest
```

Workflow:

```text
.github/workflows/ci.yml
```

---

# Security

Important security measures include:

- Passwords are hashed using Django's password hashing system.
- Passwords are never returned by API responses.
- JWT authentication protects project/task APIs.
- Refresh tokens support rotation and blacklisting.
- Case-insensitive email validation prevents duplicate accounts with different casing.
- Project-level authorization prevents unauthorized access.
- Only owners can manage project membership.
- Task assignees must be project members.
- Database constraints protect data integrity.
- Environment variables are used for secrets and database credentials.
- Production HTTPS security settings are enabled when `DEBUG=False`.

---

# Design Decisions

## Django REST Framework

DRF provides serializers, authentication, permissions, request handling, validation, and API development features suitable for this REST API.

## PostgreSQL

PostgreSQL was selected because the application contains relational data between users, projects, memberships, tasks, and audit logs.

## ProjectMembership

Project membership is represented using a separate model instead of relying only on a simple many-to-many relationship because membership is an important authorization concept.

## JWT

JWT provides token-based authentication for protected REST API endpoints.

## Database Indexes

Indexes were added for commonly filtered and queried project/task fields to support better database performance.

## Audit Logging

Audit logging records important project and task operations for traceability and administration.

---

# Assumptions

- Users must register before they can be added to a project.
- A project creator automatically becomes its owner and member.
- Only project members can access project resources.
- Only project owners can add project members.
- A task assignee must already belong to the project.
- Task creators and project owners can delete tasks.
- Access tokens are short-lived.
- Refresh tokens have a longer lifetime and support rotation/blacklisting.
- PostgreSQL is the primary supported database.
- Production secrets are supplied through environment variables.

---

# Future Improvements

Possible future improvements include:

- API rate limiting
- Email verification
- Password reset
- More granular role-based permissions
- Redis caching
- Background task processing
- Advanced search
- Deployment monitoring
- API versioning
- More extensive performance/load testing
- Production email service integration

---

# Assignment Deliverables

The project submission should contain:

- Source code
- `requirements.txt`
- Database migrations
- `.env.example`
- Automated tests
- OpenAPI / Swagger documentation
- `README.md`
- `AI_USAGE.md`
- Docker configuration
- GitHub Actions CI configuration

The real `.env` file and other secrets must not be committed.

---

# License

This project was developed as part of a Backend Engineering Internship assignment.
