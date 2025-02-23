# 🚀 Full Stack Project Setup Guide

A modern full-stack application built with Django and React+Vite.

## 📋 Prerequisites

- Python 3.12 or higher
- Node.js 16 or higher
- pip (Python package manager)
- npm (Node package manager)

## 🛠️ Backend Setup

### Virtual Environment

Create and activate a Python virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Installation

```bash
# Install required packages
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Run database migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

The backend server will be available at `http://localhost:8000`.

## 🎨 Frontend Setup

### Installation and Development

```bash
# Navigate to frontend directory
cd web-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend development server will be available at `http://localhost:5173`.

## 📂 Project Structure

```
project-root/
├── backend/                 # Django backend
│   ├── manage.py           # Django management script
│   ├── app_name/           # Main Django application
│   ├── static/             # Static assets
│   └── templates/          # HTML templates
│
├── web-frontend/           # React frontend
│   ├── src/               # Source code
│   ├── public/            # Public assets
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
│
├── requirements.txt        # Python dependencies
└── README.md              # This file
```
