const API_BASE = '/api/v1';

// Check if we have a token and user data in localStorage
const token = localStorage.getItem('token');
const user = JSON.parse(localStorage.getItem('user') || 'null');

if (token && user) {
    showDashboard();
    loadDashboardData();
} else {
    showLogin();
}

function showLogin() {
    document.getElementById('loginContainer').style.display = 'flex';
    document.getElementById('dashboard').style.display = 'none';
}

function showDashboard() {
    document.getElementById('loginContainer').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('userName').textContent = user.username;
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok) {
            // Login successful
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            user = data.user;
            showDashboard();
            loadDashboardData();
        } else {
            // Login failed
            document.getElementById('loginError').textContent = data.message;
        }
    } catch (error) {
        console.error('Login error:', error);
        document.getElementById('loginError').textContent = 'Login failed. Please try again.';
    }
});

async function loadDashboardData() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/system/health`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('systemHealth').innerHTML = `
                CPU: ${data.data.cpu_usage}%<br>
                Memory: ${data.data.memory_usage}%<br>
                Database: ${data.data.database_status}
            `;
        } else {
            document.getElementById('systemHealth').textContent = 'Failed to load system health';
        }
    } catch (error) {
        console.error('Error loading system health:', error);
        document.getElementById('systemHealth').textContent = 'Error loading system health';
    }

    // Load other data similarly...
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    showLogin();
}