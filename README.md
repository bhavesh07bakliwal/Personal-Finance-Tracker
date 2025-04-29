# Personal Finance Tracker

A web application for tracking personal finances, built with Flask and MongoDB.

## Features

- User authentication (login/register)
- Add income and expenses
- View transaction history
- Visualize spending patterns with charts
- Track total income, expenses, and savings
- Categorize transactions
- Delete transactions

## Tech Stack

- Backend: Python/Flask
- Database: MongoDB
- Frontend: HTML, CSS, JavaScript
- Charts: Plotly.js
- UI Framework: Bootstrap 5

## Prerequisites

- Python 3.8+
- MongoDB
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd finance-tracker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017/
```

5. Start MongoDB:
```bash
# On Windows
mongod

# On Linux/Mac
sudo service mongod start
```

6. Run the application:
```bash
python app.py
```

7. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Register a new account or login with existing credentials
2. Add transactions using the form on the dashboard
3. View your financial summary and charts
4. Track your spending patterns and savings

## Project Structure

```
finance-tracker/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── README.md          # Project documentation
└── templates/         # HTML templates
    ├── base.html      # Base template
    ├── dashboard.html # Dashboard page
    ├── login.html     # Login page
    └── register.html  # Registration page
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request
