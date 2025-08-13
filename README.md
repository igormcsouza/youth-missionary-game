# Youth Missionary Game Streamlit App

This is a Streamlit application designed as a youth missionary game, providing interactive activities and resources to engage young participants in missionary work.

## Project Structure

```
my-streamlit-app
├── src
│   └── app.py
├── requirements.txt
├── fly.toml
└── README.md
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd my-streamlit-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```
   streamlit run src/Dashboard.py
   ```

## Deployment

To deploy the application to Fly.io, ensure you have the Fly CLI installed and configured. Then, run the following command:

```
fly deploy
```

## Usage

After running the app, open your web browser and navigate to `http://localhost:8501` to view the application. You should see "Hello, World!" displayed on the page.