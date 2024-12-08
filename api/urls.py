from django.urls import path

from ml.views import PredictAccessView
from users.views import register_user, login_user, chain_valid, get_chain, list_users, update_access_level, \
    update_user_role, delete_user

urlpatterns = [
    path('register/', register_user, name='register-user'),
    path('login/', login_user, name='login-user'),
    path('chain-valid/', chain_valid, name='chain-valid'),
    path('get-chain/', get_chain, name='get-chain'),
    path('predict-access/', PredictAccessView.as_view(), name='predict-access'),

    path("users/", list_users, name="list_users"),
    path("users/update-access-level/", update_access_level, name="update_access_level"),
    path("users/update-role/", update_user_role, name="update_user_role"),
    path('users/<int:user_id>/', delete_user, name='delete_user'),
]
