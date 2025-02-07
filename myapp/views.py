from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import sqlite3
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from datetime import datetime,date
from .models import *
from django.views.decorators.http import require_http_methods
import logging
from CERTE import settings
from django.conf import settings

logging.basicConfig(level=logging.INFO)

def redirect_to_section(request, section):
    return redirect(f'/Home_page/#{section}')

def connect_db():
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        if isinstance(conn, dict):
            raise ValueError("DATABASE_PATH should be a string, not a dictionary.")
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None


def get_db_schema():
    conn = connect_db()
    if conn is None:
        return {}  # Return empty schema if connection fails

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            schema_info[table_name] = [column[1] for column in columns]  # Column names
        return schema_info
    except sqlite3.Error as e:
        logging.error(f"Error fetching schema: {e}")
        return {}
    finally:
        conn.close()

def login_view(request):
    login_error = False
    logged_out = False

    logging.info(f"Request Method: {request.method}")
    logging.info(f"Request POST Data: {request.POST}")

    if request.method == 'POST':
        email = request.POST.get('email')  # Changed from username to email
        password = request.POST.get('password')

        logging.info(f"Received email: {email}")
        logging.info(f"Received password: {password}")  # Avoid logging passwords in production

        # Check for empty fields
        if not email or not password:
            login_error = True
            return redirect('/login/?login_error=true')

        conn = connect_db()
        if conn is None:
            login_error = True
            return redirect('/login/?login_error=true')

        cursor = conn.cursor()

        try:
            query = "SELECT * FROM Users WHERE email=?"  # Updated query to use email
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            # Log the database query result
            logging.info(f"Database query result: {user}")

            # Check if user exists and compare passwords directly
            if user is None or password != user[2]:  # Assuming user[2] is the plain password
                return redirect('/login/?login_error=true')

            # Assuming user[6] indicates admin status and user[7] indicates active status
            if user[6] == 1 and user[7] == 1:
                request.session['email'] = email  # Changed from username to email
                return redirect('home_page_admin')
            elif user[7] == 1:
                request.session['email'] = email  # Changed from username to email
                return redirect('home_page')
            else:
                return redirect('/login/?login_error=true')
        except sqlite3.Error as e:
            login_error = True
            logging.error(f"Database error: {e}")
        finally:
            conn.close()

    # Check for logout parameter in the URL
    if 'next' in request.GET and request.GET['next'] == 'logout':
        logged_out = True

    schema_info = get_db_schema()
    logging.info(f"Database schema: {schema_info}")

    return render(request, 'registration/login.html', {
        'login_error': login_error,
        'logged_out': logged_out,
    })

