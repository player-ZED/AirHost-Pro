<p align="center">
  <img src="https://private-user-images.githubusercontent.com/140601000/529484814-0b89da25-ef0f-416d-8457-30f0a888ab2e.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjY0NjI4NjcsIm5iZiI6MTc2NjQ2MjU2NywicGF0aCI6Ii8xNDA2MDEwMDAvNTI5NDg0ODE0LTBiODlkYTI1LWVmMGYtNDE2ZC04NDU3LTMwZjBhODg4YWIyZS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjIzJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIyM1QwNDAyNDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT02NjNjNTdiNmYwNTlkZGU1YWEwYjYyYmVmZTA2ZTdmNTJlMThlZWEyYmIyMTBlNzAxMzFjMGIyZjBjMTM5ZWEzJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.rgBxG6mtwwZrnCsNK_1Sn0lHBb_c_Y7GZ0rrLL08elE" alt="AirHost Pro Banner" width="800"/>
</p>

# AirHost Pro - Management Information System

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/) 
[![Flask](https://img.shields.io/badge/Flask-2.x-orange?logo=flask&logoColor=white)](https://flask.palletsprojects.com/) 
[![SQLite](https://img.shields.io/badge/SQLite-3.0-lightgrey?logo=sqlite&logoColor=blue)](https://www.sqlite.org/) 

---

##  Overview

**AirHost Pro** is a comprehensive property management system designed for short-term rental operations across vacation homes and urban properties. Built with a **High-White Minimalist** design philosophy, it centralizes information flow to support tactical and strategic decision-making for distributed property portfolios.

Unlike traditional spreadsheet-based workflows, AirHost Pro provides real-time tracking of revenue metrics, occupancy rates, and operational status—eliminating data fragmentation and decision latency.

---

##  Key Objectives

- **Operational Excellence**: Unified dashboard for real-time property status tracking (Clean/Dirty/Maintenance)
- **Decision Intelligence**: Automated Decision Support System (DSS) monitoring occupancy trends and flagging underperforming properties (<30% occupancy)
- **Financial Transparency**: Automated P&L reports per property with RevPAR calculations
- **User-Centric Design**: Lightweight web interface requiring minimal training for non-technical staff

---

##  Core Features

###  Dashboard
- **RevPAR Tracking**: Real-time revenue per available room calculations
- **Occupancy Metrics**: Current and historical occupancy rate monitoring
- **Smart Alerts**: DSS-powered notifications for low-performance periods requiring pricing intervention

###  Property Management
- Grid view of all managed properties with live status indicators
- Quick-access property details and performance metrics
- Status tracking for cleaning, maintenance, and availability

###  Reservation Calendar
- Visual timeline of guest check-ins and check-outs
- Turnaround time optimization for cleaning staff
- Conflict detection and scheduling assistance

### 📈 Executive Reports
- Automated monthly P&L statement generation per property
- Net profit calculations and trend analysis
- Data-driven insights for asset allocation decisions

---

##  Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.x, Flask 2.x |
| **Database** | SQLite 3.0, SQLAlchemy ORM |
| **Frontend** | HTML5, Tailwind CSS, Lucide Icons |
| **Architecture** | MVC Pattern, RESTful Design |

---

##  Getting Started

### Prerequisites
- Python 3.x installed on your system
- Basic understanding of Flask applications

### Installation

**1️ Clone the Repository**
```bash
git clone https://github.com/player-ZED/airhost-pro.git
cd airhost-pro
```

**Install Dependencies**
```bash
pip install -r requirements.txt
```

**Initialize Database**
The database comes pre-seeded with sample data. To reset:
```bash
python seed.py
```

**Run the Application**
```bash
python app.py
```

**Access the Interface**
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

##  Project Structure

```
AirHost-Pro/
├── app.py              # Main Flask application
├── models.py           # Database models and schema
├── seed.py             # Database seeding script
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── static/             # CSS, JS, and assets
├── MIS-Project.docx    # Project documentation
└── REPORT_DRAFT.md     # Detailed project report
```

---

##  Design Philosophy

AirHost Pro embraces **High-White Minimalism** to ensure:
- Reduced cognitive load for daily operations
- Focus on critical metrics without visual clutter
- Professional appearance suitable for executive reporting
- Responsive design for tablet and desktop use

---

##  System Scope

###  Current Features
- Reservation management (Guest-In/Guest-Out tracking)
- Property operations (Status and maintenance tracking)
- Financial intelligence (RevPAR and Net Profit calculations)
- Executive reporting (Monthly P&L generation)

###  Future Roadmap
- Payment processing integration (Stripe)
- Channel management (Airbnb/Booking.com API sync)
- Mobile application for field staff
- Advanced analytics and forecasting

---

##  Problem Statement

Traditional property management relies on manual spreadsheets and fragmented communication channels, leading to:
- **Data Silos**: Financial data separated from booking schedules and property status
- **Decision Latency**: Monthly manual RevPAR calculations detect issues too late
- **Operational Delays**: Staff lack real-time check-out visibility
- **Revenue Leakage**: No automated alerts for pricing optimization opportunities

AirHost Pro solves these challenges through centralized data management and intelligent automation.

---

##  License

This project is developed for educational and internal management purposes.

---

##  Contact

For questions or support, please refer to the project documentation or contact the development team.

---

<p align="center">Made with ❤️ for Modern Property Management</p>
