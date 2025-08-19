# Youth Missionary Game

[![Deploy to Fly.io](https://github.com/igormcsouza/youth-missionary-game/actions/workflows/deploy.yml/badge.svg)](https://github.com/igormcsouza/youth-missionary-game/actions/workflows/deploy.yml)
[![Test Suite](https://github.com/igormcsouza/youth-missionary-game/actions/workflows/test.yml/badge.svg)](https://github.com/igormcsouza/youth-missionary-game/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/igormcsouza/youth-missionary-game/branch/main/graph/badge.svg)](https://codecov.io/gh/igormcsouza/youth-missionary-game)

A Streamlit-based web application for managing youth missionary competitions. This app allows you to register youth participants, create tasks with scoring systems, track task completions, and view interactive dashboards with rankings and statistics.

## Features

- **Youth Registration**: Register participants with name, age, and organization (Rapazes/Moças)
- **Task Management**: Create tasks with customizable points and repeatability settings
- **Task Tracking**: Record task completions with quantity and bonus points
- **Interactive Dashboard**: View rankings, statistics, and charts
- **Database Support**: SQLite for development, PostgreSQL for production
- **Authentication**: Password protection for admin functions
- **Automatic Deployment**: Continuous deployment to Fly.io

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/igormcsouza/youth-missionary-game.git
   cd youth-missionary-game
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up authentication (optional for development):**
   ```bash
   export AUTH="your-password-here"
   ```

4. **Run the application:**
   ```bash
   streamlit run src/Dashboard.py
   ```

5. **Open your browser and navigate to:** `http://localhost:8501`

## Development Setup

### Database Configuration

The application uses SQLite by default for local development. For production or testing with PostgreSQL:

1. **Set up PostgreSQL connection:**
   ```bash
   export POSTGRESCONNECTIONSTRING="postgresql://user:password@host:port/database"
   ```

2. **Create a database proxy for development (if using Fly.io PostgreSQL):**
   ```bash
   flyctl proxy 5430:5432 -a youth-missionary-game-database
   ```
   Then connect using: `postgresql://user:password@localhost:5430/database`

### Environment Variables

- `AUTH` - Password for accessing admin functions (required in production)
- `POSTGRESCONNECTIONSTRING` - PostgreSQL connection string (optional, defaults to SQLite)

### Project Structure

The application follows a standard Streamlit multi-page structure:

- `src/Dashboard.py` - Main dashboard with rankings and statistics
- `src/pages/1_📁_Dados_da_Gincana.py` - Youth and task registration
- `src/pages/2_📝_Registro_das_Tarefas.py` - Task completion tracking
- `src/database.py` - Database models and repositories
- `src/utils.py` - Utility functions including authentication

## Deployment

### Automatic Deployment

The application automatically deploys to Fly.io on every push to the main branch via GitHub Actions.

### Manual Deployment

1. **Install Fly CLI and authenticate:**
   ```bash
   flyctl auth login
   ```

2. **Deploy the application:**
   ```bash
   flyctl deploy
   ```

### Environment Setup for Production

Set the following secrets in your Fly.io app:
```bash
flyctl secrets set AUTH="your-production-password"
flyctl secrets set POSTGRESCONNECTIONSTRING="your-postgres-connection-string"
```

## Usage

1. **Access the application** - Navigate to the deployed URL or localhost:8501
2. **Enter password** - Use the AUTH environment variable password
3. **Register participants** - Go to "📁 Dados da Gincana" to add youth and tasks
4. **Track activities** - Use "📝 Registro das Tarefas" to record task completions
5. **View results** - Check the main Dashboard for rankings and statistics

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test locally
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Testing

This project includes comprehensive testing with pytest and coverage reporting. Tests are automatically run on every push and pull request.

- **Run tests locally**: `pytest tests/ --cov=src --cov-report=term-missing -v`
- **Current coverage**: 87% (target: 85%+)
- **Test categories**: Unit tests, integration tests, Streamlit UI tests

See [TESTING.md](TESTING.md) for detailed testing documentation.

### Setting Up Code Coverage (Codecov)

To enable coverage reporting with Codecov badges:

1. **Sign up for Codecov**: Go to [codecov.io](https://codecov.io) and sign in with your GitHub account
2. **Add your repository**: Find `igormcsouza/youth-missionary-game` in your Codecov dashboard
3. **Get the upload token**: Copy the repository upload token from your Codecov settings
4. **Add GitHub secret**: 
   - Go to your GitHub repository Settings → Secrets and variables → Actions
   - Add a new repository secret named `CODECOV_TOKEN` with the upload token value
5. **Enable uploads**: The workflow is already configured to upload coverage data automatically

The coverage badge will start working once the first successful upload completes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.