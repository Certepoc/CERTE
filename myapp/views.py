import calendar
from django.db.models import Count
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout,get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
import sqlite3
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.urls import reverse
from datetime import datetime,date
from .forms import CertificationForm
from .models import *
from django.views.decorators.http import require_http_methods
import logging
from CERTE import settings

def connect_db():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def login_view(request):
    login_error = False
    logged_out = False


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check for empty fields
        if not username or not password:
            login_error = True
            return redirect('/login/?login_error=true')  # Redirect for empty fields

        # Connect to the database
        conn = connect_db()
        if conn is None:
            login_error = True
            return redirect('/login/?login_error=true')  # Redirect if connection fails

        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM Users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()

            if user is None:
                print("Redirecting due to invalid credentials")
                login_url = reverse('login')  # This resolves to '/accounts/login/'
                full_redirect_url = f"{request.scheme}://{request.get_host()}/accounts{login_url}?login_error=true"
                print(f"Redirecting to: {full_redirect_url}")  # Debugging line
                return redirect(full_redirect_url)

            else:
                # Assuming user[6] indicates admin status and user[7] indicates active status
                if user[6] == 1 and user[7] == 1:
                    request.session['username'] = username  # Store username in session
                    return redirect('home_page_admin')
                elif user[7] == 1:
                    request.session['username'] = username  # Store username in session
                    # return JsonResponse({'redirect': reverse('home_page')}, status=200)
                    return redirect('home_page')
                else:
                    return redirect('/login/?login_error=true')  # Redirect for inactive account
        except sqlite3.Error as e:
            print(f"Database error: {e}")  # Print the error for debugging
            login_error = True
        finally:
            conn.close()

    # Check for logout parameter in the URL
    if 'next' in request.GET and request.GET['next'] == 'logout':
        logged_out = True

    return render(request, 'registration/login.html', {
        'login_error': login_error,
        'logged_out': logged_out,
    })


