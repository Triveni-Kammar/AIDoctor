# Setup and Deployment Guide

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python**: 3.9 or higher
- **Node.js**: 16.x or higher
- **npm**: 7.x or higher
- **PostgreSQL**: 13.x or higher (or MySQL if preferred)
- **Git**: For version control

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd PalAss
```

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file with your actual values:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/palass
LLM_MODEL=llama-3.1-8b-instant
SECRET_KEY=your-secret-key-here-generate-a-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Getting Groq API Key**:
1. Visit https://console.groq.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into your `.env` file

### 2.4 Set Up Database

#### PostgreSQL Setup

**Install PostgreSQL** (if not already installed):
- Windows: Download from https://www.postgresql.org/download/windows/
- macOS: `brew install postgresql`
- Linux: `sudo apt-get install postgresql postgresql-contrib`

**Create Database**:
```bash
# Start PostgreSQL service
# On Windows: Start PostgreSQL service from Services
# On macOS: brew services start postgresql
# On Linux: sudo service postgresql start

# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE palass;

# Exit
\q
```

#### Initialize Database with Seed Data

```bash
cd backend
python init_db.py
```

This will create all tables and populate them with sample data for testing.

### 2.5 Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

**Verify Backend**:
- Visit `http://localhost:8000` - Should return API info
- Visit `http://localhost:8000/docs` - Interactive API documentation
- Visit `http://localhost:8000/health` - Health check endpoint

## Step 3: Frontend Setup

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
cd frontend
cp .env.example .env
```

Edit the `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000
```

### 3.3 Start Frontend Development Server

```bash
cd frontend
npm start
```

The frontend will be available at `http://localhost:3000`

## Step 4: Verify Integration

1. Open `http://localhost:3000` in your browser
2. You should see the "Log HCP Interaction" screen
3. Test the AI chat panel by typing a description like:
   ```
   Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure
   ```
4. The AI should automatically fill the form fields
5. Test corrections by typing in the chat:
   ```
   Change the sentiment to Neutral
   ```
6. The AI should update the form accordingly

## Step 5: Production Deployment

### Backend Deployment (Optional)

For production deployment, consider:

**Docker Deployment**:
```dockerfile
# Dockerfile for backend
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run**:
```bash
docker build -t palass-backend .
docker run -p 8000:8000 --env-file .env palass-backend
```

**Cloud Deployment Options**:
- **AWS**: Use EC2, ECS, or App Runner
- **Google Cloud**: Use Cloud Run or Compute Engine
- **Azure**: Use Azure App Service or Container Instances
- **Heroku**: Direct deployment with Procfile

### Frontend Deployment

**Build for Production**:
```bash
cd frontend
npm run build
```

**Serve Static Files**:
- Use Nginx, Apache, or any static file server
- Or deploy to:
  - **Netlify**: Drag and drop the `build` folder
  - **Vercel**: Connect Git repository
  - **AWS S3**: Upload `build` folder contents
  - **GitHub Pages**: Use gh-pages branch

### Database Deployment

For production database:

**Managed PostgreSQL Services**:
- AWS RDS
- Google Cloud SQL
- Azure Database for PostgreSQL
- Heroku Postgres
- Supabase

**Update DATABASE_URL** in production `.env`:
```env
DATABASE_URL=postgresql://user:password@production-host:5432/palass
```

## Troubleshooting

### Common Issues

**1. Backend won't start**
- Check if port 8000 is already in use
- Verify Python dependencies are installed
- Check `.env` file exists and is valid

**2. Database connection errors**
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Ensure database `palass` exists
- Verify credentials are correct

**3. Groq API errors**
- Verify GROQ_API_KEY is correct
- Check if you have API credits
- Verify network connectivity

**4. Frontend can't connect to backend**
- Check REACT_APP_API_URL in frontend `.env`
- Verify backend is running
- Check CORS settings in backend

**5. TailwindCSS not working**
- Ensure Tailwind dependencies are installed
- Check `tailwind.config.js` is correct
- Verify `postcss.config.js` exists
- Restart frontend dev server

## Development Workflow

### Making Changes

**Backend Changes**:
1. Modify code in `backend/app/`
2. Backend auto-reloads with `--reload` flag
3. Test changes at `http://localhost:8000/docs`

**Frontend Changes**:
1. Modify code in `frontend/src/`
2. Frontend hot-reloads automatically
3. View changes at `http://localhost:3000`

### Database Migrations

For schema changes in production:

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Testing

**Backend Testing**:
```bash
cd backend
pytest
```

**Frontend Testing**:
```bash
cd frontend
npm test
```

## Security Considerations

1. **Never commit `.env` files** to version control
2. **Use strong secrets** for SECRET_KEY
3. **Enable HTTPS** in production
4. **Implement rate limiting** for API endpoints
5. **Use environment-specific configurations**
6. **Regularly update dependencies** for security patches
7. **Implement proper authentication** (not included in this demo)

## Performance Optimization

1. **Enable database connection pooling**
2. **Implement caching** for frequently accessed data
3. **Use CDN** for static assets in production
4. **Enable compression** for API responses
5. **Optimize LLM calls** with batching where possible
6. **Implement pagination** for large datasets

## Monitoring and Logging

1. **Set up application monitoring** (e.g., Sentry, DataDog)
2. **Implement structured logging**
3. **Monitor API response times**
4. **Track LLM API usage and costs**
5. **Set up database performance monitoring**

## Support

For issues or questions:
- Check the main README.md
- Review LangGraph documentation
- Check Groq API documentation
- Review FastAPI documentation
- Check React documentation

## License

This project is part of an assignment submission. See LICENSE file for details.
