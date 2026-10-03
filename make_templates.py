import os

base = "templates"
if not os.path.exists(base):
    os.makedirs(base)

# ── base.html ──────────────────────────────────────────────────
open(f"{base}/base.html","w").write("""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Medicine Expiry Tracker{% endblock %}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box
    }

    body {
      font-family: 'Segoe UI', sans-serif;
      background: #F1F5F9;
      color: #1E293B
    }

    a {
      text-decoration: none;
      color: inherit
    }

    /* Navbar */
    .navbar {
      background: #1E3A5F;
      padding: 0 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 60px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3)
    }

    .navbar .brand {
      color: #fff;
      font-size: 1.2rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px
    }

    .navbar .brand span {
      color: #34D399
    }

    .nav-links {
      display: flex;
      gap: 4px
    }

    .nav-links a {
      color: #CBD5E1;
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 14px;
      transition: all 0.2s
    }

    .nav-links a:hover,
    .nav-links a.active {
      background: #2563EB;
      color: #fff
    }

    .nav-right {
      display: flex;
      align-items: center;
      gap: 12px
    }

    .nav-right .user-info {
      color: #94A3B8;
      font-size: 13px
    }

    .nav-right .role-badge {
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700
    }

    .role-admin {
      background: #DC2626;
      color: #fff
    }

    .role-staff {
      background: #059669;
      color: #fff
    }

    .btn-logout {
      background: #374151;
      color: #fff;
      border: none;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px
    }

    .btn-logout:hover {
      background: #4B5563
    }

    /* Layout */
    .container {
      max-width: 1300px;
      margin: 0 auto;
      padding: 24px
    }

    .page-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px
    }

    .page-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: #1E3A5F
    }

    .page-subtitle {
      font-size: 13px;
      color: #64748B;
      margin-top: 2px
    }

    /* Cards */
    .card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08)
    }

    /* Buttons */
    .btn {
      padding: 9px 18px;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s
    }

    .btn-primary {
      background: #2563EB;
      color: #fff
    }

    .btn-primary:hover {
      background: #1D4ED8
    }

    .btn-success {
      background: #059669;
      color: #fff
    }

    .btn-success:hover {
      background: #047857
    }

    .btn-danger {
      background: #DC2626;
      color: #fff
    }

    .btn-danger:hover {
      background: #B91C1C
    }

    .btn-warning {
      background: #D97706;
      color: #fff
    }

    .btn-warning:hover {
      background: #B45309
    }

    .btn-sm {
      padding: 5px 12px;
      font-size: 12px;
      border-radius: 6px
    }

    .btn-outline {
      background: transparent;
      border: 1.5px solid #2563EB;
      color: #2563EB
    }

    .btn-outline:hover {
      background: #2563EB;
      color: #fff
    }

    /* Tables */
    .table-wrap {
      overflow-x: auto
    }

    table {
      width: 100%;
      border-collapse: collapse
    }

    th {
      background: #1E3A5F;
      color: #fff;
      padding: 11px 14px;
      text-align: left;
      font-size: 13px;
      font-weight: 600
    }

    td {
      padding: 10px 14px;
      font-size: 13px;
      border-bottom: 1px solid #E2E8F0
    }

    tr:hover td {
      background: #F8FAFC
    }

    tr:last-child td {
      border-bottom: none
    }

    /* Badges */
    .badge {
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700
    }

    .badge-danger {
      background: #FEE2E2;
      color: #DC2626
    }

    .badge-warning {
      background: #FEF3C7;
      color: #D97706
    }

    .badge-success {
      background: #D1FAE5;
      color: #059669
    }

    .badge-info {
      background: #DBEAFE;
      color: #2563EB
    }

    .badge-gray {
      background: #E2E8F0;
      color: #475569
    }

    /* Forms */
    .form-group {
      margin-bottom: 18px
    }

    .form-group label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      color: #374151;
      margin-bottom: 6px
    }

    .form-group input,
    .form-group select,
    .form-group textarea {
      width: 100%;
      padding: 9px 12px;
      border: 1.5px solid #E2E8F0;
      border-radius: 8px;
      font-size: 14px;
      color: #1E293B;
      transition: border 0.2s
    }

    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px
    }

    /* Flash messages */
    .flash {
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 16px;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px
    }

    .flash-success {
      background: #D1FAE5;
      color: #065F46;
      border-left: 4px solid #059669
    }

    .flash-danger {
      background: #FEE2E2;
      color: #991B1B;
      border-left: 4px solid #DC2626
    }

    /* Stat cards */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 16px;
      margin-bottom: 24px
    }

    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
      border-left: 4px solid
    }

    .stat-card .stat-num {
      font-size: 2rem;
      font-weight: 800;
      line-height: 1
    }

    .stat-card .stat-label {
      font-size: 12px;
      color: #64748B;
      margin-top: 4px
    }

    .stat-blue {
      border-color: #2563EB
    }

    .stat-blue .stat-num {
      color: #2563EB
    }

    .stat-green {
      border-color: #059669
    }

    .stat-green .stat-num {
      color: #059669
    }

    .stat-red {
      border-color: #DC2626
    }

    .stat-red .stat-num {
      color: #DC2626
    }

    .stat-amber {
      border-color: #D97706
    }

    .stat-amber .stat-num {
      color: #D97706
    }

    .stat-purple {
      border-color: #7C3AED
    }

    .stat-purple .stat-num {
      color: #7C3AED
    }

    .stat-teal {
      border-color: #0D9488
    }

    .stat-teal .stat-num {
      color: #0D9488
    }

    .stat-navy {
      border-color: #1E3A5F
    }

    .stat-navy .stat-num {
      color: #1E3A5F
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px
    }

    .mt-4 {
      margin-top: 16px
    }

    .mt-6 {
      margin-top: 24px
    }

    .mb-4 {
      margin-bottom: 16px
    }

    .section-title {
      font-size: 15px;
      font-weight: 700;
      color: #1E3A5F;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px
    }

    .section-title::after {
      content: '';
      flex: 1;
      height: 1px;
      background: #E2E8F0
    }
  </style>
</head>

<body>
  {% if session.user_id %}
  <nav class="navbar">
    <div class="brand">💊 Medicine Expiry <span>Tracker</span></div>
    <div class="nav-links">
      <a href="{{ url_for('dashboard') }}" {% if request.endpoint=='dashboard' %}class="active"{% endif %}>🏠 Dashboard</a>
      <a href="{{ url_for('medicines') }}" {% if 'medicine' in request.endpoint %}class="active"{% endif %}>💊 Medicines</a>
      <a href="{{ url_for('suppliers') }}" {% if 'supplier' in request.endpoint %}class="active"{% endif %}>🚚 Suppliers</a>
      <a href="{{ url_for('batches') }}" {% if 'batch' in request.endpoint %}class="active"{% endif %}>📦 Batches</a>
      <a href="{{ url_for('stock') }}" {% if request.endpoint=='stock' %}class="active"{% endif %}>📊 Stock</a>
      <a href="{{ url_for('alerts') }}" {% if request.endpoint=='alerts' %}class="active"{% endif %}>🔔 Alerts</a>
      <a href="{{ url_for('reports') }}" {% if request.endpoint=='reports' %}class="active"{% endif %}>📈 Reports</a>
    </div>
    <div class="nav-right">
      <div class="user-info">{{ session.fullname }}</div>
      <span class="role-badge role-{{ session.role }}">{{ session.role|upper }}</span>
      <a href="{{ url_for('logout') }}"><button class="btn-logout">Logout</button></a>
    </div>
  </nav>
  {% endif %}
  <div {% if session.user_id %}class="container"{% endif %}>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for cat, msg in messages %}
        <div class="flash flash-{{ cat }}">{{ msg }}</div>
      {% endfor %}
    {% endwith %}
    {% block content %}{% endblock %}
  </div>
</body>

</html>""")