@csrf_exempt  # Use this only if you are not using CSRF tokens; otherwise, ensure CSRF protection is in place
def save_vouchers(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Incoming data:", data)  # Log incoming data
            vouchers = data.get('items', [])

            # Verify that vouchers is a list
            if not isinstance(vouchers, list):
                return JsonResponse({'success': False, 'error': 'Vouchers should be a list'}, status=400)

            if not vouchers:
                return JsonResponse({'success': False, 'error': 'No vouchers provided'}, status=400)

            saved_count = 0
            errors = []

            # Prepare the SQL insert query
            insert_query = """
                INSERT INTO vouchers (certification_name, voucher_code, expiration_date)
                VALUES (?, ?, ?);
            """

            # Prepare data for bulk insert
            insert_data = []
            for voucher in vouchers:
                try:
                    insert_data.append((
                        voucher['certification_name'],
                        voucher['voucher_code'],
                        voucher['expiry_date']
                    ))
                except KeyError as e:
                    errors.append({'error': f'Missing key: {str(e)} in voucher {voucher}'})

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            # Connect to the database
            conn = sqlite3.connect(settings.DATABASE_PATH)
            cursor = conn.cursor()

            try:
                print("Inserting data:", insert_data)  # Log data being inserted
                cursor.executemany(insert_query, insert_data)
                saved_count = cursor.rowcount  # Get the number of rows affected
                conn.commit()
                print(f"Successfully inserted {saved_count} rows.")  # Log successful insertion
            except sqlite3.Error as e:
                conn.rollback()  # Rollback on error
                errors.append({'error': str(e)})
                print(f"Database error: {e}")  # Log database error
            finally:
                conn.close()  # Ensure the connection is closed

            return JsonResponse({
                'success': True,
                'message': f'Successfully saved {saved_count} vouchers.',
                'total_count': len(vouchers),
                'errors': errors,
                'redirect_url': reverse('home_page_admin')
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except sqlite3.Error as e:
            return JsonResponse({'success': False, 'error': f'Database error: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def insert_user(username, password, email, is_admin, is_active):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()

    sql_query = ("INSERT INTO Users (username, password, email, is_admin, is_active, created_at, updated_at) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?)")
    created_at = datetime.now()
    updated_at = created_at

    try:
        cursor.execute(sql_query, (username, password, email, is_admin, is_active, created_at, updated_at))
        conn.commit()
        cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            logging.info(f"Inserted user: {username} into the database successfully.")
        else:
            logging.warning(f"User {username} not found after insertion.")
    except sqlite3.Error as e:
        logging.error(f"An error occurred while inserting user: {username}. Error: {e}")
    finally:
        cursor.close()
        conn.close()


def update_user_in_db(user_id, username=None, password=None, email=None, is_admin=None, is_active=None):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()

    # Step 1: Fetch the current password
    cursor.execute("SELECT password FROM Users WHERE id = ?", (user_id,))
    current_password = cursor.fetchone()

    # Check if the user exists
    if current_password is None:
        logging.error(f"User with ID: {user_id} does not exist.")
        return  # Optionally raise an exception or handle accordingly

    current_password = current_password[0]  # Get the current password

    # Step 2: Construct the SQL query dynamically based on the parameters provided
    sql_query = "UPDATE Users SET "
    updates = []
    params = []

    if username is not None:
        updates.append("username = ?")
        params.append(username)
    if password is not None:
        updates.append("password = ?")
        params.append(password)
    else:
        # If no new password is provided, keep the current password
        updates.append("password = ?")
        params.append(current_password)

    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if is_admin is not None:
        updates.append("is_admin = ?")
        params.append(is_admin)
    if is_active is not None:
        updates.append("is_active = ?")
        params.append(is_active)

    # Add the user_id to the parameters
    params.append(user_id)
    sql_query += ", ".join(updates) + " WHERE id = ?"

    try:
        cursor.execute(sql_query, params)
        conn.commit()
        logging.info(f"Updated user with ID: {user_id} successfully.")
    except sqlite3.Error as e:
        logging.error(f"An error occurred while updating user with ID: {user_id}. Error: {e}")
    finally:
        cursor.close()
        conn.close()

def update_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_admin = 'is_admin' in request.POST
        is_active = 'is_active' in request.POST

        # Call the database update function
        update_user_in_db(user_id, username, password, email, is_admin, is_active)

        return redirect('home_page_admin')  # Redirect after successful update

    # If the request method is not POST, redirect or render an error page
    return redirect('home_page_admin')

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, id):
    logging.info(f"Received request to delete user with ID: {id}")
    if id < 0:
        logging.error("Invalid user ID provided.")
        return JsonResponse({'error': 'Invalid user ID provided.'}, status=400)

    sql_query = "DELETE FROM Users WHERE id = ?"

    try:
        with sqlite3.connect(settings.DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, (id,))
            conn.commit()

            if cursor.rowcount > 0:
                logging.info(f"Deleted user with ID: {id} successfully.")
                return JsonResponse({'message': 'User deleted successfully'}, status=204)
            else:
                logging.warning(f"No user found with ID: {id}.")
                return JsonResponse({'error': 'No user found with the given ID'}, status=404)

    except sqlite3.Error as e:
        logging.error(f"An error occurred while deleting user with ID: {id}. Error: {e}")
        return JsonResponse({'error': 'An error occurred while deleting the user'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def user_form(request):
    if request.method == 'POST':
        print(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        is_admin = request.POST.get('is_admin') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        print(
            f"Username: {username}, Password: {password}, Email: {email}, Is Admin: {is_admin}, Is Active: {is_active}")

        if username is None or username == '':
            logging.error("Username is empty or None.")
            messages.error(request, "Username cannot be empty.")
            return redirect('home_page_admin')

        insert_user(username, password, email, is_admin, is_active)

        messages.success(request, f"User {username} has been successfully added.")

        return redirect('home_page_admin')

    return render(request, 'home_page_admin')

@csrf_exempt
def user_list(request):
    conn = None
    try:
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        # Establish the database connection
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()

        # Get total user count for pagination
        cursor.execute("SELECT COUNT(*) FROM Users;")
        total_users = cursor.fetchone()[0]

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Fetch users with pagination
        cursor.execute("SELECT id, username, email, is_admin, is_active, created_at, updated_at  FROM Users LIMIT ? OFFSET ?;", (per_page, offset))
        users = cursor.fetchall()

        # Construct the user list
        user_list = [
            {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'is_admin': user[3] == 1,  # Assuming 1 means True
                'is_active': user[4] == 1,   # Assuming 1 means True
                'created_at': user[5],
                'updated_at': user[6],
            }
            for user in users
        ]

        total_pages = (total_users + per_page - 1) // per_page  # Calculate total pages

        return JsonResponse({
            'users': user_list,
            'total_users': total_users,
            'total_pages': total_pages,
            'current_page': page
        })

    except sqlite3.Error as e:
        return JsonResponse({'error': 'Database operation failed'}, status=500)

    finally:
        if conn:
            conn.close()
@csrf_exempt
def user_list1(request):
    conn = None
    try:
        # Establish the database connection
        conn = sqlite3.connect(settings.DATABASE_PATH)
        print("Database connection successful")

        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, is_admin, is_active FROM Users;")
        users = cursor.fetchall()
        print("Query executed successfully")

        # Construct the user list
        user_list = [
            {
                'id': user[0],
                'username': user[1],
                'password': user[2],
                'email': user[3],
                'created_at': user[4],
                'updated_at': user[5],
                'is_admin': user[6] == 1,  # Assuming 1 means True
                'is_active': user[7] == 1   # Assuming 1 means True
            }
            for user in users
        ]

        return render(request, 'Home_page_Admin.html', {'users': user_list})

    except sqlite3.Error as e:
        print(f"Database operation failed: {e}")
        return render(request, 'Home_page_Admin.html', {'error': 'Database operation failed'})

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()
            print("Database connection closed")



class HomePageView(TemplateView):
    template_name = 'Home_page.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Get the username from the session
        received_username = self.request.session.get('username', None)

        # Add the username to the context
        context['received_username'] = received_username

        return context


class HomePageAdminView(TemplateView):

    def get(self, request):
        conn = None
        active_count = 0
        blocked_count = 0
        user_list = []

        # Retrieve the username from the session
        received_username = request.session.get('username', None)  # Get username from session

        try:
            conn = sqlite3.connect(settings.DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users;")
            users = cursor.fetchall()

            for user in users:
                user_info = {
                    'id': user[0],
                    'username': user[1],
                    'password': user[2],
                    'email': user[3],
                    'created_at': user[4].date() if isinstance(user[4], datetime) else user[4],
                    'updated_at': user[5].date() if isinstance(user[5], datetime) else user[5],
                    'is_admin': user[6],
                    'is_active': user[7]
                }
                user_list.append(user_info)

                # Count active and blocked users
                if user[7] == 1:
                    active_count += 1
                else:
                    blocked_count += 1

            return render(request, 'Home_page_Admin.html', {
                'users': user_list,
                'active_count': active_count,
                'blocked_count': blocked_count,
                'received_username': received_username  # Pass it to the template
            })

        except sqlite3.Error as e:
            return render(request, 'Home_page_Admin.html', {'error': 'Database operation failed'})

        finally:
            if conn:
                conn.close()

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
    request.session.flush()
    return redirect('/accounts/login/?logout=true')

def postassesmentrequest(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Expecting a single assessment request
            request_data = data.get('assessment_request', {})
            errors = []

            # Validate required fields
            if not all(key in request_data for key in ['employeeid', 'assesmentrequested', 'assesmentrequesteddate']):
                return JsonResponse({
                    'success': False,
                    'message': 'Missing required fields.',
                    'errors': errors,
                })

            # Prepare the insert query
            insert_query = """
            INSERT INTO TBLMSTASSESMENTREQUESTS (EMPLOYEEID, ASSESMENTREQUESTED, ASSESMENTREQUESTEDDATE)
            VALUES (?, ?, ?)
            """
            insert_data = (
                request_data['employeeid'],
                request_data['assesmentrequested'],
                request_data['assesmentrequesteddate']
            )

            # Connect to the database
            conn = sqlite3.connect(settings.DATABASE_PATH)
            cursor = conn.cursor()
            try:
                cursor.execute(insert_query, insert_data)  # Use execute for a single insert
                conn.commit()  # Commit the transaction
                saved_count = cursor.rowcount  # Get the number of rows inserted
            except Exception as e:
                errors.append({'error': str(e)})
                return JsonResponse({'success': False, 'errors': errors}, status=500)
            finally:
                conn.close()  # Ensure the connection is closed

            return JsonResponse({
                'success': True,
                'message': f'Successfully saved {saved_count} assessment request.',
                'errors': errors,
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@csrf_exempt  # Use this only if you are not using CSRF tokens; otherwise, ensure CSRF protection is in place
def save_certifications(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            certifications = data.get('items', [])
            saved_count = 0
            errors = []
            # Prepare the SQL insert query
            insert_query = """
                INSERT INTO certification (ID, name, provider, status, validity_years)
                VALUES (?, ?,?, ?, ?);
            """
            # Prepare data for bulk insert
            insert_data = []
            for certification in certifications:
                insert_data.append((
                    certification['id'],
                    certification['name'],
                    certification['provider'],
                    certification['status'],
                    certification['validity_years']
                ))
            # Connect to the database
            conn = connect_db()
            print("Database connected:", conn)
            cursor = conn.cursor()
            try:
                cursor.executemany(insert_query, insert_data)
                saved_count = cursor.rowcount  # Get the count of rows affected
                conn.commit()
                print(f"Inserted {saved_count} records")
            except Exception as e:
                errors.append({'error': str(e)})
                print(f"Error during insert: {e}")
            finally:
                cursor.close()
                conn.close()
            return JsonResponse({
                'success': True,
                'message': f'Successfully saved {saved_count} certifications.',
                'total_count': len(certifications),
                'errors': errors,
                'redirect_url': reverse('home_page_admin')
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except sqlite3.Error as e:
            return JsonResponse({'success': False, 'error': f'Database error: {str(e)}'}, status=500)

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

#view to get employee certification details from table
def get_employee_certification_records(request):
    if request.method=='POST':
        jdata=json.loads(request.body)
        category=jdata.get('category')
    quarter_dict = {1: ['Apr', 'May', 'Jun'], 2: ['Jul', 'Aug', 'Sep'],
                    3: ['Oct', 'Nov', 'Dec'], 4: ['Jan', 'Feb', 'Mar']}

    today = date.today()
    current_month=today.strftime("%b")
    current_year=today.year
    data_year = current_year
    for key,value_list in quarter_dict.items():
        if current_month in value_list:
            current_quarter=key
    if key==4:
        data_year=current_year-1
        data_quarter=key-1
    elif key==1:
        data_quarter=4
    else:
        data_quarter = key - 1
    data_quarter=3
    data_year=2024
    quarter_dates = {1:(datetime(data_year,4,1),datetime(data_year,6,30)),
                     2: (datetime(data_year, 7, 1), datetime(data_year, 9, 30)),
                     3: (datetime(data_year, 10, 1), datetime(data_year, 12, 31)),
                     4: (datetime(data_year, 1, 1), datetime(data_year, 3, 31)) }
    start_date=quarter_dates[data_quarter][0]
    end_date = quarter_dates[data_quarter][1]
    data_filter=EmployeeCertifications.objects.filter(update_date__gte=start_date,update_date__lte=end_date,certification_details__icontains=category).values('employee_ps_no','employee_name','employee_designation').annotate(cert_count=Count('certification_details')).order_by('-cert_count')[:3]
    data=list(data_filter.values('employee_name','employee_designation'))
    return JsonResponse(data,safe=False)

def get_overall_cert_champ(request):
    today = date.today()
    current_month = today.month
    current_year = today.year
    start_date =datetime(2023, 4, 1)
    end_date =datetime(current_year, current_month, 31)
    data_filter = EmployeeCertifications.objects.filter(update_date__gte=start_date, update_date__lte=end_date).values(
        'employee_ps_no', 'employee_name', 'employee_designation').annotate(
        cert_count=Count('certification_details')).order_by('-cert_count')[:3]
    data = list(data_filter.values('employee_name', 'employee_designation','cert_count'))
    return JsonResponse(data, safe=False)
def insert_certfication(request):
    # return render(request, 'certdata.html')
    if request.method=="POST":
        form=CertificationForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('cert_records')
    else:
        form=CertificationForm()
        return render(request,'certification_form.html',{'form':form})
# View to handle the form submission
