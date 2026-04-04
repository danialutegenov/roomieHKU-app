# RoomieHKU Technical Overview

## Purpose

This document records the main technical decisions for RoomieHKU so the team can build from the same architecture, stack, and implementation assumptions.

## Technical Direction

RoomieHKU will be built as a traditional Django web application backed by PostgreSQL.

The project prioritizes speed, clarity, and team familiarity. Since the team already knows Django and the project will run locally, it does not need a separate frontend application or a separate API service.

## Chosen Stack

- **Backend framework:** Django
- **Language:** Python
- **Database:** PostgreSQL
- **Database access layer:** Django ORM
- **Frontend approach:** Django templates with HTML, CSS, and JavaScript
- **Styling approach:** Tailwind CSS
- **Authentication:** Django built-in authentication and session management
- **Admin tooling:** custom admin dashboard UI plus Django admin
- **Runtime context:** local development and local demonstration

## Architecture Overview

RoomieHKU will use a monolithic web application structure.

- Django handles routing, views, forms, authentication, and server-side rendering
- PostgreSQL stores the application data
- Django ORM is used to read from and write to the database
- Django models and migrations define and evolve the schema
- HTML pages are rendered on the server and returned to the browser
- two frontend surfaces are served by the same backend: student app UI and admin dashboard UI
- JavaScript is used only where needed

## Frontend and Backend Communication

The frontend communicates with the backend through normal Django request-response flows.

Typical flow:

1. the browser sends a request
2. a Django view handles the request
3. the view reads or writes data through Django ORM
4. Django renders an HTML template
5. the browser receives the rendered page

## API Direction

The project does not require a separate REST API. Most interactions will be handled directly through Django views and templates.

## Main Technical Modules

### Authentication and Access Control

- user registration
- user login and logout
- session-based authentication
- role-based access for normal users and admins

### User Profiles

- profile creation and editing
- display of user information
- connection between a user and their listings, comments, and saved items

### Listings

- creation, editing, and deletion of listings
- support for multiple listing types
- public browsing of visible listings

### Search and Filtering

- keyword-based search
- filtering by listing attributes such as type, location, or rent
- sorting and feed presentation

### Saved Listings

- storing user-interest relationships between users and listings
- preventing duplicate saves

### Comments

- commenting on listings
- moderation and deletion rules

### Admin Tools

- moderation of users, listings, and comments
- access to simple platform statistics

### Database Management

- defining application models in Django
- managing schema changes through migrations
- enforcing relationships and constraints at the database level
- supporting application queries and course-related analytics

## Database Approach

The system will use PostgreSQL as a relational database because the project centers on clearly related entities such as users, listings, comments, and saved listings.

Django ORM will be the main database access layer. It will be used to define models, manage relationships, and handle migrations. Raw SQL can still be used where needed for course-related queries or analytics.

## Authentication and Roles

Authentication will use Django’s built-in user and session system.

- **User:** can browse listings, manage their profile, create listings, save listings, and comment
- **Admin:** can perform moderation tasks and access admin-only functionality

## Frontend Approach

The frontend will be built with Django templates rather than a separate JavaScript application.

The UI will use Tailwind CSS for styling (loaded via CDN for this course-project MVP), with small amounts of JavaScript added where extra interactivity is needed.

The project will maintain two frontend surfaces:

- **Student app frontend:** user-facing flows for listings, search, saved items, and comments
- **Admin dashboard frontend:** internal moderation and platform oversight UI (staff-only access)

## Suggested Project Structure

Current scaffold direction:

```text
roomiehku/
  .env.example
  manage.py
  requirements.txt
  roomiehku/
    __init__.py
    asgi.py
    settings.py
    urls.py
    wsgi.py
  core/
    __init__.py
    admin.py
    apps.py
    forms.py
    models.py
    migrations/
      __init__.py
    templates/
      core/
        app/
          base.html
          home.html
        dashboard/
          base.html
          home.html
    static/
      core/
        app/
        css/
        dashboard/
        js/
        images/
    tests.py
    urls.py
    views.py
  media/
    listing_images/
  docs/
```

- `manage.py`: runs Django commands
- `roomiehku/`: project-level Django config
- `settings.py`: app and database settings
- `urls.py`: main route entry and app route includes
- `core/`: main application logic
- `models.py`: database models
- `views.py`: request handling
- `forms.py`: form validation and input handling
- `core/urls.py`: app-specific routes
- `migrations/`: database schema changes
- `templates/core/app/`: student app templates
- `templates/core/dashboard/`: admin dashboard templates
- `static/core/`: namespaced CSS, JS, images
- `media/listing_images/`: uploaded listing files
- `docs/`: project documentation

For the current project scope, the team will keep the system in one Django app to reduce setup overhead and move faster.

## Key Engineering Principles

- prefer one Django application codebase over multiple services
- keep the request flow simple and understandable
- use Django built-ins where possible instead of rebuilding common features
- keep interactive behavior lightweight unless there is a clear product need
- align implementation closely with the database schema and project brief

## Current Assumptions

- the application is primarily page-based, not SPA-based
- the project will run locally for development and demo
- a separate public API is not required for the first version
- partial asynchronous page updates are not required for the first version
- the project will stay in one Django app for simplicity
- both frontend surfaces will be served from the same Django project
- the team values fast delivery and maintainability over architectural novelty

## Open Decisions

The following items should still be finalized by the team:

- whether listing images will use uploaded files or image URLs only