# ── login.html ─────────────────────────────────────────────────
open(f"{base}/login.html","w").write("""{% extends 'base.html' %}
{% block title %}Login — Medicine Expiry Tracker{% endblock %}
{% block content %}
<div style="display:flex; justify-content:center; align-items:center; min-height:80vh;">
  <div class="card" style="width:100%; max-width:400px;">
    <div style="text-align:center; margin-bottom:24px;">
      <h2 style="color:#1E3A5F; font-size:1.8rem; margin-bottom:8px;">Welcome Back</h2>
      <p style="color:#64748B; font-size:14px;">Sign in to manage your inventory</p>
    </div>
    
    {% if error %}
    <div class="flash flash-danger" style="margin-bottom:20px;">{{ error }}</div>
    {% endif %}

    <form method="POST">
      <div class="form-group">
        <label>Username</label>
        <input type="text" name="username" required placeholder="Enter username">
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" name="password" required placeholder="Enter password">
      </div>
      <div class="form-group">
        <label>Login As</label>
        <select name="role">
          <option value="staff">Staff Member</option>
          <option value="admin">Administrator</option>
        </select>
      </div>
      <button type="submit" class="btn btn-primary" style="width:100%; justify-content:center; margin-top:10px;">Sign In</button>
    </form>
  </div>
</div>
{% endblock %}""")

