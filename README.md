#👇🏻👇🏻This is my demo video link of project

https://drive.google.com/file/d/1n6kAcoCpXW5IYB-K_xdIgfSqnnWSggy7/view?usp=drive_link
# Personal Finance Advisor Bot

An AI-powered web application designed to help users manage personal finances through income and expense tracking, budgeting, financial goals, reports, calculations, and an AI-powered finance chatbot.

## Project Overview

Personal Finance Advisor Bot provides a centralized platform where users can organize their financial information and understand their spending more easily.

The application combines a Python/Flask backend, SQLite database, and web-based frontend with AI/NLP functionality for conversational finance assistance.

## Objectives

- Manage income and expenses in one place.
- Create and monitor personal budgets.
- Set and track financial goals.
- Review financial information through dashboards and reports.
- Perform supported financial calculations.
- Provide conversational assistance through an AI finance chatbot.
- Maintain structured financial records using a database.

## Features

### User Authentication
- User registration
- User login
- User profile management

### Income & Expense Management
- Add and manage income records
- Add and manage expense records
- Organize financial transactions

### Budget Management
- Create budgets
- Monitor spending against budgets
- Review budget-related information

### Financial Goals
- Create financial goals
- Track goal progress
- Monitor planned financial targets

### Dashboard
- Centralized financial overview
- Quick access to major finance-management features

### Reports & Analysis
- Review organized financial information
- Analyze spending and financial activity

### Finance Calculator
- Perform supported finance-related calculations

### AI Finance Chatbot
- Ask supported finance-related questions
- Receive conversational financial guidance using the implemented AI/NLP functionality

## Technologies Used

- **Python** – Core programming language
- **Flask** – Backend web framework
- **SQLite** – Database
- **HTML** – Web-page structure
- **CSS** – User interface styling
- **JavaScript** – Frontend interactivity
- **AI/NLP** – Finance chatbot functionality
- **Git & GitHub** – Source-code management and repository hosting

## Project Structure

```text
personal-finance-advisor-bot/
├── models/              # Database/application models
├── routes/              # Application routes
├── services/            # Application/business services
├── static/              # CSS, JavaScript and static resources
├── templates/           # HTML templates
├── tests/               # Testing resources
├── app.py               # Main Flask application
├── config.py            # Application configuration
├── finance_bot.db       # SQLite database
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment configuration
└── .gitignore           # Git ignored files

Installation & Setup
Prerequisites
Python 3.x
VS Code or another Python-compatible IDE
Internet connection for installing dependencies and any configured external services
Steps
Clone or download this repository.
Open the project folder in VS Code.
Create a virtual environment if required:
python -m venv venv
Activate the virtual environment.
Windows:
venv\Scripts\activate
Install the required dependencies:
pip install -r requirements.txt
Configure environment variables using .env.example where required.
Start the application:
python app.py
Open the local URL displayed by Flask in your browser.
Basic Workflow
User
  ↓
Registration / Login
  ↓
Dashboard
  ↓
Income & Expense Management
  ↓
Budgets / Financial Goals
  ↓
Reports & Analysis
  ↓
Finance Calculator / AI Chatbot
  ↓
SQLite Database
Inputs
User registration/login information
Income details
Expense details
Budget information
Financial goal information
Calculator inputs
Finance-related chatbot questions
Outputs
Dashboard information
Income and expense records
Budget information
Goal progress
Reports and financial analysis
Calculator results
AI chatbot responses
Future Enhancements
Secure bank-account/API integrations
AI-based spending predictions
Personalized financial insights
Advanced data visualization
Mobile application
Notifications and reminders
Multi-currency support
Additional report export formats
Improved automated testing and deployment
Security & Privacy
Never upload API keys, passwords, or secret tokens to the repository.
Use environment variables for sensitive configuration.
Avoid storing real private financial information in a public repository.
Validate and protect user-provided data appropriately.
Disclaimer
This project is intended for educational, organizational, and informational purposes. Information provided by the application or AI chatbot should not be considered guaranteed financial advice or a substitute for advice from a qualified financial professional.
Project Status
Status: Completed project prototype / Capstone Project
