from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
from functools import wraps
from datetime import date

app = Flask(__name__)
app.secret_key = 'medicine_tracker_secret_2024'

# ── DB Config ────────────────────────────────────────────
DB = dict(host='localhost', user='root', password='your_actual_password', port=3306, 
          db='medicine_tracker', cursorclass=pymysql.cursors.DictCursor, charset='utf8mb4')

def get_db():
    try:
        return pymysql.connect(**DB)
    except pymysql.MySQLError as e:
        print("\n" + "!"*60)
        print(" DATABASE CONNECTION FAILED ".center(60, '='))
        print("!"*60)
        print(f"Error Code: {e.args[0]}")
        print(f"Message:    {e.args[1]}")
        print("-" * 60)
        print("CHECKLIST:")
        print("1. Is MySQL Server running? (Check Windows Services)")
        print("2. Does the password in app.py match your MySQL root password?")
        print("3. Did you run schema.sql to create 'medicine_tracker'?")
        print("!"*60 + "\n")
        raise e

# ── Auth decorator ───────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════
@app.route('/', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_req = request.form.get('role', 'staff')
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Users WHERE username=%s AND password=%s AND role=%s AND is_active=TRUE",
                        (username, password, role_req))
            user = cur.fetchone()
        conn.close()
        if user:
            session['user_id']  = user['user_id']
            session['username'] = user['username']
            session['role']     = user['role']
            session['fullname'] = user['full_name']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials or wrong role selected.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    with conn.cursor() as cur:
        cur.callproc('GetDashboardStats')
        stats = cur.fetchone()
        cur.nextset()
        cur.execute("SELECT * FROM ActiveAlerts LIMIT 5")
        alerts = cur.fetchall()
        cur.execute("SELECT * FROM NearExpiryIn30Days LIMIT 5")
        near_expiry = cur.fetchall()
        cur.execute("SELECT * FROM LowStockMedicines")
        low_stock = cur.fetchall()
    conn.close()
    return render_template('dashboard.html', stats=stats, alerts=alerts,
                           near_expiry=near_expiry, low_stock=low_stock)