# ── dashboard.html ─────────────────────────────────────────────
open(f"{base}/dashboard.html","w").write("""{% extends 'base.html' %}
{% block title %}Dashboard — Medicine Expiry Tracker{% endblock %}
{% block content %}
<div class="page-header">
  <div>
    <div class="page-title">🏠 Dashboard</div>
    <div class="page-subtitle">Welcome back, {{ session.fullname }} ({{ session.role|upper }})</div>
  </div>
</div>

{% if stats %}
<div class="stats-grid">
  <div class="stat-card stat-blue">
    <div class="stat-num">{{ stats.total_medicines }}</div>
    <div class="stat-label">Total Medicines</div>
  </div>
  <div class="stat-card stat-teal">
    <div class="stat-num">{{ stats.total_suppliers }}</div>
    <div class="stat-label">Suppliers</div>
  </div>
  <div class="stat-card stat-navy">
    <div class="stat-num">{{ stats.active_batches }}</div>
    <div class="stat-label">Active Batches</div>
  </div>
  <div class="stat-card stat-red">
    <div class="stat-num">{{ stats.critical_alerts }}</div>
    <div class="stat-label">Critical Alerts</div>
  </div>
  <div class="stat-card stat-amber">
    <div class="stat-num">{{ stats.active_alerts }}</div>
    <div class="stat-label">Active Alerts</div>
  </div>
  <div class="stat-card stat-purple">
    <div class="stat-num">{{ stats.low_stock_count }}</div>
    <div class="stat-label">Low Stock Items</div>
  </div>
  <div class="stat-card stat-green">
    <div class="stat-num">{{ stats.expired_count }}</div>
    <div class="stat-label">Expired Batches</div>
  </div>
</div>
{% endif %}

<div class="grid-2">
  <!-- Active Alerts -->
  <div class="card">
    <div class="section-title">🔔 Active Alerts</div>
    {% if alerts %}
      {% for a in alerts %}
      <div style="padding:10px 12px;margin-bottom:8px;border-radius:8px;border-left:4px solid {% if a.alert_type=='EXPIRY_CRITICAL' %}#DC2626{% elif a.alert_type=='EXPIRY_WARNING' %}#D97706{% else %}#2563EB{% endif %};background:{% if a.alert_type=='EXPIRY_CRITICAL' %}#FEE2E2{% elif a.alert_type=='EXPIRY_WARNING' %}#FEF3C7{% else %}#DBEAFE{% endif %}">
        <div style="font-weight:600;font-size:13px;color:#1E293B">{{ a.medicine_name }}</div>
        <div style="font-size:12px;color:#64748B;margin-top:2px">{{ a.alert_message }}</div>
        <div style="font-size:11px;color:#94A3B8;margin-top:4px">{{ a.created_at }}</div>
      </div>
      {% endfor %}
      <a href="{{ url_for('alerts') }}" class="btn btn-outline btn-sm mt-4">View All Alerts →</a>
    {% else %}
      <div style="text-align:center; padding:20px; color:#94A3B8;">✅ No active alerts!</div>
    {% endif %}
  </div>

  <!-- Near Expiry -->
  <div class="card">
    <div class="section-title">⚠️ Expiring in 30 Days</div>
    {% if near_expiry %}
      <div class="table-wrap">
        <table>
          <tr><th>Medicine</th><th>Batch</th><th>Expiry</th><th>Days Left</th></tr>
          {% for b in near_expiry %}
          <tr>
            <td><strong>{{ b.medicine_name }}</strong></td>
            <td><code style="background:#F1F5F9;padding:2px 6px;border-radius:4px;font-size:12px">{{ b.batch_number }}</code></td>
            <td>{{ b.expiry_date }}</td>
            <td><span class="badge badge-danger">{{ b.days_remaining }} days</span></td>
          </tr>
          {% endfor %}
        </table>
      </div>
      <a href="{{ url_for('batches') }}" class="btn btn-outline btn-sm mt-4">View All Batches →</a>
    {% else %}
      <div style="text-align:center; padding:20px; color:#94A3B8;">✅ No batches expiring soon!</div>
    {% endif %}
  </div>
</div>

<!-- Low Stock Table (Optional expansion) -->
{% if low_stock %}
<div class="card mt-6">
  <div class="section-title">📉 Low Stock Summary</div>
  <!-- Detailed table similar to stock.html but filtered -->
</div>
{% endif %}
{% endblock %}""")

