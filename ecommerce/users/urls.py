from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect


def redirect_to_login(request):
    return redirect('login')


urlpatterns = [
    # auth endpoints
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', user_views.logout_view, name='logout'),

    # helper to redirect root to login
    path('', redirect_to_login, name='home'),

    # include shop URLs under /shop/
    path('shop/', include('shop.urls')),
    # admin user management
    path('admin/users/', user_views.user_list, name='user_list'),
    path('admin/users/create/', user_views.user_create, name='user_create'),
    path('admin/users/<int:pk>/edit/', user_views.user_update, name='user_update'),
    path('admin/users/<int:pk>/delete/', user_views.user_delete, name='user_delete'),
]