# ════════════════════════════════════════════════════════
# MEDICINES — CRUD
# ════════════════════════════════════════════════════════
@app.route('/medicines')
@login_required
def medicines():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT m.*, st.current_quantity
            FROM Medicine m
            LEFT JOIN Stock st ON m.medicine_id = st.medicine_id
            ORDER BY m.name
        """)
        meds = cur.fetchall()
    conn.close()
    return render_template('medicines.html', medicines=meds)

@app.route('/medicines/add', methods=['GET','POST'])
@login_required
@admin_required
def add_medicine():
    if request.method == 'POST':
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO Medicine (name,category,dosage_form,manufacturer,min_stock_level,description)
                               VALUES (%s,%s,%s,%s,%s,%s)""",
                            (request.form['name'], request.form['category'],
                             request.form['dosage_form'], request.form['manufacturer'],
                             request.form['min_stock_level'], request.form['description']))
                med_id = cur.lastrowid
                cur.execute("INSERT INTO Stock (medicine_id, current_quantity) VALUES (%s, 0)", (med_id,))
            conn.commit()
            flash('Medicine added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('medicines'))
    return render_template('add_medicine.html')

@app.route('/medicines/edit/<int:mid>', methods=['GET','POST'])
@login_required
@admin_required
def edit_medicine(mid):
    conn = get_db()
    if request.method == 'POST':
        try:
            with conn.cursor() as cur:
                cur.execute("""UPDATE Medicine SET name=%s,category=%s,dosage_form=%s,
                               manufacturer=%s,min_stock_level=%s,description=%s
                               WHERE medicine_id=%s""",
                            (request.form['name'], request.form['category'],
                             request.form['dosage_form'], request.form['manufacturer'],
                             request.form['min_stock_level'], request.form['description'], mid))
            conn.commit()
            flash('Medicine updated!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('medicines'))
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Medicine WHERE medicine_id=%s", (mid,))
        med = cur.fetchone()
    conn.close()
    return render_template('edit_medicine.html', med=med)

@app.route('/medicines/delete/<int:mid>')
@login_required
@admin_required
def delete_medicine(mid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Medicine WHERE medicine_id=%s", (mid,))
        conn.commit()
        flash('Medicine deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('medicines'))

# ════════════════════════════════════════════════════════
# SUPPLIERS — CRUD
# ════════════════════════════════════════════════════════
@app.route('/suppliers')
@login_required
def suppliers():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT s.*, COUNT(b.batch_id) AS total_batches
            FROM Supplier s LEFT JOIN Batch b ON s.supplier_id=b.supplier_id
            GROUP BY s.supplier_id ORDER BY s.name
        """)
        sups = cur.fetchall()
    conn.close()
    return render_template('suppliers.html', suppliers=sups)

@app.route('/suppliers/add', methods=['GET','POST'])
@login_required
@admin_required
def add_supplier():
    if request.method == 'POST':
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO Supplier (name,contact_number,email,city,state,gst_number)
                               VALUES (%s,%s,%s,%s,%s,%s)""",
                            (request.form['name'], request.form['contact_number'],
                             request.form['email'], request.form['city'],
                             request.form['state'], request.form['gst_number']))
            conn.commit()
            flash('Supplier added!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('suppliers'))
    return render_template('add_supplier.html')

@app.route('/suppliers/delete/<int:sid>')
@login_required
@admin_required
def delete_supplier(sid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Supplier WHERE supplier_id=%s", (sid,))
        conn.commit()
        flash('Supplier deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('suppliers'))

# ════════════════════════════════════════════════════════
# BATCHES — CRUD
# ════════════════════════════════════════════════════════
@app.route('/batches')
@login_required
def batches():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT b.*, m.name AS medicine_name, s.name AS supplier_name,
                   DATEDIFF(b.expiry_date, CURDATE()) AS days_left
            FROM Batch b
            JOIN Medicine m ON b.medicine_id=m.medicine_id
            JOIN Supplier s ON b.supplier_id=s.supplier_id
            ORDER BY b.expiry_date ASC
        """)
        btchs = cur.fetchall()
    conn.close()
    return render_template('batches.html', batches=btchs)

@app.route('/batches/add', methods=['GET','POST'])
@login_required
@admin_required
def add_batch():
    conn = get_db()
    if request.method == 'POST':
        try:
            with conn.cursor() as cur:
                qty = int(request.form['quantity_purchased'])
                cur.execute("""INSERT INTO Batch
                    (medicine_id,supplier_id,batch_number,purchase_date,manufacture_date,
                     expiry_date,quantity_purchased,quantity_remaining,unit_price)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (request.form['medicine_id'], request.form['supplier_id'],
                     request.form['batch_number'], request.form['purchase_date'],
                     request.form['manufacture_date'], request.form['expiry_date'],
                     qty, qty, request.form['unit_price']))
                mid = int(request.form['medicine_id'])
                cur.execute("""UPDATE Stock SET current_quantity = current_quantity + %s
                               WHERE medicine_id = %s""", (qty, mid))
            conn.commit()
            flash('Batch added! Triggers fired automatically for expiry alerts.', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('batches'))
    with conn.cursor() as cur:
        cur.execute("SELECT medicine_id, name FROM Medicine ORDER BY name")
        meds = cur.fetchall()
        cur.execute("SELECT supplier_id, name FROM Supplier ORDER BY name")
        sups = cur.fetchall()
    conn.close()
    return render_template('add_batch.html', medicines=meds, suppliers=sups)

@app.route('/batches/delete/<int:bid>')
@login_required
@admin_required
def delete_batch(bid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Batch WHERE batch_id=%s", (bid,))
        conn.commit()
        flash('Batch deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('batches'))

# ════════════════════════════════════════════════════════
# ALERTS
# ════════════════════════════════════════════════════════
@app.route('/alerts')
@login_required
def alerts():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.*, m.name AS medicine_name, b.batch_number
            FROM Alert a
            JOIN Medicine m ON a.medicine_id=m.medicine_id
            LEFT JOIN Batch b ON a.batch_id=b.batch_id
            ORDER BY a.is_resolved ASC, a.created_at DESC
        """)
        all_alerts = cur.fetchall()
    conn.close()
    return render_template('alerts.html', alerts=all_alerts)

@app.route('/alerts/resolve/<int:aid>')
@login_required
@admin_required
def resolve_alert(aid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.callproc('ResolveAlert', (aid, session['role']))
            conn.commit()
        flash('Alert resolved!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('alerts'))

# ════════════════════════════════════════════════════════
# REPORTS (Aggregate + JOIN + Subquery)
# ════════════════════════════════════════════════════════
@app.route('/reports')
@login_required
def reports():
    conn = get_db()
    with conn.cursor() as cur:
        # Aggregate: total stock value per medicine
        cur.execute("""
            SELECT m.name, m.category,
                   SUM(b.quantity_remaining * b.unit_price) AS stock_value,
                   SUM(b.quantity_remaining) AS total_units
            FROM Medicine m JOIN Batch b ON m.medicine_id=b.medicine_id
            WHERE b.expiry_date >= CURDATE()
            GROUP BY m.medicine_id, m.name, m.category
            ORDER BY stock_value DESC
        """)
        stock_value = cur.fetchall()

        # JOIN: supplier batch count
        cur.execute("""
            SELECT s.name AS supplier, s.city,
                   COUNT(b.batch_id) AS total_batches,
                   SUM(b.quantity_purchased * b.unit_price) AS total_purchased_value
            FROM Supplier s JOIN Batch b ON s.supplier_id=b.supplier_id
            GROUP BY s.supplier_id, s.name, s.city
            ORDER BY total_batches DESC
        """)
        supplier_stats = cur.fetchall()

        # Aggregate: category-wise avg price
        cur.execute("""
            SELECT m.category, AVG(b.unit_price) AS avg_price,
                   COUNT(DISTINCT m.medicine_id) AS medicine_count
            FROM Medicine m JOIN Batch b ON m.medicine_id=b.medicine_id
            GROUP BY m.category
        """)
        category_stats = cur.fetchall()

        # Subquery: medicines with NO valid (non-expired) batch
        cur.execute("""
            SELECT name, category FROM Medicine
            WHERE medicine_id NOT IN (
                SELECT DISTINCT medicine_id FROM Batch WHERE expiry_date >= CURDATE()
            )
        """)
        no_valid_batch = cur.fetchall()

        # Alert type count
        cur.execute("SELECT alert_type, COUNT(*) AS total FROM Alert GROUP BY alert_type")
        alert_stats = cur.fetchall()

    conn.close()
    return render_template('reports.html', stock_value=stock_value,
                           supplier_stats=supplier_stats, category_stats=category_stats,
                           no_valid_batch=no_valid_batch, alert_stats=alert_stats)

# ════════════════════════════════════════════════════════
# STOCK
# ════════════════════════════════════════════════════════
@app.route('/stock')
@login_required
def stock():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT m.name, m.category, st.current_quantity, m.min_stock_level,
                   st.last_updated,
                   CASE WHEN st.current_quantity < m.min_stock_level THEN 'LOW'
                        WHEN st.current_quantity < m.min_stock_level * 2 THEN 'MEDIUM'
                        ELSE 'OK' END AS stock_status
            FROM Stock st JOIN Medicine m ON st.medicine_id=m.medicine_id
            ORDER BY stock_status ASC, st.current_quantity ASC
        """)
        stock_data = cur.fetchall()
    conn.close()
    return render_template('stock.html', stock=stock_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