# ── medicines.html ─────────────────────────────────────────────
open(f"{base}/medicines.html","w").write("""{% extends 'base.html' %}
{% block title %}Medicines{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">💊 Medicines</div><div class="page-subtitle">Manage your medicine inventory</div></div>
  {% if session.role == 'admin' %}
  <a href="{{ url_for('add_medicine') }}" class="btn btn-primary">+ Add Medicine</a>
  {% endif %}
</div>
<div class="card">
  <div class="table-wrap">
    <table>
      <tr><th>#</th><th>Name</th><th>Category</th><th>Dosage Form</th><th>Manufacturer</th><th>Min Stock</th><th>Current Stock</th><th>Status</th>{% if session.role=='admin' %}<th>Actions</th>{% endif %}</tr>
      {% for m in medicines %}
      <tr>
        <td>{{ m.medicine_id }}</td>
        <td><strong>{{ m.name }}</strong><br><small style="color:#94A3B8">{{ m.description[:50] if m.description else '' }}</small></td>
        <td><span class="badge badge-info">{{ m.category }}</span></td>
        <td>{{ m.dosage_form }}</td>
        <td>{{ m.manufacturer }}</td>
        <td>{{ m.min_stock_level }}</td>
        <td>{{ m.current_quantity or 0 }}</td>
        <td>{% if m.current_quantity and m.current_quantity < m.min_stock_level %}<span class="badge badge-danger">LOW</span>{% else %}<span class="badge badge-success">OK</span>{% endif %}</td>
        {% if session.role=='admin' %}
        <td>
          <a href="{{ url_for('edit_medicine', mid=m.medicine_id) }}" class="btn btn-warning btn-sm">Edit</a>
          <a href="{{ url_for('delete_medicine', mid=m.medicine_id) }}" class="btn btn-danger btn-sm" onclick="return confirm('Delete this medicine?')">Del</a>
        </td>
        {% endif %}
      </tr>
      {% endfor %}
    </table>
  </div>
</div>
{% endblock %}""")

