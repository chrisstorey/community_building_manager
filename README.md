# Community Building Manager

A FastAPI-based service for managing community buildings, tracking maintenance activities, and coordinating asset management across multiple locations.

## Features

- **User Management**: Role-based access control (Admin, Manager, Viewer)
- **Organization Hierarchy**: Support for parent-child organization relationships
- **Location Management**: Track multiple buildings with asset allocations
- **Asset Tracking**: Manage building assets with maintenance templates
- **Work Item Management**: Generate maintenance items from markdown templates
- **Dashboard**: Real-time view of outstanding and upcoming actions
- **Responsive UI**: Bootstrap 5-based interface with WCAG 2.1 AA accessibility
- **12-Factor Compliance**: Environment-based configuration

## Architecture

### Technology Stack

- **Backend**: Python 3.13+ with FastAPI 0.115+
- **Package Manager**: UV (fast Python package management)
- **ORM**: SQLModel with SQLAlchemy (SQLite for development, PostgreSQL for production)
- **Authentication**: JWT tokens with argon2 password hashing
- **Frontend**: HTML5, CSS3 (Bootstrap 5), Vanilla JavaScript
- **Testing**: pytest with async support

### Project Structure

```
community_building_manager/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── organization.py
│   │   └── work.py
│   ├── schemas/             # Pydantic validation schemas
│   ├── services/            # Business logic
│   ├── api/                 # API route handlers
│   ├── core/                # Security and dependencies
│   └── db/                  # Database setup and utilities
├── static/                  # CSS, JavaScript, images
├── templates/               # HTML templates
├── tests/                   # Pytest test suite
├── pyproject.toml          # Project metadata and dependencies
├── .env.example            # Example environment variables
└── README.md
```

## Installation

### Prerequisites

- Python 3.13 or higher (3.12 supported but 3.13+ recommended for better compatibility)
- UV package manager (install from https://docs.astral.sh/uv/)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd community_building_manager
   ```

2. **Create environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Create virtual environment and install dependencies**
   ```bash
   uv venv --python 3.13
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

4. **Run migrations**
   The database tables are automatically created on first run.

5. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## Usage

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

1. **Register** a new user
   ```bash
   POST /auth/register
   {
     "email": "user@example.com",
     "password": "securepassword",
     "full_name": "User Name",
     "organization_id": 1
   }
   ```

2. **Login** to get a token
   ```bash
   POST /auth/login
   {
     "email": "user@example.com",
     "password": "securepassword"
   }
   ```

3. **Use token** in headers
   ```bash
   Authorization: Bearer <access_token>
   ```

### Managing Organizations

- **Create organization**
  ```bash
  POST /organizations
  {
    "name": "Community Center",
    "address": "123 Main St"
  }
  ```

- **Create location**
  ```bash
  POST /organizations/{org_id}/locations
  {
    "name": "Main Building",
    "address": "123 Main St, Building A"
  }
  ```

### Locations Management

**Location Features:**
- Create and manage multiple locations for your organization
- Track location details including:
  - Address and GPS coordinates (latitude/longitude)
  - Operating hours
  - Capacity information
  - Contact person, phone, and email
  - Status (active, inactive, under_maintenance)
- Search locations by name or address
- Filter locations by status
- Soft delete locations (non-destructive)

**API Endpoints:**
```bash
# Create location
POST /organizations/{org_id}/locations
{
  "name": "Scout HQ",
  "address": "123 Main St",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "status": "active",
  "opening_hours": "Mon-Fri 09:00-17:00",
  "capacity": 100,
  "contact_person": "John Doe",
  "contact_phone": "555-1234",
  "contact_email": "john@example.com"
}

# List locations for organization
GET /organizations/{org_id}/locations

# Get location details
GET /organizations/locations/{location_id}

# Update location
PATCH /organizations/locations/{location_id}

# Delete location (soft delete)
DELETE /organizations/locations/{location_id}

# Search locations
GET /organizations/locations/search?q=scout&status_filter=active
```

**UI:** Access locations management at http://localhost:8000/locations

### Asset Types and Work Items

Asset types are defined with markdown templates that structure maintenance work. The system includes predefined asset types for scout organizations:

- **Scout HQ** - Scout headquarters building
- **Church** - Church building
- **Church Hall** - Church hall/community center
- **Scout Activity Centre** - Scout activity and training centre

Each asset type includes maintenance templates with organized areas and checklist items:

```markdown
## Area: Roof
- Inspect for leaks
- Check gutters
- Clear debris

## Area: HVAC System
- Change filters monthly
- Service annually
- Check thermostat
```

When an asset is added to a location, work areas and items are automatically generated from the template.

**API Endpoints:**
```bash
# Create asset type
POST /asset-types
{
  "name": "Custom Building",
  "description": "Description of the building type",
  "template": "## Area: Section1\n- Task 1\n- Task 2"
}

# Initialize default scout asset types
POST /asset-types/initialize-defaults

# List asset types
GET /asset-types

# Get asset type details
GET /asset-types/{asset_type_id}

# Add asset to location
POST /organizations/locations/{location_id}/assets/{asset_type_id}

# Get location assets
GET /organizations/locations/{location_id}/assets

# Remove asset from location
DELETE /organizations/locations/{location_id}/assets/{asset_id}
```

**UI:** Access asset management at http://localhost:8000/assets

### Dashboard

Access the dashboard at http://localhost:8000/dashboard to:
- View outstanding maintenance items
- See upcoming scheduled reviews
- Track completion status
- Add updates to work items

## Configuration

Environment variables in `.env`:

```
# Application
APP_NAME=Community Building Manager
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///./community_manager.db
# For PostgreSQL: postgresql://user:password@localhost/dbname

# JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app
```

## Development

### Database Migrations

The application uses SQLAlchemy with automatic table creation. To modify the schema:

1. Update the model in `app/models/`
2. Models are automatically registered and tables created on app start

### Adding New Endpoints

1. Create route handler in `app/api/`
2. Add request/response schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Include router in `app/main.py`

## Deployment

### Production Configuration

1. **Set environment variables**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure PostgreSQL database
   - Set appropriate CORS origins

2. **Use production ASGI server**
   ```bash
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

3. **Configure reverse proxy** (nginx)
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

Build and run with Docker:

```bash
docker build -t community-building-manager .
docker run -p 8000:8000 --env-file .env community-building-manager
```

## Brand Identity

### Color Palette

- **Primary (Deep Navy)**: #1A365D - Use for authority and structure
- **Action (Amber)**: #D97706 - Use for CTAs and "Requires Attention"
- **Success (Emerald)**: #059669 - Use for "Maintained" or "Functional"
- **Background (Cool Grey)**: #F8FAFC - Keep UI airy
- **Text (Slate)**: #1E293B - Body copy for legibility

### Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Semantic HTML markup
- Skip to main content link
- Focus indicators on interactive elements

## Contributing

1. Create feature branch from `main`
2. Make changes and add tests
3. Ensure all tests pass
4. Submit pull request with description

## License

Proprietary - Community Building Manager

## Support

For issues or questions:
- Check existing issues in the repository
- Create new issue with detailed information
- Contact development team

## Roadmap

- [ ] Email notifications for upcoming reviews
- [ ] Mobile app for field inspections
- [ ] Photo/document attachments
- [ ] Multi-language support
- [ ] Advanced reporting and analytics
- [ ] Integration with maintenance vendors
- [ ] Mobile-responsive dashboard
