from django.http import HttpResponse
from django.urls import path
from .views import (login_view,custom_login_redirect,logout_view,HomePageView,
                    HomePageAdminView,save_vouchers,user_form,user_list,user_list1,
                    postassesmentrequest,save_certifications,update_user,delete_user,
                    get_employee_certification_records,get_overall_cert_champ,insert_certfication)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('redirect/', custom_login_redirect, name='custom_login_redirect'),
    path('Home_page/', HomePageView.as_view(), name='home_page'),
    path('home_page_admin/', HomePageAdminView.as_view(), name='home_page_admin'),
    path('logout/', logout_view, name='logout'),
    path('save_vouchers/', save_vouchers, name='save_vouchers'),
    path('insert_user/', user_form, name='insert_user'),
    path('save_certifications/', save_certifications, name='save_certifications'),
    path('success/', lambda request: HttpResponse("User inserted successfully!")),
    path('user_list/', user_list, name='user_list'),
    path('api/postassesmentrequest/', postassesmentrequest, name='postassesmentrequest'),
    path('update_user/', update_user, name='update_user'),
    path('delete_user/<int:id>/', delete_user, name='delete_user'),
    path('get_employee_data/',get_employee_certification_records,name='get_employee_data'),
    path('get_overall_cert_champ/', get_overall_cert_champ, name='get_overall_cert_champ'),
    path('insert_certfication/', insert_certfication, name='insert_certfication'),
    #path('user_management/', user_management_view, name='user_management'),
]