# ── add_medicine.html ──────────────────────────────────────────
open(f"{base}/add_medicine.html","w").write("""{% extends 'base.html' %}
{% block title %}Add Medicine{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">💊 Add Medicine</div></div>
  <a href="{{ url_for('medicines') }}" class="btn btn-outline">← Back</a>
</div>
<div class="card" style="max-width:700px">
  <form method="POST">
    <div class="form-grid">
      <div class="form-group"><label>Medicine Name *</label><input name="name" required placeholder="e.g. Paracetamol 500mg"></div>
      <div class="form-group"><label>Category *</label>
        <select name="category" required>
          <option value="">Select category</option>
          <option>Analgesic</option><option>Antibiotic</option><option>Antidiabetic</option>
          <option>Antilipemic</option><option>Antihistamine</option><option>Antacid</option>
          <option>Antihypertensive</option><option>Supplement</option><option>Other</option>
        </select>
      </div>
      <div class="form-group"><label>Dosage Form *</label>
        <select name="dosage_form" required>
          <option>Tablet</option><option>Capsule</option><option>Syrup</option>
          <option>Injection</option><option>Cream</option><option>Drops</option>
        </select>
      </div>
      <div class="form-group"><label>Manufacturer *</label><input name="manufacturer" required placeholder="e.g. Sun Pharma"></div>
      <div class="form-group"><label>Min Stock Level *</label><input name="min_stock_level" type="number" min="1" required value="10"></div>
    </div>
    <div class="form-group"><label>Description</label><textarea name="description" rows="2" placeholder="Brief description..."></textarea></div>
    <button type="submit" class="btn btn-primary">✅ Add Medicine</button>
  </form>
</div>
{% endblock %}""")

# ── edit_medicine.html ─────────────────────────────────────────
open(f"{base}/edit_medicine.html","w").write("""{% extends 'base.html' %}
{% block title %}Edit Medicine{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">✏️ Edit Medicine</div></div>
  <a href="{{ url_for('medicines') }}" class="btn btn-outline">← Back</a>
</div>
<div class="card" style="max-width:700px">
  <form method="POST">
    <div class="form-grid">
      <div class="form-group"><label>Medicine Name *</label><input name="name" value="{{ med.name }}" required></div>
      <div class="form-group"><label>Category *</label><input name="category" value="{{ med.category }}" required></div>
      <div class="form-group"><label>Dosage Form *</label><input name="dosage_form" value="{{ med.dosage_form }}" required></div>
      <div class="form-group"><label>Manufacturer *</label><input name="manufacturer" value="{{ med.manufacturer }}" required></div>
      <div class="form-group"><label>Min Stock Level *</label><input name="min_stock_level" type="number" value="{{ med.min_stock_level }}" required></div>
    </div>
    <div class="form-group"><label>Description</label><textarea name="description" rows="2">{{ med.description or '' }}</textarea></div>
    <button type="submit" class="btn btn-success">💾 Update Medicine</button>
  </form>
</div>
{% endblock %}""")

# ── suppliers.html ─────────────────────────────────────────────
open(f"{base}/suppliers.html","w").write("""{% extends 'base.html' %}
{% block title %}Suppliers{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">🚚 Suppliers</div><div class="page-subtitle">All medicine distributors and suppliers</div></div>
  {% if session.role=='admin' %}<a href="{{ url_for('add_supplier') }}" class="btn btn-primary">+ Add Supplier</a>{% endif %}
</div>
<div class="card">
  <div class="table-wrap">
    <table>
      <tr><th>#</th><th>Supplier Name</th><th>Contact</th><th>Email</th><th>City / State</th><th>GST No.</th><th>Total Batches</th>{% if session.role=='admin' %}<th>Actions</th>{% endif %}</tr>
      {% for s in suppliers %}
      <tr>
        <td>{{ s.supplier_id }}</td>
        <td><strong>{{ s.name }}</strong></td>
        <td>{{ s.contact_number }}</td>
        <td>{{ s.email }}</td>
        <td>{{ s.city }}, {{ s.state }}</td>
        <td><code style="font-size:11px">{{ s.gst_number or 'N/A' }}</code></td>
        <td><span class="badge badge-info">{{ s.total_batches }}</span></td>
        {% if session.role=='admin' %}
        <td><a href="{{ url_for('delete_supplier', sid=s.supplier_id) }}" class="btn btn-danger btn-sm" onclick="return confirm('Delete supplier?')">Del</a></td>
        {% endif %}
      </tr>
      {% endfor %}
    </table>
  </div>
</div>
{% endblock %}""")

