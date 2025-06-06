# DataBaseProject

## Overview
DataBaseProject is a web application that allows users to register, log in, update their information, and withdraw their accounts. The application is structured into a backend and a frontend, with the backend handling the server-side logic and the frontend providing the user interface.

## Project Structure
```
DataBaseProject
├── backend
│   └── app
│       ├── routes
│       │   └── auth.py
│       └── models
│           └── user.py
├── frontend
│   ├── index.html
│   ├── update_user.html
│   ├── js
│   │   ├── main.js
│   │   └── update_user.js
│   └── css
│       └── style.css
└── README.md
```

## Features
- **User Registration**: Users can create a new account by providing an email and password.
- **User Login**: Users can log in using their registered email and password.
- **Update User Information**: Users can update their email, password, and notification preferences.
- **Withdraw Account**: Users can delete their account and all associated data.

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd DataBaseProject
   ```
3. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the backend server:
   ```
   python -m flask run
   ```
6. Open `frontend/index.html` in a web browser to access the application.

## Usage
- Navigate to the registration page to create a new account.
- Use the login page to access your account.
- Go to the "Update User Information" page to modify your account details.
- If you wish to delete your account, use the withdrawal feature.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.