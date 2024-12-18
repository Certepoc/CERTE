from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
import sqlite3
from django.views.generic import TemplateView
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User

def connect_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('C:\\Users\\10821476\\PycharmProjects\\pythonProject\\CERTE\\db.sqlite3')  # Change this to your database path
    conn.row_factory = sqlite3.Row  # Allows access to columns by name
    return conn

def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Create a new table for custom users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()
initialize_db()

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Hash the password
        hashed_password = make_password(password)

        # Connect to the SQLite database
        conn = connect_db()
        cursor = conn.cursor()

        # Insert the new user into the custom_users table
        cursor.execute("INSERT INTO Employees (username, password) VALUES (?, ?)", (username, hashed_password))

        # Commit changes and close connection
        conn.commit()
        conn.close()

        return redirect('login')  # Redirect to the login page after registration

    return render(request, 'registration/register.html')

def login_view(request):
    login_error = False
    logged_out = False

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Attempting login for user: {username}")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Employees WHERE username=?", (username,))
        user = cursor.fetchone()

        # Close the database connection
        conn.close()

        if user and check_password(user[2],password):
            user_instance = User(username=username)  # Create a User instance
            login(request, user_instance)
            return redirect('Home_page')
        else:
            login_error = True

    if 'next' in request.GET and request.GET['next'] == 'logout':
        logged_out = True

    return render(request, 'registration/login.html', {
        'login_error': login_error,
        'logged_out': logged_out
    })

class HomePageView(TemplateView):
    template_name = 'Home_page.html'

class HomePageAdminView(TemplateView):
    template_name = 'Home_page_Admin.html'

# def home_page_view(request):
#     return render(request, 'Home_page_Admin.html')

@login_required
def custom_login_redirect(request):
    if request.user.is_superuser:
        return redirect('home_page_admin')  # Assuming you have a named URL
    else:
        return redirect('home_page')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request,'You have been logged out')
    return redirect('/accounts/login/?logout=true')
