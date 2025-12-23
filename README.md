# AirHost Pro - Management Information System

## Overview
AirHost Pro is a "High-White Minimalist" property management system designed to help managers track revenue, occupancy, and maintenance tasks efficiently.

## Features
- **Dashboard**: RevPAR tracking, Occupancy rates, and intelligent alerts (Decision Support System).
- **Properties**: Grid view of all managed properties with status indicators.
- **Calendar**: Reservation tracking.
- **Reports**: P&L Statements per property.

## How to Run
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Initialize Database**:
   The database should already be seeded. To reset:
   ```bash
   python seed.py
   ```
3. **Run the Application**:
   ```bash
   python app.py
   ```
4. **Access the App**:
   Open your browser and navigate to `http://127.0.0.1:5000`

## Technology Stack
- **Backend**: Python (Flask), SQLite (SQLAlchemy)
- **Frontend**: HTML5, Tailwind CSS (CDN), Lucide Icons
- **Design logic**: High-White Minimalism
