from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from models import db, Property, Reservation, Financial, Staff, Log, Settings
from datetime import datetime, timedelta, date
import os
import random
import time
import calendar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///airhost.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

db.init_app(app)

# --- Global Simulation State ---
last_simulation_time = time.time()
simulation_counter = 0

# Helper Functions
def run_simulation(force=False):
    """Autonomous MIS: Handles bookings, checkouts, cleaning, maintenance, pricing."""
    global simulation_counter
    simulation_counter += 1
    
    # Run multiple events per poll to create activity
    events_this_cycle = []
    
    # 30% chance of event per poll
    if random.random() < 0.3:
        prop = Property.query.order_by(db.func.random()).first()
        if not prop: return None

        event_type = random.choice(['booking', 'checkout', 'auto_clean', 'maintenance_detect', 'maintenance_fix', 'price_optimize'])
        
        if event_type == 'booking':
            check_in = date.today() + timedelta(days=random.randint(1, 45))
            check_out = check_in + timedelta(days=random.randint(2, 7))
            amount = prop.base_price * (check_out - check_in).days
            
            res = Reservation(
                property_id=prop.id,
                guest_name=f"Guest-{random.randint(1000,9999)}",
                check_in=check_in,
                check_out=check_out,
                amount_paid=amount
            )
            db.session.add(res)
            db.session.add(Financial(property_id=prop.id, category='Income', amount=amount, date=check_in))
            
            msg = f"✓ New booking confirmed: {prop.title} | Guest arrives {check_in.strftime('%b %d')} | ${int(amount)}"
            db.session.add(Log(event_type="Operations", category="Booking", message=msg))
            events_this_cycle.append(msg)
            
        elif event_type == 'checkout':
            if prop.status == 'Clean':
                prop.status = 'Dirty'
                msg = f"⚠ Guest checked out from {prop.title} - Property marked DIRTY"
                db.session.add(Log(event_type="Operations", category="Alert", message=msg))
                events_this_cycle.append(msg)
                
                # IMMEDIATE AUTO-DISPATCH CLEANER
                cleaner = Staff.query.filter_by(role='Cleaner').order_by(db.func.random()).first()
                if cleaner:
                    dispatch_msg = f"🔔 MIS AUTO-DISPATCH: {cleaner.name} assigned to clean {prop.title}"
                    db.session.add(Log(event_type="Operations", category="System", message=dispatch_msg))
                    events_this_cycle.append(dispatch_msg)
        
        elif event_type == 'auto_clean':
            if prop.status == 'Dirty':
                cleaner = Staff.query.filter_by(role='Cleaner').order_by(db.func.random()).first()
                cleaner_name = cleaner.name if cleaner else "Staff"
                prop.status = 'Clean'
                msg = f"✨ {cleaner_name} completed cleaning {prop.title} - Ready for next guest"
                db.session.add(Log(event_type="Operations", category="Maintenance", message=msg))
                db.session.add(Financial(property_id=prop.id, category='Cleaning', amount=50, date=date.today()))
                events_this_cycle.append(msg)

        elif event_type == 'maintenance_detect':
            if prop.status == 'Clean':
                prop.status = 'Maintenance'
                msg = f"🔧 ALERT: {prop.title} - Plumbing issue detected by smart sensors"
                db.session.add(Log(event_type="Operations", category="Alert", message=msg))
                events_this_cycle.append(msg)
                
                # AUTO-DISPATCH MAINTENANCE
                tech = Staff.query.filter_by(role='Maintenance').order_by(db.func.random()).first()
                if tech:
                    dispatch_msg = f"🔔 MIS AUTO-DISPATCH: {tech.name} assigned to repair {prop.title}"
                    db.session.add(Log(event_type="Operations", category="System", message=dispatch_msg))
                    events_this_cycle.append(dispatch_msg)

        elif event_type == 'maintenance_fix':
            if prop.status == 'Maintenance':
                tech = Staff.query.filter_by(role='Maintenance').order_by(db.func.random()).first()
                tech_name = tech.name if tech else "Technician"
                prop.status = 'Clean'
                msg = f"✓ {tech_name} fixed {prop.title} - Issue resolved, property operational"
                db.session.add(Log(event_type="Operations", category="Maintenance", message=msg))
                db.session.add(Financial(property_id=prop.id, category='Repair', amount=random.randint(100, 300), date=date.today()))
                events_this_cycle.append(msg)

        elif event_type == 'price_optimize':
            # AUTONOMOUS PRICING DECISION
            today = date.today()
            next_30 = today + timedelta(days=30)
            
            # Calculate occupancy
            booked_days = 0
            reservations = Reservation.query.filter(
                Reservation.property_id == prop.id,
                Reservation.check_in < next_30,
                Reservation.check_out > today
            ).all()
            
            for res in reservations:
                start = max(res.check_in, today)
                end = min(res.check_out, next_30)
                if end > start:
                    booked_days += (end - start).days
            
            occupancy_pct = (booked_days / 30) * 100
            old_price = prop.base_price
            
            # INTELLIGENT PRICING LOGIC
            if occupancy_pct < 20:
                # Low demand - reduce price
                new_price = round(old_price * 0.92, 2)
                prop.base_price = new_price
                msg = f"📊 AI PRICING: {prop.title} occupancy {int(occupancy_pct)}% - Price reduced ${old_price}→${new_price}"
                db.session.add(Log(event_type="Pricing", category="System", message=msg))
                events_this_cycle.append(msg)
                
                # Auto-create booking due to price drop
                check_in = today + timedelta(days=random.randint(2, 10))
                check_out = check_in + timedelta(days=random.randint(3, 6))
                amount = new_price * (check_out - check_in).days
                res = Reservation(
                    property_id=prop.id,
                    guest_name=f"AutoBook-{random.randint(100,999)}",
                    check_in=check_in,
                    check_out=check_out,
                    amount_paid=amount
                )
                db.session.add(res)
                db.session.add(Financial(property_id=prop.id, category='Income', amount=amount, date=check_in))
                
                booking_msg = f"✓ Price optimization successful! New booking secured for {prop.title}"
                db.session.add(Log(event_type="Pricing", category="Booking", message=booking_msg))
                events_this_cycle.append(booking_msg)
                
            elif occupancy_pct > 70:
                # High demand - increase price
                new_price = round(old_price * 1.08, 2)
                prop.base_price = new_price
                msg = f"📈 AI PRICING: {prop.title} high demand {int(occupancy_pct)}% - Price increased ${old_price}→${new_price}"
                db.session.add(Log(event_type="Pricing", category="System", message=msg))
                events_this_cycle.append(msg)

        db.session.commit()
        return events_this_cycle[0] if events_this_cycle else None
            
    return None

