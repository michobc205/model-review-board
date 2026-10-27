> **Note on the source of this description**
> This project description was provided externally by the course coach, because the original file `project-for-today.md`, which the README of the course repository links to, is missing there. The wording below is the coach's text. Only the formatting was adjusted to Markdown.

# Model Review Board

## Scenario

A small ML team reviews a sample of model predictions before those decisions are used by another department. Their current spreadsheet makes it difficult to see which cases are pending and whether reviewer notes survive handovers.
Build a small web application that stores those reviews in a relational database. The first version should be intentionally modest: server-rendered HTML, a few routes, one database table, and one hosted deployment.

## Required User Journey

1. A reviewer opens the dashboard and sees all reviews plus status totals.
2. They create a review with a case reference, prediction, confidence, and short input summary.
3. They change the decision to approved or rejected and add notes.
4. Another browser session can read the saved decision.
5. A review can be deleted only through an explicit form action.

## Technical Requirements

* Use Flask routes and Jinja templates to render the user interface on the server.
* Use Flask-SQLAlchemy for one Review model and all database operations.
* Read the database connection from DATABASE_URL, with SQLite as the local default and PostgreSQL after deployment.
* Validate required text fields, confidence between 0 and 1, and the allowed decisions pending, approved, and rejected.
* Use POST requests for create, update, and delete operations.
* Expose /health and return an error status if the database cannot be reached.
* Keep secrets and connection strings outside the repository.
* Deploy with Render's native Python runtime. Do not add a Dockerfile.

## Milestones

### 1. Data Model

Define the review fields and initialize a local SQLite database. Add two or three records manually and inspect them through the application.

### 2. Web Workflow

Build the dashboard, create form, edit form, status totals, empty state, and delete confirmation. Test invalid input as well as the successful path.

### 3. Hosted Database

Add a Render Blueprint that creates the web service and PostgreSQL database. Connect them using a managed DATABASE_URL value rather than a copied credential.

### 4. Deployment Evidence

Create one review through the public application, restart or redeploy the web service, and show that the record remains available. Check /health and inspect the service logs for one successful request.

## Deliverables

* Flask application code, templates, and CSS;
* database model and initialization command;
* tests for the dashboard, validation, editing, deletion, and health check;
* .env.example with placeholder local configuration;
* render.yaml containing the web service and database relationship; and
* reports/deployment-notes.md containing the public URL, persistence evidence, one observed limitation, and confirmation that resources were removed or intentionally retained.

Do not commit real secrets, copied database URLs, or local database files.

## Acceptance Checklist

* The app starts locally with SQLite and no cloud account.
* A reviewer can create, read, update, and delete reviews in the browser.
* Invalid form data is rejected with a helpful message.
* The deployed app uses PostgreSQL rather than a SQLite file.
* /health verifies database connectivity.
* A saved review remains after a service restart or redeploy.
* No Dockerfile or container build is required.
* The deployment notes include cleanup and cost-awareness evidence.

## Reflection

In your deployment notes, explain why a local SQLite file is useful during development but unsuitable for a free Render web service with an ephemeral filesystem. Then identify one change needed before this application could handle sensitive production review data.
