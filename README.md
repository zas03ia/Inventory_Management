# Django Project: Inventory Management System

## Project Overview
The Inventory Management System is a Django-based application designed to streamline inventory management across multiple locations efficiently. This system leverages the Django Admin interface for convenient administration, uses database partitioning for scalability and custom data segmentation, and incorporates the PostGIS extension to support geospatial features such as tracking and mapping inventory distribution.

## Features
- **User Management**: Role-based user authentication and authorization.
- **Inventory Management**: CRUD operations for items, locations, and partitions.
- **Admin Panel**: A dedicated Django admin panel for quick data operations.
- **Reporting**: Generate reports based on inventory data.
- **Test Coverage**: Includes unit tests for robust code reliability.
- **Dockerized Deployment**: Docker support for isolated environment setup.
```

## Setup Instructions

### Prerequisites
1. Python 3.10 or higher
2. Docker and Docker Compose (optional for containerized setup)
3. PostgreSQL (or your preferred database)
4. Git

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/zas03ia/Inventory_Management.git
   ```

### Using Docker
1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Use Docker bash:
   ```bash
   docker exec -it django_app bash
   ```
3. Migrate:
   ```docker bash
   python manage.py migrate
   ```
4. Load initial data:
   ```docker bash
   python manage.py loaddata location/fixtures/initial_data.json
   ```

5. Generate sitemap from location data:
  ```docker bash
  python manage.py generate_sitemap
   ```

6. Access the application at `http://localhost:8000`.

### Checking partitions
1. Use psql to interact with database:
  ```
  docker exec -it inventory_db_container psql -U <password> -d <database_name>
  ```
2. Run the following:
  ```
  SELECT child.relname AS partition_name
  FROM pg_inherits
  JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
  JOIN pg_class child ON pg_inherits.inhrelid = child.oid
  WHERE parent.relname = 'location_accommodation';
  ```

  ```
  SELECT tableoid::regclass, COUNT(*)
  FROM loaction_accommodation
  GROUP BY tableoid;
  ```
  ```
  SELECT child.relname AS partition_name
  FROM pg_inherits
  JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
  JOIN pg_class child ON pg_inherits.inhrelid = child.oid
  WHERE parent.relname = 'location_localizeaccommodation';
  ```
  ```
  SELECT tableoid::regclass, COUNT(*)
  FROM loaction_localizeaccommodation
  GROUP BY tableoid;
  ```


### Running Tests
Run all tests to ensure the application is working correctly:
```bash
python manage.py test
coverage report
```

## Usage
- Navigate to `http://127.0.0.1:8000/admin` to access the admin panel.
- Use the API endpoints for inventory operations (check `urls.py` for endpoints).
- Upload or manage inventory via the example CSV file (`example_location.csv`).