def calculate_revpar(days=30):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    total_revenue = sum([r.amount_paid for r in Reservation.query.filter(Reservation.check_in >= start_date).all()])
    total_properties = Property.query.count()
    if total_properties == 0: return 0
    
    total_available_nights = total_properties * days
    return round(total_revenue / total_available_nights, 2) if total_available_nights > 0 else 0

def get_occupancy_rate():
    today = date.today()
    total_properties = Property.query.count()
    if total_properties == 0: return 0
    
    booked_count = Reservation.query.filter(Reservation.check_in <= today, Reservation.check_out > today).count()
    return round((booked_count / total_properties) * 100, 1)

def get_alerts():
    alerts = []
    properties = Property.query.all()
    today = date.today()
    next_30 = today + timedelta(days=30)
    
    for prop in properties:
        booked_days = 0
        reservations = Reservation.query.filter(
            Reservation.property_id == prop.id,
            Reservation.check_in < next_30,
            Reservation.check_out > today
        ).all()
        
        for res in reservations:
            start = max(res.check_in, today)
            end = min(res.check_out, next_30)
            if end > start:
                booked_days += (end - start).days
        
        occupancy_pct = (booked_days / 30) * 100
        if occupancy_pct < 20: 
            alerts.append({
                'type': 'AI Monitoring',
                'message': f"{prop.title}: {int(occupancy_pct)}% occupancy - AI auto-adjusting price",
                'property_id': prop.id,
                'action_url': f"/property/{prop.id}"
            })

        if prop.status == 'Dirty' or prop.status == 'Maintenance':
             alerts.append({
                'type': 'Auto-Dispatch Active',
                'message': f"{prop.title} - Staff dispatched automatically",
                'property_id': prop.id,
                'action_url': f"/property/{prop.id}"
            })
            
    return alerts[:5]

