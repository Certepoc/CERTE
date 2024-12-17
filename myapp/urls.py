from django.urls import path
from .views import login_view,custom_login_redirect,logout_view,HomePageView,HomePageAdminView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('redirect/', custom_login_redirect, name='custom_login_redirect'),
    path('Home_page/', HomePageView.as_view(), name='home_page'),
    path('home_page_admin/', HomePageAdminView.as_view(), name='home_page_admin'),
    path('logout/', logout_view, name='logout'),
]