# ── add_supplier.html ──────────────────────────────────────────
open(f"{base}/add_supplier.html","w").write("""{% extends 'base.html' %}
{% block title %}Add Supplier{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">🚚 Add Supplier</div></div>
  <a href="{{ url_for('suppliers') }}" class="btn btn-outline">← Back</a>
</div>
<div class="card" style="max-width:700px">
  <form method="POST">
    <div class="form-grid">
      <div class="form-group"><label>Supplier Name *</label><input name="name" required placeholder="e.g. MedSupply India Pvt Ltd"></div>
      <div class="form-group"><label>Contact Number *</label><input name="contact_number" required placeholder="9876543210"></div>
      <div class="form-group"><label>Email *</label><input name="email" type="email" required placeholder="supplier@gmail.com"></div>
      <div class="form-group"><label>City *</label><input name="city" required placeholder="Bangalore"></div>
      <div class="form-group"><label>State *</label><input name="state" required value="Karnataka"></div>
      <div class="form-group"><label>GST Number</label><input name="gst_number" placeholder="GST29AAAAA1234A1Z5"></div>
    </div>
    <button type="submit" class="btn btn-primary">✅ Add Supplier</button>
  </form>
</div>
{% endblock %}""")

# ── batches.html ───────────────────────────────────────────────
open(f"{base}/batches.html","w").write("""{% extends 'base.html' %}
{% block title %}Batches{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">📦 Batches</div><div class="page-subtitle">All purchase batches with expiry dates</div></div>
  {% if session.role=='admin' %}<a href="{{ url_for('add_batch') }}" class="btn btn-primary">+ Add Batch</a>{% endif %}
</div>
<div class="card">
  <div class="table-wrap">
    <table>
      <tr><th>Batch No.</th><th>Medicine</th><th>Supplier</th><th>Purchase Date</th><th>Expiry Date</th><th>Qty Purchased</th><th>Qty Remaining</th><th>Unit Price</th><th>Status</th>{% if session.role=='admin' %}<th>Del</th>{% endif %}</tr>
      {% for b in batches %}
      <tr>
        <td><code style="background:#F1F5F9;padding:2px 6px;border-radius:4px;font-size:12px">{{ b.batch_number }}</code></td>
        <td><strong>{{ b.medicine_name }}</strong></td>
        <td>{{ b.supplier_name }}</td>
        <td>{{ b.purchase_date }}</td>
        <td>{{ b.expiry_date }}</td>
        <td>{{ b.quantity_purchased }}</td>
        <td>{{ b.quantity_remaining }}</td>
        <td>₹{{ b.unit_price }}</td>
        <td>
          {% if b.days_left < 0 %}<span class="badge badge-gray">EXPIRED</span>
          {% elif b.days_left <= 30 %}<span class="badge badge-danger">{{ b.days_left }}d left</span>
          {% elif b.days_left <= 90 %}<span class="badge badge-warning">{{ b.days_left }}d left</span>
          {% else %}<span class="badge badge-success">Valid</span>{% endif %}
        </td>
        {% if session.role=='admin' %}
        <td><a href="{{ url_for('delete_batch', bid=b.batch_id) }}" class="btn btn-danger btn-sm" onclick="return confirm('Delete batch?')">Del</a></td>
        {% endif %}
      </tr>
      {% endfor %}
    </table>
  </div>
</div>
{% endblock %}""")

# ── add_batch.html ─────────────────────────────────────────────
open(f"{base}/add_batch.html","w").write("""{% extends 'base.html' %}
{% block title %}Add Batch{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">📦 Add Batch</div><div class="page-subtitle">Adding a batch will auto-fire expiry alert triggers</div></div>
  <a href="{{ url_for('batches') }}" class="btn btn-outline">← Back</a>
</div>
<div class="card" style="max-width:800px">
  <div style="background:#FEF3C7;border-left:4px solid #D97706;padding:10px 14px;border-radius:8px;margin-bottom:20px;font-size:13px;color:#92400E">
    ⚡ <strong>Trigger Note:</strong> When you add a batch, the database will automatically check the expiry date and insert alerts if needed.
  </div>
  <form method="POST">
    <div class="form-grid">
      <div class="form-group"><label>Medicine *</label>
        <select name="medicine_id" required>
          <option value="">Select medicine</option>
          {% for m in medicines %}<option value="{{ m.medicine_id }}">{{ m.name }}</option>{% endfor %}
        </select>
      </div>
      <div class="form-group"><label>Supplier *</label>
        <select name="supplier_id" required>
          <option value="">Select supplier</option>
          {% for s in suppliers %}<option value="{{ s.supplier_id }}">{{ s.name }}</option>{% endfor %}
        </select>
      </div>
      <div class="form-group"><label>Batch Number *</label><input name="batch_number" required placeholder="e.g. PARA-2025-003"></div>
      <div class="form-group"><label>Purchase Date *</label><input name="purchase_date" type="date" required></div>
      <div class="form-group"><label>Manufacture Date *</label><input name="manufacture_date" type="date" required></div>
      <div class="form-group"><label>Expiry Date *</label><input name="expiry_date" type="date" required></div>
      <div class="form-group"><label>Quantity *</label><input name="quantity_purchased" type="number" min="1" required placeholder="100"></div>
      <div class="form-group"><label>Unit Price (₹) *</label><input name="unit_price" type="number" step="0.01" min="0.01" required placeholder="5.50"></div>
    </div>
    <button type="submit" class="btn btn-primary">✅ Add Batch</button>
  </form>
</div>
{% endblock %}""")