def get_cleaning_priority():
    today = date.today()
    upcoming = Reservation.query.filter(Reservation.check_in >= today).order_by(Reservation.check_in).limit(5).all()
    priority = []
    for res in upcoming:
        priority.append({
            'property': res.property.title,
            'check_in': res.check_in,
            'status': res.property.status
        })
    return priority

def get_monthly_revenue():
    today = date.today()
    data = []
    labels = []
    
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        income = sum([f.amount for f in Financial.query.filter(
            Financial.category == 'Income',
            Financial.date >= month_start,
            Financial.date < next_month
        ).all()])
        
        data.append(income)
        labels.append(month_start.strftime('%b'))
        
    return labels, data

# Authentication
@app.before_request
def require_login():
    allowed_routes = ['login', 'static', 'api_simulate', 'api_notifications']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'admin':
            session['user'] = {'name': 'Manager', 'role': 'Admin'}
            if 'notifications' not in session:
                session['notifications'] = [] 
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    revpar = calculate_revpar()
    occupancy = get_occupancy_rate()
    alerts = get_alerts()
    cleaning_tasks = get_cleaning_priority()
    
    total_income = sum([f.amount for f in Financial.query.filter_by(category='Income').all()])
    total_expenses = sum([f.amount for f in Financial.query.filter(Financial.category != 'Income').all()])
    net_profit = total_income - total_expenses
    
    all_properties = Property.query.all()
    chart_labels, chart_data = get_monthly_revenue()
    all_staff = Staff.query.all()
    
    # Separate logs by type
    operations_logs = Log.query.filter_by(event_type='Operations').order_by(Log.timestamp.desc()).limit(20).all()
    pricing_logs = Log.query.filter_by(event_type='Pricing').order_by(Log.timestamp.desc()).limit(20).all()
    
    return render_template('dashboard.html', 
                           revpar=revpar, 
                           occupancy=occupancy, 
                           alerts=alerts, 
                           cleaning_tasks=cleaning_tasks,
                           net_profit=net_profit,
                           properties=all_properties,
                           chart_labels=chart_labels,
                           chart_data=chart_data,
                           staff=all_staff,
                           operations_logs=operations_logs,
                           pricing_logs=pricing_logs,
                           notifications=session.get('notifications', []),
                           active_page='dashboard')

@app.route('/api/simulate')
def api_simulate():
    msg = run_simulation()
    
    revpar = calculate_revpar()
    occupancy = get_occupancy_rate()
    chart_labels, chart_data = get_monthly_revenue()
    
    total_income = sum([f.amount for f in Financial.query.filter_by(category='Income').all()])
    total_expenses = sum([f.amount for f in Financial.query.filter(Financial.category != 'Income').all()])
    net_profit = total_income - total_expenses
    
    # Separate logs by type
    operations_logs_objs = Log.query.filter_by(event_type='Operations').order_by(Log.timestamp.desc()).limit(20).all()
    pricing_logs_objs = Log.query.filter_by(event_type='Pricing').order_by(Log.timestamp.desc()).limit(20).all()
    
    operations_logs = [l.to_dict() for l in operations_logs_objs]
    pricing_logs = [l.to_dict() for l in pricing_logs_objs]

    response_data = {
        'revpar': revpar,
        'occupancy': occupancy,
        'net_profit': net_profit,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'operations_logs': operations_logs,
        'pricing_logs': pricing_logs
    }

    if msg:
        if 'notifications' not in session:
            session['notifications'] = []
        n_list = session['notifications']
        n_list.insert(0, {'type': 'booking', 'message': msg, 'read': False})
        session['notifications'] = n_list[:10]
        session.modified = True
        
        response_data['new_event'] = True

        response_data['message'] = msg
    else:
        response_data['new_event'] = False
        
    return jsonify(response_data)

@app.route('/api/notifications/mark_read', methods=['POST'])
def mark_notifications_read():
    session['notifications'] = []
    session.modified = True
    return jsonify({'success': True})

@app.route('/properties')
def properties():
    all_props = Property.query.all()
    return render_template('properties.html', properties=all_props, active_page='properties', notifications=session.get('notifications', []))

@app.route('/property/<int:id>')
def property_detail(id):
    prop = Property.query.get_or_404(id)
    income = sum([f.amount for f in Financial.query.filter_by(property_id=prop.id, category='Income').all()])
    expenses = sum([f.amount for f in Financial.query.filter(Financial.property_id == prop.id, Financial.category != 'Income').all()])
    
    reservations = Reservation.query.filter_by(property_id=prop.id).order_by(Reservation.check_in.desc()).all()
    
    return render_template('property_detail.html', property=prop, income=income, expenses=expenses, profit=income-expenses, reservations=reservations, notifications=session.get('notifications', []))