@csrf_exempt  # Use this only if you are not using CSRF tokens; otherwise, ensure CSRF protection is in place
def save_vouchers(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vouchers = data.get('items', [])
            saved_count = 0

            if not isinstance(vouchers, list):
                return JsonResponse({'success': False, 'error': 'Vouchers should be a list'}, status=400)

            if not vouchers:
                return JsonResponse({'success': False, 'error': 'No vouchers provided'}, status=400)

            insert_data = []
            errors = []

            for voucher in vouchers:
                try:
                    # Extract and validate voucher data
                    certification_name = str(voucher['certification_name'])
                    voucher_code = str(voucher['voucher_code'])

                    # Handle expiration_date conversion
                    expiration_date = convert_date_to_string(voucher['expiration_date'])
                    if expiration_date is None:
                        errors.append({'error': f'Invalid date format for voucher: {voucher}'})
                        continue

                    discount_percentage = voucher.get('discount_percentage', 0.0)

                    # Validate discount_percentage
                    if discount_percentage is not None:
                        try:
                            discount_percentage = float(discount_percentage)
                        except (ValueError, TypeError):
                            errors.append({'error': f'Invalid discount_percentage value: {voucher}'})
                            continue

                    # Get the current time for update_time
                    update_time = datetime.now().isoformat()  # ISO format for better compatibility

                    # Prepare data for insertion
                    insert_data.append((certification_name, voucher_code, expiration_date, discount_percentage,
                                        voucher.get('psid'), voucher.get('is_active'), update_time))
                except KeyError as e:
                    errors.append({'error': f'Missing key: {str(e)} in voucher {voucher}'})

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            conn = sqlite3.connect(settings.DATABASE_PATH)
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO vouchers (certification_name, voucher_code, expiration_date, discount_percentage, psid, is_active, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """

            cursor.executemany(insert_query, insert_data)
            saved_count = cursor.rowcount
            conn.commit()
            conn.close()

            return JsonResponse({'success': True, 'message': f'Successfully inserted {saved_count} vouchers.'},
                                status=201)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def validate_date_format(date_str):
    """Validate the date format (DD-MM-YYYY). Adjust as needed."""
    import re
    pattern = r'^\d{2}-\d{2}-\d{4}$'
    return re.match(pattern, date_str) is not None

def convert_date_to_string(date_input):
    # Handle integer input (Excel date serial number)
    if isinstance(date_input, int):
        base_date = datetime(1899, 12, 30)
        return (base_date + timedelta(days=date_input)).strftime('%Y-%m-%d')
    # Handle string input
    elif isinstance(date_input, str):
        try:
            # Check if it's in 'MM-DD-YYYY' format
            if re.match(r'^\d{2}-\d{2}-\d{4}$', date_input):
                date_obj = datetime.strptime(date_input, '%m-%d-%Y')
                return date_obj.strftime('%Y-%m-%d')
            # If it's already in 'YYYY-MM-DD', return it as is
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_input):
                return date_input
        except ValueError:
            return None
    return None

def insert_user(username, password, email, is_admin, is_active, PSID):
    logging.debug(f"Received username: '{username}', email: '{email}'")

    # Check if username and email are provided and not just whitespace
    if username is None or email is None or not username.strip() or not email.strip():
        logging.error("Username and email must be provided.")
        return "Username and email must be provided."

    username = username.strip()
    email = email.strip()

    logging.debug(f"Stripped username: '{username}', email: '{email}'")

    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()

    sql_query = ("INSERT INTO Users (username, password, email, is_admin, is_active, created_at, updated_at, PSID) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
    password = 'mypassword123'
    created_at = datetime.now()
    updated_at = created_at


    try:
        cursor.execute(sql_query, (username, password, email, is_admin, is_active, created_at, updated_at, PSID))
        conn.commit()

        cursor.execute("SELECT * FROM Users WHERE email = ?", (username,))
        user = cursor.fetchone()
        if user:
            logging.info(f"Inserted user: {username} into the database successfully.")
        else:
            logging.warning(f"User {username} not found after insertion.")
    except sqlite3.Error as e:
        logging.error(f"An error occurred while inserting user: {username}. Error: {e}")
        return f"An error occurred: {e}"
    finally:
        cursor.close()
        conn.close()

    return "User inserted successfully."

def insert_users_to_db(users):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()
    sql_query = ("INSERT INTO Users (username, password, email, created_at, updated_at, is_admin, is_active, PSID) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?)")

    created_at = datetime.now()
    updated_at = created_at

    try:
        cursor.executemany(sql_query, [
            (user['username'], user['password'], user['email'], created_at, updated_at,
             user.get('is_admin', 0),  # Default to 0 if not provided
             user['is_active'], user['PSID'])
            for user in users
        ])
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"An error occurred while inserting users: {e}")
        raise  # Reraise to handle in the calling function
    finally:
        cursor.close()
        conn.close()

@csrf_exempt
def insert_users_bulk(request):
    if request.method == 'POST':
        try:
            logging.info(f"Request body: {request.body.decode('utf-8')}")  # Log raw request body

            if not request.body:
                return JsonResponse({"error": "Request body is empty"}, status=400)

            data = json.loads(request.body)  # Load JSON data from request body

            # Validate that data is a list of users
            if not isinstance(data, list):
                return JsonResponse({"error": "Payload must be a list of users"}, status=400)

            for user in data:
                # Ensure each user has the required fields
                if not all(key in user for key in ['username', 'email', 'is_active', 'PSID']):
                    return JsonResponse(
                        {"error": "Each user must have username, email, is_active, and PSID"},
                        status=400)

                # Set default password
                user['password'] = user.get('password', 'mypassword123')

                # Set is_admin to 0 if not provided
                user.setdefault('is_admin', 0)

            logging.info(f"Received data: {data}")  # Log the received data

            # Call your insert function here
            insert_users_to_db(data)
            return JsonResponse({"status": "success"}, status=200)
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return JsonResponse({"error": "Database error occurred"}, status=500)
        except Exception as e:
            logging.error(f"Error in bulk insert: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

def update_user_in_db(user_id, username=None, email=None, is_admin=None, is_active=None):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()

    # Check if the user exists
    cursor.execute("SELECT password FROM Users WHERE id = ?", (user_id,))
    current_password = cursor.fetchone()

    if current_password is None:
        logging.error(f"User with ID: {user_id} does not exist.")
        return

    # Construct the SQL query dynamically
    sql_query = "UPDATE Users SET "
    updates = []
    params = []

    if username is not None:
        updates.append("username = ?")
        params.append(username)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if is_admin is not None:
        updates.append("is_admin = ?")
        params.append(1 if is_admin else 0)  # Convert boolean to integer
    if is_active is not None:
        updates.append("is_active = ?")
        params.append(1 if is_active else 0)  # Convert boolean to integer

    # Check if there are any updates to apply
    if updates:
        # Add the user_id to the parameters
        params.append(user_id)
        sql_query += ", ".join(updates) + " WHERE id = ?"

        # Debugging output
        print(f"SQL Query: {sql_query}")
        print(f"Parameters: {params}")

        try:
            cursor.execute(sql_query, params)
            conn.commit()
            logging.info(f"Updated user with ID: {user_id} successfully.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while updating user with ID: {user_id}. Error: {e}")
    else:
        logging.info(f"No updates provided for user with ID: {user_id}.")
def update_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        is_admin = request.POST.get('is_admin') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        print(f"Is Admin: {is_admin}, Is Active: {is_active}")  # Debugging output

        # Call the database update function
        update_user_in_db(user_id, username, email, is_admin, is_active)

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
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        PSID = request.POST.get('PSID')
        is_admin = request.POST.get('is_admin') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        if username is None or username == '':
            messages.error(request, "Username cannot be empty.")
            return redirect('home_page_admin')

        insert_user(username, password, email, is_admin, is_active, PSID)

        messages.success(request, f"User {username} has been successfully added.")

        return redirect('home_page_admin')

    return render(request, 'home_page_admin')

@csrf_exempt
def user_list(request):
    conn = None
    try:
        # Establish the database connection
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()

        # Fetch all users without pagination
        cursor.execute("SELECT id, username, email, is_admin, is_active, created_at, updated_at FROM Users;")
        users = cursor.fetchall()

        # Construct the user list
        user_list = [
            {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'is_admin': user[3] == 1,  # Assuming 1 means True
                'is_active': user[4] == 1,  # Assuming 1 means True
                'created_at': user[5],
                'updated_at': user[6],
            }
            for user in users
        ]

        return JsonResponse({
            'users': user_list,
            'total_users': len(user_list)  # Total users count
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

        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, is_admin, is_active FROM Users;")
        users = cursor.fetchall()

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
        return render(request, 'Home_page_Admin.html', {'error': 'Database operation failed'})

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

class HomePageView(TemplateView):
    template_name = 'Home_page.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Get the username from the session
        received_username = self.request.session.get('email', None)

        # Add the username to the context
        context['received_username'] = received_username

        return context

    def post(self, request, *args, **kwargs):
        # Handle POST request
        return self.get(request, *args, **kwargs)

class HomePageAdminView(TemplateView):

    def get(self, request):
        conn = None
        active_count = 0
        blocked_count = 0
        user_list = []

        # Retrieve the username from the session
        received_username = request.session.get('email', None)  # Get username from session

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

@login_required
def custom_login_redirect(request):
    if request.user.is_superuser:
        return redirect('home_page_admin')
    else:
        return redirect('home_page')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request,'You have been logged out')
    request.session.flush()
    return redirect('/accounts/login/?logout=true')


# View to handle the form submission
@csrf_exempt
def update_user_status(request, user_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=user_id)
            user.is_active = data.get('is_active', user.is_active)
            user.save()
            return JsonResponse({'message': 'User status updated successfully!'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
@csrf_exempt
def change_passw(request):
    if request.method == 'POST':
        user_id = request.session.get('email')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')


        # Fetch the user using the user_id
        conn = sqlite3.connect(settings.DATABASE_PATH)

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM Users WHERE email = ?", (user_id,))
            result = cursor.fetchone()

            if result is None:
                request.session['message'] = 'User not found.'
                request.session['message_type'] = 'error'
                return redirect('../')  # Redirect to your actual page

            stored_password = result[0]

            # Check if the current password matches the stored password
            if current_password != stored_password:
                request.session['message'] = 'Current password is incorrect.'
                request.session['message_type'] = 'error'
                return redirect('../')  # Redirect to your actual page
            else:
                cursor.execute("UPDATE Users SET password = ? WHERE email = ?", (new_password, user_id))
                conn.commit()  # Commit the changes

                request.session['message'] = 'Your password has been changed successfully.'
                request.session['message_type'] = 'success'
                return redirect('../')  # Redirect to your actual page

        except Exception as e:
            request.session['message'] = 'Failed to update password.'
            request.session['message_type'] = 'error'
            return redirect('../')  # Redirect to your actual page
        finally:
            conn.close()  # Ensure the connection is closed

    return render(request, 'Home_page.html')

@csrf_exempt
def change_passw1(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        # Fetch the user using the user_id
        conn = sqlite3.connect(settings.DATABASE_PATH)

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM Users WHERE id = ?", (user_id,))

            result = cursor.fetchone()
            if result is None:
                messages.error(request, 'User not found.')
                return redirect('../')  # Replace with your actual redirect URL

            stored_password = result[0]

            # Check if the current password matches the stored password
            if current_password != stored_password:
                messages.error(request, 'Current password is incorrect.')
                return redirect('../')  # Replace with your actual redirect URL
            else:
                cursor.execute("UPDATE Users SET password = ? WHERE id = ?", (new_password, user_id))
            conn.commit()  # Commit the changes
        except Exception as e:
            messages.error(request, 'Failed to update password.')
            return redirect('../')  # Replace with your actual redirect URL
        finally:
            conn.close()  # Ensure the connection is closed

        messages.success(request, 'Your password has been changed successfully.')
        return redirect('../')  # Redirect to the same page or wherever

    return render(request, 'Home_page.html')


@csrf_exempt  # Use this only if you are not using CSRF tokens; otherwise, ensure CSRF protection is in place
def save_certifications(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            certifications = data.get('items', [])
            saved_count = 0
            errors = []
            # Prepare the SQL insert query (removed validity_years)
            insert_query = """
                INSERT INTO certification (ID, name, provider, status)
                VALUES (?, ?, ?, ?);
            """
            # Prepare data for bulk insert (removed validity_years)
            insert_data = []
            for certification in certifications:
                insert_data.append((
                    certification['id'],
                    certification['name'],
                    certification['provider'],
                    certification['status']
                ))
            # Connect to the database
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.executemany(insert_query, insert_data)
                saved_count = cursor.rowcount  # Get the count of rows affected
                conn.commit()
            except Exception as e:
                errors.append({'error': str(e)})
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
def insert_certifications_to_db(certifications):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO certification (ID, name, provider, status)
        VALUES (?, ?, ?, ?);
    """
    try:
        cursor.executemany(insert_query, certifications)
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"An error occurred while inserting certifications: {e}")
        raise  # Re-raise the exception for higher-level handling
    finally:
        cursor.close()
        conn.close()

@csrf_exempt
def insert_cert_bulk(request):
    if request.method == 'POST':
        if request.content_type != 'application/json':
            return JsonResponse({'success': False, 'error': 'Invalid Content-Type, expected application/json'}, status=400)

        try:
            data = json.loads(request.body)
            logging.info(f"Received request body: {request.body.decode('utf-8')}")

            if not data:
                return JsonResponse({'success': False, 'error': 'No data provided'}, status=400)

            if not isinstance(data, list):
                return JsonResponse({'success': False, 'error': 'Expected a list of certifications'}, status=400)

            insert_data = []
            errors = []

            for cert in data:
                try:
                    certification_id = cert['ID']  # Ensure this is an integer
                    certification_name = cert['Name']
                    provider = cert['Provider']
                    status = cert['Status']
                    insert_data.append((certification_id, certification_name, provider, status))
                except KeyError as e:
                    errors.append(f'Missing key: {str(e)} in certification {cert}')
                except ValueError as e:
                    errors.append(f'Invalid value for Id in certification {cert}: {e}')

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            insert_certifications_to_db(insert_data)
            return JsonResponse({'success': True, 'message': f'Successfully saved {len(insert_data)} certifications.'})

        except json.JSONDecodeError:
            logging.error("Invalid JSON data")
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logging.error(f"Error in bulk insert: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
@csrf_exempt
def certification_list(request):
    conn = None
    try:
        # Establish the database connection
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()

        # Fetch all certifications without pagination
        cursor.execute("SELECT id, name, provider, status FROM certification;")
        certifications = cursor.fetchall()

        # Construct the certification list
        certification_list = [
            {
                'id': cert[0],
                'name': cert[1],
                'provider': cert[2],
                'status': cert[3],
            }
            for cert in certifications
        ]

        return JsonResponse({
            'certifications': certification_list,
            'total_certifications': len(certification_list)  # Total certifications count
        })

    except sqlite3.Error as e:
        return JsonResponse({'error': 'Database operation failed'}, status=500)

    finally:
        if conn:
            conn.close()

@csrf_exempt  # Use this only for testing; ensure CSRF protection in production
def update_certification(request, id):

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)  # Parse the JSON data from the request

            # Connect to the database and fetch the certification
            conn = sqlite3.connect(settings.DATABASE_PATH)
            cursor = conn.cursor()

            # Check if the certification exists
            cursor.execute("SELECT * FROM certification WHERE id = ?", (id,))
            certification = cursor.fetchone()

            if not certification:
                return JsonResponse({'error': 'Certification not found.'}, status=404)

            # Prepare SQL query for updates
            updates = []
            params = []

            if 'name' in data:
                updates.append("name = ?")
                params.append(data['name'])

            if 'provider' in data:
                updates.append("provider = ?")
                params.append(data['provider'])

            if 'status' in data:
                updates.append("status = ?")
                params.append(data['status'])

            # Check if there are any updates
            if not updates:
                return JsonResponse({'error': 'No fields to update.'}, status=400)

            # Append the ID for the WHERE clause
            params.append(id)
            sql_query = "UPDATE certification SET " + ", ".join(updates) + " WHERE id = ?"

            # Execute the update
            cursor.execute(sql_query, params)
            conn.commit()
            return JsonResponse({'success': 'Certification updated successfully.'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except sqlite3.Error as e:
            logging.error(f"An error occurred while updating certification with ID: {id}. Error: {e}")
            return JsonResponse({'error': 'Failed to update certification.'}, status=500)
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
        finally:
            cursor.close()
            conn.close()

    return JsonResponse({'error': 'Invalid request method'}, status=405)

#Leadership module request response
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
    quarter_dates = {1:(datetime(data_year,4,1),datetime(data_year,6,30)),
                     2: (datetime(data_year, 7, 1), datetime(data_year, 9, 30)),
                     3: (datetime(data_year, 10, 1), datetime(data_year, 12, 31)),
                     4: (datetime(data_year, 1, 1), datetime(data_year, 3, 31))}
    start_date=quarter_dates[data_quarter][0]
    end_date = quarter_dates[data_quarter][1]
    data_filter=EmployeeCertifications.objects.filter(update_date__gte=start_date,update_date__lte=end_date,certification_name__icontains=category,certification_status='Completed').values('employee_ps_no','employee_name').annotate(cert_count=Count('certification_name')).order_by('-cert_count')[:3]
    data1=list(data_filter.values('employee_name'))
    quarter_data={'quarter':data_quarter,'year':data_year}
    data={'emp_data':data1,'quarter_data':quarter_data}
    return JsonResponse(data,safe=False)

def get_overall_cert_champ(request):
    today = date.today()
    current_month = today.month
    current_year = today.year
    start_date =datetime(current_year-1, current_month, 1)
    end_date =datetime(current_year, current_month, 28)
    data_filter = EmployeeCertifications.objects.filter(update_date__gte=start_date, update_date__lte=end_date,certification_status='Completed' ).values(
        'employee_ps_no', 'employee_name').annotate(
        cert_count=Count('certification_name')).order_by('-cert_count')[:3]
    data = list(data_filter.values('employee_name','cert_count'))
    return JsonResponse(data, safe=False)

###enrollment Section ####
def get_providers(request):
    providers = []  # Initialize an empty list for providers
    if request.method == 'GET':
        conn = sqlite3.connect(settings.DATABASE_PATH)

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT Provider FROM certification")
            providers = cursor.fetchall()
            providers = [provider[0] for provider in providers]  # Extract provider names
        except sqlite3.Error as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()  # Ensure the cursor is closed
            conn.close()  # Close the connection

    return JsonResponse(providers, safe=False)
def get_names_by_provider(request):
    names=[]
    if request.method == 'GET':
        provider = request.GET.get('provider')
        conn = sqlite3.connect(settings.DATABASE_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM certification WHERE Provider = ?", (provider,))
            names = cursor.fetchall()
        except sqlite3.Error as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()  # Ensure the cursor is closed
            conn.close()  # Close the connection

    return JsonResponse(list(names), safe=False)

def save_enrollment(request):
    received_username = request.session.get('username')

    # Connect to the SQLite database
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Execute the query using the correct placeholder
        cursor.execute("SELECT PSID FROM Users WHERE username = ?", (received_username,))
        psid = cursor.fetchone()
        psid=int(psid[0])

        if request.method == "POST":
            provider = request.POST.get('provider')
            certname = request.POST.get('name')
            try:
                enrollment_rec = EmployeeCertifications.objects.filter(
                    employee_name=received_username,
                    certification_name=certname
                ).exclude(certification_status__icontains='fail')

                if enrollment_rec.exists():
                    return JsonResponse({'message': 'User already registered.'})
                else:
                    # If record doesn't exist, create a new record
                    obj = EmployeeCertifications.objects.create(
                        employee_name=received_username,
                        employee_ps_no=psid,  # Replace with actual logic to fetch PS No
                        certification_name=certname,
                        certification_status='enrolled',
                        provider='provider',
                        update_date=timezone.now()  # Use timezone-aware datetime
                    )
                    return redirect('redirect_to_section', section='enrollment')
            except Exception as e:
                # Handle exceptions
                print(f"Error: {e}")
                return JsonResponse({'error': 'An error occurred.'})
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

    return redirect('redirect_to_section', section='enrollment')
def show_enrollment(request):
    received_username = request.session.get('username')

    if not received_username:
        return JsonResponse({'error': 'User not logged in.'}, status=401)

    # Connect to the SQLite database
    conn = sqlite3.connect(settings.DATABASE_PATH)
    name = None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM Users WHERE username = ?", (received_username,))
        name = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return JsonResponse({'error': 'Database error occurred.'}, status=500)
    finally:
        cursor.close()  # Ensure the cursor is closed
        conn.close()  # Close the connection

    # Check if the user exists
    if not name:
        return JsonResponse({'error': 'User not found.'}, status=404)

    # Fetch enrollment data
    enrollment_data = EmployeeCertifications.objects.filter(employee_name=received_username).values('id',
                                                                                                    'certification_name',
                                                                                                    'certification_status','voucher_code')

    # Return enrollment data as JSON
    return JsonResponse(list(enrollment_data), safe=False)

###Voucher request response user module
@csrf_exempt
def update_certification_status(request):
    if request.method == 'POST':
        certification_name = request.POST.get('certification_name')
        new_status = request.POST.get('new_status')
        username = request.session.get('username')

        try:
            certification = EmployeeCertifications.objects.get(
                employee_name=username,
                certification_name=certification_name
            )
            certification.certification_status = new_status
            certification.save()
            return JsonResponse({'success': True})
        except EmployeeCertifications.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Certification not found'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
@csrf_exempt
def update_exam_date(request):
    if request.method == 'POST':
        certification_name = request.POST.get('certification_name')
        date = request.POST.get('date')
        username = request.session.get('username')
        try:
            certification = EmployeeCertifications.objects.get(
                employee_name=username,
                certification_name=certification_name
            )
            certification.exam_date = date
            certification.save()
            return redirect('redirect_to_section', section='dashboard')
        except EmployeeCertifications.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Certification not found'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

####Admin interphase request response functionality
def get_wcp_request_records(request):
    wcp_request_data = EmployeeCertifications.objects.filter(certification_status='WCP Test Requested').values('id','certification_name','employee_name')
    print(wcp_request_data)
    return JsonResponse(list(wcp_request_data), safe=False)

def get_wcp_completed_records(request):
    wcp_completion_data = EmployeeCertifications.objects.filter(certification_status='WCP Completed').values('id','certification_name','employee_name')
    return JsonResponse(list(wcp_completion_data), safe=False)

@csrf_exempt
def update_status_voucher(request, pk):
    if request.method == 'POST':
        obj = get_object_or_404(EmployeeCertifications, id=pk)  # Use get_object_or_404 for better error handling
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'decline':
            obj.certification_status = 'WCP Failed'
        elif action == 'assign':
            obj.certification_status = 'WCP Assigned'

        obj.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

def certificate_upload(request):
    if request.method == 'POST':
        # Get form fields
        name = request.POST.get('name')
        exam_result = request.POST.get('exam_result')
        request_id = request.POST.get('request_id')
        request_id_value = request.POST.get('request_id_value')

        user = request.session.get('username')

        # Get PSID
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT PSID FROM Users WHERE username = ?", (user,))
        psid = cursor.fetchone()
        conn.close()  # Close the database connection

        if psid:
            psid = int(psid[0])
        else:
            return HttpResponse("User PSID not found", status=400)

        # Get or create the EmployeeCertifications record
        cert, created = EmployeeCertifications.objects.get_or_create(
            employee_name=user,
            certification_name=name,
            defaults={
                'employee_ps_no': psid,
                'certification_status': 'enrolled',
                'update_date': timezone.now()
            }
        )

        # Update certification status based on exam result
        if exam_result == 'fail':
            cert.certification_status = 'Failed'
            cert.uploaded_certificate = 'yes'
        else:
            cert.certification_status = 'Completed'
            cert.uploaded_certificate = 'yes'

        # Update request ID if provided
        if request_id == "yes" and request_id_value:
            cert.request_id = request_id_value

        cert.save()

    return redirect('redirect_to_section', section='dashboard')

@csrf_exempt
def upload_certificate_request(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON payload
            data = json.loads(request.body)
            print("Incoming data:", data)  # Log incoming data

            # Validate required fields in the payload
            required_fields = ['employee_psno', 'platform', 'certificate_name', 'upload_status']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required fields.',
                    'missing_fields': missing_fields
                }, status=400)

            insert_query = """
                INSERT INTO useruploadedcertificates 
                (EMPLOYEEPSNO, PLATFORM, CERTIFICATENAME, UPLOADSTATUS, CREATED_AT) 
                VALUES (?, ?, ?, ?, ?)
            """

            created_at = data.get('created_at', datetime.now().strftime('%Y-%m-%d'))
            insert_data = (
                data['employee_psno'],
                data['platform'],
                data['certificate_name'],
                data['upload_status'],
                created_at
            )

            # Connect to the database and execute the query
            conn = sqlite3.connect(settings.DATABASE_PATH)
            cursor = conn.cursor()
            saved_count = 0
            errors = []

            try:
                cursor.execute(insert_query, insert_data)
                conn.commit()
                saved_count = cursor.rowcount
                print(f"Successfully inserted {saved_count} record(s).")
            except sqlite3.Error as e:
                conn.rollback()
                errors.append({'error': str(e)})
                print(f"Database error: {e}")
            finally:
                conn.close()

            return JsonResponse({
                'success': True,
                'message': f'Successfully saved {saved_count} certificate(s).',
                'errors': errors,
                'redirect_url': reverse('home_page_admin')
            })


        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)


        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def get_voucher(request):
    update_time=datetime.now()
    data = json.loads(request.body)
    request_id = data.get('recordId')
    certification = data.get('certificationName')

    if not certification:
        return JsonResponse({'error': 'Certification name is required'}, status=400)

    record = get_object_or_404(EmployeeCertifications, id=request_id)
    psid = record.employee_ps_no

    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Get the count of available vouchers
        cursor.execute("""
            SELECT COUNT(*) 
            FROM vouchers 
            WHERE certification_name = ? AND PSID IS NULL
        """, (certification,))
        available_vouchers = cursor.fetchone()[0]

        cursor.execute("""
            SELECT voucher_code FROM vouchers 
            WHERE certification_name = ? AND PSID IS NULL
            LIMIT 1
        """, (certification,))

        result = cursor.fetchone()

        if result:
            voucher_code = result[0]
            cursor.execute("""
                UPDATE vouchers 
                SET PSID = ? , update_time= ?
                WHERE certification_name = ? AND voucher_code = ?
            """, (psid,update_time, certification, voucher_code))

            conn.commit()

            record.voucher_code = voucher_code
            record.certification_status = 'Voucher Assigned'
            record.save()

            return JsonResponse({
                'voucher_code': voucher_code,
                'available_vouchers': available_vouchers - 1  # Subtract 1 as we've just assigned one
            })
        else:
            return JsonResponse({
                'error': 'No voucher available for this certification',
                'available_vouchers': 0
            }, status=404)