# ── alerts.html ────────────────────────────────────────────────
open(f"{base}/alerts.html","w").write("""{% extends 'base.html' %}
{% block title %}Alerts{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">🔔 Alerts</div><div class="page-subtitle">Auto-generated by database triggers</div></div>
</div>
<div class="card">
  <div class="table-wrap">
    <table>
      <tr><th>ID</th><th>Medicine</th><th>Batch</th><th>Type</th><th>Message</th><th>Created</th><th>Status</th>{% if session.role=='admin' %}<th>Action</th>{% endif %}</tr>
      {% for a in alerts %}
      <tr style="{% if a.is_resolved %}opacity:0.55{% endif %}">
        <td>{{ a.alert_id }}</td>
        <td><strong>{{ a.medicine_name }}</strong></td>
        <td><code style="font-size:11px">{{ a.batch_number or '—' }}</code></td>
        <td>
          {% if a.alert_type=='EXPIRY_CRITICAL' %}<span class="badge badge-danger">CRITICAL</span>
          {% elif a.alert_type=='EXPIRY_WARNING' %}<span class="badge badge-warning">WARNING</span>
          {% else %}<span class="badge badge-info">LOW STOCK</span>{% endif %}
        </td>
        <td style="max-width:300px;font-size:12px">{{ a.alert_message }}</td>
        <td style="font-size:12px">{{ a.created_at }}</td>
        <td>{% if a.is_resolved %}<span class="badge badge-success">Resolved</span>{% else %}<span class="badge badge-danger">Active</span>{% endif %}</td>
        {% if session.role=='admin' %}
        <td>{% if not a.is_resolved %}<a href="{{ url_for('resolve_alert', aid=a.alert_id) }}" class="btn btn-success btn-sm">✓ Resolve</a>{% endif %}</td>
        {% endif %}
      </tr>
      {% endfor %}
    </table>
  </div>
</div>
{% endblock %}""")

# ── stock.html ─────────────────────────────────────────────────
open(f"{base}/stock.html","w").write("""{% extends 'base.html' %}
{% block title %}Stock{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">📊 Stock Levels</div><div class="page-subtitle">Current inventory status for all medicines</div></div>
</div>
<div class="card">
  <div class="table-wrap">
    <table>
      <tr><th>Medicine</th><th>Category</th><th>Current Qty</th><th>Min Required</th><th>Status</th><th>Last Updated</th></tr>
      {% for s in stock %}
      <tr>
        <td><strong>{{ s.name }}</strong></td>
        <td><span class="badge badge-info">{{ s.category }}</span></td>
        <td>
          <strong style="font-size:16px;color:{% if s.stock_status=='LOW' %}#DC2626{% elif s.stock_status=='MEDIUM' %}#D97706{% else %}#059669{% endif %}">
            {{ s.current_quantity }}
          </strong>
        </td>
        <td>{{ s.min_stock_level }}</td>
        <td>
          {% if s.stock_status=='LOW' %}<span class="badge badge-danger">⚠ LOW</span>
          {% elif s.stock_status=='MEDIUM' %}<span class="badge badge-warning">~ MEDIUM</span>
          {% else %}<span class="badge badge-success">✓ OK</span>{% endif %}
        </td>
        <td style="font-size:12px;color:#94A3B8">{{ s.last_updated }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>
</div>
{% endblock %}""")

