# Pilot Portal

A Flask-based web application for managing pilot schedules and communications.

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example`
5. Run the application:
   ```bash
   flask run
   ```

## Deployment on Railway

1. Push your code to GitHub
2. Sign up at [Railway](https://railway.app/)
3. Create a new project
4. Select "Deploy from GitHub repo"
5. Select your repository
6. Add environment variables from your `.env` file in the Railway dashboard
7. Click "Deploy"

## Environment Variables

Required environment variables are listed in `.env.example`.

## License

Proprietary - All rights reserved.
