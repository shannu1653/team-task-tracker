# AI Usage

## Purpose

AI tools were used as a development assistant during the implementation of the
Team Task Tracker API.

AI assistance was used for planning, implementation guidance, code review,
documentation, debugging suggestions, and test planning.

The final implementation was reviewed, understood, and integrated manually by
the developer.

## Areas Where AI Assistance Was Used

### 1. Project Structure

AI assistance was used to plan the Django project structure and separate the
application into:

- `accounts`
- `projects`
- `tasks`
- `audit`
- `config`

The structure was reviewed and adapted according to the assignment
requirements.

### 2. Authentication

AI assistance was used while implementing:

- User registration
- JWT authentication
- Access and refresh tokens
- Refresh token rotation
- Refresh token blacklisting
- Logout
- Password validation
- Authentication-related API documentation

The authentication implementation was reviewed and adapted to the project
requirements.

### 3. Project Management

AI assistance was used for implementation ideas related to:

- Project creation
- Project listing
- Project details
- Project membership
- Owner authorization
- Project deletion
- Project summary
- Membership validation

### 4. Task Management

AI assistance was used for:

- Task creation
- Task listing
- Task detail retrieval
- Task updates
- Task deletion
- Status handling
- Priority handling
- Assignee validation
- Filtering
- Sorting
- Pagination
- `completed_at` handling
- Task authorization

### 5. Audit Logging

AI assistance was used to design and review the audit logging functionality,
including logging important actions such as:

- Project creation
- Project deletion
- Member addition
- Task creation
- Task updates
- Task deletion

### 6. Database Design

AI assistance was used to review:

- Django model relationships
- Foreign keys
- Unique constraints
- Database indexes
- Query optimization
- Project membership relationships

### 7. API Documentation

AI assistance was used to configure and organize:

- OpenAPI schema
- Swagger UI
- API endpoint documentation
- Request examples
- Response examples

### 8. Testing

AI assistance was used to plan and create meaningful automated tests covering:

- Registration
- Login
- Authentication validation
- Project permissions
- Project membership
- Task permissions
- Task creation and updates
- Task completion behavior
- Filtering
- Sorting
- Pagination
- Project summary
- Audit logging

The tests were reviewed against the assignment requirements.

### 9. Deployment and Engineering

AI assistance was used for development guidance related to:

- Environment variables
- `.env.example`
- Docker
- Docker Compose
- Gunicorn
- Static files
- GitHub Actions CI
- Production-oriented Django settings

## Human Responsibility

The developer is responsible for the final codebase.

AI-generated suggestions were reviewed, modified where necessary, and
integrated according to the assignment requirements.

AI suggestions were not treated as automatically correct. The implementation
was reviewed for correctness, security, authorization behavior, database
relationships, API behavior, and maintainability.

The developer understands the main implementation decisions, API behavior,
database relationships, authentication flow, authorization rules, audit
logging, and task business logic.

## Important Design Decisions

### Django REST Framework

Django REST Framework was selected because it provides a mature structure for
building REST APIs, serializers, authentication, permissions, validation, and
API documentation.

### PostgreSQL

PostgreSQL was selected as the relational database because the application has
relationships between users, projects, memberships, and tasks.

### JWT

JWT authentication was selected for stateless API authentication.

Refresh-token rotation and blacklisting are enabled to provide stronger token
management.

### Project Membership

Project membership is stored separately using the `ProjectMembership` model.

This makes authorization explicit and allows a project to contain multiple
users while ensuring that only members can access project resources.

### Task Completion

The `completed_at` field is controlled by the task status:

- When a task first becomes `DONE`, `completed_at` is set.
- When a completed task is reopened, `completed_at` is cleared.

### Audit Logging

Important project and task operations are recorded using the `AuditLog`
model.

This provides an auditable history of important actions performed through the
API.

## Limitations

AI assistance does not replace testing or code review.

The complete application will be validated using the final automated test
suite and final engineering checks before submission.

The developer remains responsible for understanding and verifying the final
implementation.