# ── reports.html ───────────────────────────────────────────────
open(f"{base}/reports.html","w").write("""{% extends 'base.html' %}
{% block title %}Reports{% endblock %}
{% block content %}
<div class="page-header">
  <div><div class="page-title">📈 Reports & Analytics</div><div class="page-subtitle">JOIN queries, Aggregate functions, Subqueries</div></div>
</div>

<!-- Stock Value -->
<div class="card mb-4">
  <div class="section-title">💰 Stock Value per Medicine (JOIN + SUM aggregate)</div>
  <div class="table-wrap">
    <table>
      <tr><th>Medicine</th><th>Category</th><th>Total Units</th><th>Stock Value (₹)</th></tr>
      {% for r in stock_value %}
      <tr>
        <td><strong>{{ r.name }}</strong></td>
        <td><span class="badge badge-info">{{ r.category }}</span></td>
        <td>{{ r.total_units }}</td>
        <td><strong style="color:#059669">₹{{ "%.2f"|format(r.stock_value) }}</strong></td>
      </tr>
      {% endfor %}
    </table>
  </div>
</div>

<div class="grid-2 mb-4">
  <!-- Supplier Stats -->
  <div class="card">
    <div class="section-title">🚚 Supplier Performance (JOIN + COUNT)</div>
    <div class="table-wrap">
      <table>
        <tr><th>Supplier</th><th>City</th><th>Batches</th><th>Total Value (₹)</th></tr>
        {% for r in supplier_stats %}
        <tr>
          <td><strong>{{ r.supplier }}</strong></td>
          <td>{{ r.city }}</td>
          <td><span class="badge badge-info">{{ r.total_batches }}</span></td>
          <td>₹{{ "%.0f"|format(r.total_purchased_value) }}</td>
        </tr>
        {% endfor %}
      </table>
    </div>
  </div>

  <!-- Category Stats -->
  <div class="card">
    <div class="section-title">📊 Category Avg Price (AVG aggregate)</div>
    <div class="table-wrap">
      <table>
        <tr><th>Category</th><th>Medicines</th><th>Avg Price (₹)</th></tr>
        {% for r in category_stats %}
        <tr>
          <td><span class="badge badge-info">{{ r.category }}</span></td>
          <td>{{ r.medicine_count }}</td>
          <td><strong>₹{{ "%.2f"|format(r.avg_price) }}</strong></td>
        </tr>
        {% endfor %}
      </table>
    </div>
  </div>
</div>

<div class="grid-2">
  <!-- No valid batch — Subquery -->
  <div class="card">
    <div class="section-title">⚠️ No Valid Batch (Subquery)</div>
    {% if no_valid_batch %}
      <div class="table-wrap">
        <table>
          <tr><th>Medicine</th><th>Category</th></tr>
          {% for r in no_valid_batch %}
          <tr><td><strong>{{ r.name }}</strong></td><td><span class="badge badge-warning">{{ r.category }}</span></td></tr>
          {% endfor %}
        </table>
      </div>
    {% else %}
      <div class="empty"><div class="empty-icon">✅</div><p>All medicines have valid batches!</p></div>
    {% endif %}
  </div>

  <!-- Alert Stats -->
  <div class="card">
    <div class="section-title">🔔 Alert Summary (COUNT + GROUP BY)</div>
    {% for r in alert_stats %}
    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #E2E8F0">
      <span>
        {% if r.alert_type=='EXPIRY_CRITICAL' %}<span class="badge badge-danger">EXPIRY CRITICAL</span>
        {% elif r.alert_type=='EXPIRY_WARNING' %}<span class="badge badge-warning">EXPIRY WARNING</span>
        {% else %}<span class="badge badge-info">LOW STOCK</span>{% endif %}
      </span>
      <strong style="font-size:1.4rem;color:#1E3A5F">{{ r.total }}</strong>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}""")

print("All templates created!")

print("All templates created!")
