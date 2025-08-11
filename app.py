from flask import Flask, render_template, request, session, redirect, url_for
import paramiko

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Change this to a secure random key in production

# Mikrotik connection details (static)
MIKROTIK_HOST = '192.168.15.254'
MIKROTIK_USER = 'admin'
MIKROTIK_PASS = 'i-konnect'

# Application login credentials (static, change these in production)
APP_USER = 'admin'
APP_PASS = 'password'

def human_readable_bytes(size):
    """Convert bytes to human-readable format (GB, MB, KB, bytes)."""
    if size == 0:
        return "0 bytes"
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"

def get_hotspot_users():
    """Connect to Mikrotik via SSH and retrieve detailed hotspot user information."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(MIKROTIK_HOST, username=MIKROTIK_USER, password=MIKROTIK_PASS)
    
    stdin, stdout, stderr = client.exec_command('/ip hotspot user print detail')
    output = stdout.read().decode('utf-8').strip()
    client.close()

    # Parse the output
    users = []
    current_user = {}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('Flags:'):
            continue
        if line and line[0].isdigit():
            if current_user:
                users.append(current_user)
            current_user = {}
            parts = line.split(None, 1)
            current_user['id'] = parts[0]
            if len(parts) > 1:
                line = parts[1]
            else:
                line = ''
        if line.startswith(';;;'):
            current_user['comment'] = line[3:].strip()
            continue
        # Parse key=value pairs
        for part in line.split():
            if '=' in part:
                key, value = part.split('=', 1)
                current_user[key] = value

    if current_user:
        users.append(current_user)

    # Exclude default-trial user
    users = [u for u in users if u.get('name') != '"default-trial"']

    return users

@app.route('/', methods=['GET', 'POST'])
def login():
    """Handle application login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == APP_USER and password == APP_PASS:
            session['logged_in'] = True
            session['viewed_details'] = {}  # Initialize viewed details
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Identifiants invalides')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """Display dashboard with totals and user details."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if 'viewed_details' not in session:
        session['viewed_details'] = {}

    viewed_details = session['viewed_details']

    if request.method == 'POST' and 'view_details' in request.form:
        entered_pass = request.form.get('password')
        username = request.form.get('username')
        
        users = get_hotspot_users()
        for u in users:
            if u.get('name') == username and u.get('password') == entered_pass:
                # Extract other details: all except displayed ones
                displayed = ['id', 'name', 'profile', 'uptime', 'consumption', 'percentage',
                           'limit-bytes-total', 'bytes-in', 'bytes-out', 'consumption_formatted',
                           'limit_formatted']
                details = {k: v for k, v in u.items() if k not in displayed}
                session['viewed_details'][username] = details
                session.modified = True
                break

    users = get_hotspot_users()

    total_users = len(users)
    total_consumption = 0
    total_limit = 0

    for user in users:
        bytes_in = int(user.get('bytes-in', '0'))
        bytes_out = int(user.get('bytes-out', '0'))
        consumption = bytes_in + bytes_out
        limit = int(user.get('limit-bytes-total', '0'))
        user['consumption'] = consumption
        user['consumption_formatted'] = human_readable_bytes(consumption)
        user['limit_formatted'] = human_readable_bytes(limit)
        user['percentage'] = (consumption / limit * 100) if limit > 0 else 0
        total_consumption += consumption
        total_limit += limit

    total_percentage = (total_consumption / total_limit * 100) if total_limit > 0 else 0
    total_consumption_formatted = human_readable_bytes(total_consumption)
    total_limit_formatted = human_readable_bytes(total_limit)

    return render_template('dashboard.html', users=users, total_users=total_users,
                         total_consumption_formatted=total_consumption_formatted,
                         total_limit_formatted=total_limit_formatted,
                         total_percentage=total_percentage, viewed_details=viewed_details)

@app.route('/logout')
def logout():
    """Handle logout."""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
