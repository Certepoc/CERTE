from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import sqlite3
from django.views.generic import TemplateView
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User


def connect_db():
    db_path = 'C:\\Users\\10821476\\PycharmProjects\\pythonProject\\CERTE\\employees.db'
    return sqlite3.connect(db_path)


def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Commit changes and close connection
    conn.commit()
    conn.close()
def login_view(request):
    login_error = False
    logged_out = False


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Connect to the SQLite database
        conn = connect_db()
        cursor = conn.cursor()

        # Query to check if the user exists and the password matches
        # cursor.execute("SELECT * FROM auth_users WHERE username=? AND password=?", (username, password))
        # user = cursor.fetchone()

        # Close the database connection
        conn.close()

        # if user:
        #     # Log the user in
        #     user_instance = User.objects.get(username=username)  # Optionally retrieve User model instance
        #     django_login(request, user_instance)
        #
        #     return redirect('Home_page')
        # else:
        #     login_error = True

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