@app.route('/add_property', methods=['POST'])
def add_property():
    try:
        new_prop = Property(
            title=request.form['title'],
            type=request.form['type'],
            base_price=float(request.form['base_price']),
            address=request.form['address'],
            status=request.form['status']
        )
        db.session.add(new_prop)
        db.session.commit()
        db.session.add(Log(event_type="System", message=f"✓ New property onboarded: {new_prop.title}"))
        db.session.commit()
        flash('Property added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding property: {str(e)}', 'error')
    
    return redirect(url_for('properties'))

@app.route('/add_staff', methods=['POST'])
def add_staff():
    try:
        new_staff = Staff(
            name=request.form['name'],
            role=request.form['role'],
            contact=request.form['contact']
        )
        db.session.add(new_staff)
        db.session.commit()
        db.session.add(Log(event_type="System", message=f"✓ New staff registered: {new_staff.name} ({new_staff.role})"))
        db.session.commit()
        flash(f'Staff member {new_staff.name} added.', 'success')
    except Exception as e:
        flash(f'Error adding staff: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

@app.route('/add_reservation', methods=['POST'])
def add_reservation():
    try:
        prop_id = int(request.form['property_id'])
        check_in = datetime.strptime(request.form['check_in'], '%Y-%m-%d').date()
        check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d').date()
        amount = float(request.form['amount_paid'])
        
        res = Reservation(
            property_id=prop_id,
            guest_name=request.form['guest_name'],
            check_in=check_in,
            check_out=check_out,
            amount_paid=amount
        )
        db.session.add(res)
        
        fin = Financial(property_id=prop_id, category='Income', amount=amount, date=check_in)
        db.session.add(fin)
        db.session.add(Log(event_type="Booking", message=f"✓ Manual booking: Property #{prop_id} | ${amount}"))
        
        db.session.commit()
        
        referer = request.headers.get("Referer")
        if referer and "calendar" in referer:
            flash('Reservation added!', 'success')
            return redirect(url_for('calendar_view'))
            
        flash('Booking confirmed!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash(f'Error creating reservation: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/delete_property/<int:id>', methods=['POST'])
def delete_property(id):
    prop = Property.query.get_or_404(id)
    try:
        Reservation.query.filter_by(property_id=id).delete()
        Financial.query.filter_by(property_id=id).delete()
        db.session.delete(prop)
        db.session.commit()
        flash('Property deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting property: {str(e)}', 'error')
    return redirect(url_for('properties'))

@app.route('/update_property/<int:id>', methods=['POST'])
def update_property(id):
    prop = Property.query.get_or_404(id)
    try:
        prop.title = request.form['title']
        prop.type = request.form['type']
        prop.base_price = float(request.form['base_price'])
        prop.address = request.form['address']
        prop.status = request.form['status']
        db.session.commit()
        flash('Property updated successfully.', 'success')
    except Exception as e:
        flash(f'Update failed: {str(e)}', 'error')
    return redirect(url_for('property_detail', id=id))

@app.route('/update_status/<int:id>/<status>', methods=['POST'])
def update_status(id, status):
    prop = Property.query.get_or_404(id)
    try:
        prop.status = status
        db.session.commit()
        db.session.add(Log(event_type="Maintenance", message=f"Manual override: {prop.title} → {status}"))
        db.session.commit()
        flash(f'Status updated to {status}.', 'success')
    except Exception as e:
        flash('Error updating status.', 'error')
    return redirect(url_for('property_detail', id=id))

@app.route('/apply_fix/<int:property_id>')
def apply_fix(property_id):
    # This is now mostly automated, but kept for manual override
    prop = Property.query.get_or_404(property_id)
    old_price = prop.base_price
    new_price = round(prop.base_price * 0.9, 2)
    prop.base_price = new_price
    
    today = date.today()
    res = Reservation(
        property_id=prop.id,
        guest_name="Manual-Override-Booking",
        check_in=today + timedelta(days=2),
        check_out=today + timedelta(days=6),
        amount_paid=new_price * 4
    )
    db.session.add(res)
    db.session.add(Log(event_type="System", message=f"Manual price override: {prop.title} ${old_price}→${new_price}"))
    db.session.commit()
    
    flash(f'Manual price adjustment applied!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/calendar')
def calendar_view():
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    curr_date = date(year, month, 1)
    
    if month == 12: next_date = date(year + 1, 1, 1)
    else: next_date = date(year, month + 1, 1)
        
    if month == 1: prev_date = date(year - 1, 12, 1)
    else: prev_date = date(year, month - 1, 1)

    reservations = Reservation.query.all()
    all_properties = Property.query.all()
    
    days_in_month = calendar.monthrange(year, month)[1]
    
    return render_template('calendar.html', 
                           reservations=reservations, 
                           properties=all_properties, 
                           active_page='calendar',
                           current_year=year,
                           current_month=month,
                           month_name=curr_date.strftime('%B'),
                           days_in_month=days_in_month,
                           next_year=next_date.year,
                           next_month=next_date.month,
                           prev_year=prev_date.year,
                           prev_month=prev_date.month,
                           notifications=session.get('notifications', []))

@app.route('/reports')
def reports():
    timeframe = request.args.get('timeframe', 'all')
    properties = Property.query.all()
    report_data = []
    
    today = date.today()
    start_date = date(2000, 1, 1)
    end_date = date(2100, 1, 1)
    
    if timeframe == 'this_month':
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1)
        else:
            end_date = date(today.year, today.month + 1, 1)
    elif timeframe == 'last_month':
        if today.month == 1:
            start_date = date(today.year - 1, 12, 1)
            end_date = date(today.year, 1, 1)
        else:
            start_date = date(today.year, today.month - 1, 1)
            end_date = date(today.year, today.month, 1)
    elif timeframe == 'ytd':
        start_date = date(today.year, 1, 1)
        end_date = date(today.year + 1, 1, 1)

    for prop in properties:
        income = sum([f.amount for f in Financial.query.filter(
            Financial.property_id == prop.id, 
            Financial.category == 'Income',
            Financial.date >= start_date,
            Financial.date < end_date
        ).all()])
        
        expenses = sum([f.amount for f in Financial.query.filter(
            Financial.property_id == prop.id, 
            Financial.category != 'Income',
            Financial.date >= start_date,
            Financial.date < end_date
        ).all()])
        
        report_data.append({
            'title': prop.title,
            'income': income,
            'expenses': expenses,
            'profit': income - expenses
        })
        
    return render_template('reports.html', report_data=report_data, active_page='reports', timeframe=timeframe, notifications=session.get('notifications', []))

@app.route('/settings')
def settings():
    # Load current settings
    auto_pricing = Settings.get('auto_pricing_enabled', 'true')
    price_min = Settings.get('price_min_percent', '70')
    price_max = Settings.get('price_max_percent', '150')
    price_step = Settings.get('price_step_percent', '8')
    low_threshold = Settings.get('low_occupancy_threshold', '20')
    high_threshold = Settings.get('high_occupancy_threshold', '70')
    
    return render_template('settings.html', 
                         active_page='settings', 
                         notifications=session.get('notifications', []),
                         auto_pricing_enabled=auto_pricing,
                         price_min_percent=price_min,
                         price_max_percent=price_max,
                         price_step_percent=price_step,
                         low_occupancy_threshold=low_threshold,
                         high_occupancy_threshold=high_threshold)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    try:
        # Save all settings
        Settings.set('auto_pricing_enabled', request.form.get('auto_pricing_enabled', 'false'))
        Settings.set('price_min_percent', request.form.get('price_min_percent', '70'))
        Settings.set('price_max_percent', request.form.get('price_max_percent', '150'))
        Settings.set('price_step_percent', request.form.get('price_step_percent', '8'))
        Settings.set('low_occupancy_threshold', request.form.get('low_occupancy_threshold', '20'))
        Settings.set('high_occupancy_threshold', request.form.get('high_occupancy_threshold', '70'))
        
        db.session.add(Log(event_type="Pricing", category="System", message="Pricing settings updated by admin"))
        db.session.commit()
        
        flash('Pricing settings saved successfully!', 'success')
    except Exception as e:
        flash(f'Error saving settings: {str(e)}', 'error')
    
    return redirect(url_for('settings'))

@app.route('/billing')
def billing():
    return render_template('billing.html', active_page='billing', notifications=session.get('notifications', []))

if __name__ == '__main__':
    app.run(debug=True)
