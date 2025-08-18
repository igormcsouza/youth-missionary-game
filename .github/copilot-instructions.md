# Youth Missionary Game - Streamlit Application

Youth Missionary Game is a Python Streamlit web application for managing youth missionary competitions. It provides interactive dashboards, youth/task management, and scoring systems for church youth organizations.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Dependencies
- Install Python dependencies: `pip install -r requirements.txt` -- takes 30 seconds to complete. NEVER CANCEL. Set timeout to 120+ seconds.
- **CRITICAL**: Python 3.12+ is required and tested. The application uses modern Python features.

### Running the Application
- **ALWAYS set AUTH environment variable first**: `export AUTH=your_password_here`
- Start the application: `streamlit run src/Dashboard.py`
- Application starts in under 5 seconds and runs on http://localhost:8501
- **AUTHENTICATION REQUIRED**: All management pages (except Dashboard) require entering the AUTH password

### Docker Operations
- Build Docker image: `docker build --build-arg PIP_TRUSTED_HOST=1 -t youth-missionary-game .` -- takes 30 seconds to complete. NEVER CANCEL. Set timeout to 120+ seconds.
- **CRITICAL**: In isolated environments, Docker builds WILL fail with SSL errors. ALWAYS use this workaround:
  ```bash
  docker build --build-arg PIP_TRUSTED_HOST=1 -t youth-missionary-game .
  ```
- Run containerized app: `docker run -p 8080:8080 -e AUTH=your_password youth-missionary-game`

### Validation and Testing
- Validate Python syntax: `python -m py_compile src/*.py src/pages/*.py` -- completes in under 10 seconds.
- **NO TESTING INFRASTRUCTURE EXISTS**: There are no unit tests, pytest configuration, or automated tests.
- **NO LINTING CONFIGURATION**: No pylint, flake8, black, or other linting tools are configured.

## Application Structure

### Main Components
- **Entry point**: `src/Dashboard.py` - Main dashboard with analytics and charts
- **Database**: `src/database.py` - SQLModel definitions for Youth, Tasks, and Compiled data
- **Authentication**: `src/utils.py` - Password protection system
- **Management pages**: `src/pages/` directory contains:
  - `1_📁_Dados_da_Gincana.py` - Youth and task management
  - `2_📝_Registro_das_Tarefas.py` - Task completion recording

### Database Configuration
- **SQLite default**: Creates `youth_data.db` automatically on first run
- **PostgreSQL support**: Set `POSTGRESCONNECTIONSTRING` environment variable
- **Auto-table creation**: SQLModel creates all tables automatically on startup
- **No migrations**: Database schema changes require manual intervention

## Validation Scenarios

### ALWAYS Test Authentication Flow
1. Set AUTH environment variable: `export AUTH=testpassword123`
2. Start application: `streamlit run src/Dashboard.py`
3. Navigate to http://localhost:8501/Dados_da_Gincana
4. Enter the password when prompted
5. Verify access to Youth and Task management features

### ALWAYS Test Complete User Workflow
1. **Add a Youth**: Go to "Dados da Gincana" page, add a youth with name, age, organization
2. **Add a Task**: On same page, add a task with name, points, repeatable setting
3. **Record Completion**: Go to "Registro das Tarefas" page, select youth and task, add quantity and bonus
4. **View Results**: Return to Dashboard to see updated rankings and charts

### ALWAYS Verify Navigation and Display
- Dashboard should show empty states with "Nenhum jovem cadastrado ainda" when no data exists
- All 3 navigation links should work: Dashboard, Dados da Gincana, Registro das Tarefas
- Charts and tables should display correctly when data is present

## Common Tasks and Expected Timing

### Development Setup (First Time)
```bash
# Setup takes ~30 seconds total
export AUTH=your_password_here
pip install -r requirements.txt  # 30 seconds
streamlit run src/Dashboard.py   # <5 seconds to start
```

### Docker Deployment Testing
```bash
# Build and test takes ~40 seconds total
docker build --build-arg PIP_TRUSTED_HOST=1 -t youth-missionary-game .  # 30 seconds
docker run -p 8080:8080 -e AUTH=test youth-missionary-game  # <10 seconds
```

### Code Validation
```bash
# Validation takes <10 seconds
python -m py_compile src/*.py src/pages/*.py
```

## Key Environment Variables
- **AUTH** (required): Password for accessing management pages
- **POSTGRESCONNECTIONSTRING** (optional): PostgreSQL database URL, defaults to SQLite

## Deployment Information
- **Fly.io deployment**: Configured in `fly.toml` and `.github/workflows/deploy.yml`
- **Docker port**: Application runs on port 8080 in containers
- **Local port**: Application runs on port 8501 locally
- **Auto-deployment**: GitHub Actions deploys to Fly.io on main branch pushes

## Important Limitations
- **No automated testing**: Manual validation required for all changes
- **No linting tools**: Code style validation must be done manually
- **Password in environment**: AUTH password must be set as environment variable
- **Docker SSL issues**: Builds may require trusted-host workarounds in restricted environments
- **Database migrations**: No automated migration system - schema changes need manual handling

## Troubleshooting
- **"Password field not in form" console warning**: This is expected behavior, can be ignored
- **SSL certificate errors during Docker build**: ALWAYS use `--build-arg PIP_TRUSTED_HOST=1` flag
- **Empty dropdowns in task recording**: Ensure youth and tasks are created first in management page
- **Database connection errors**: Check POSTGRESCONNECTIONSTRING format or fallback to SQLite default