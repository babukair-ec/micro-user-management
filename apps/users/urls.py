from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import UserTokenObtainPairView, UserRegistrationView, CurrentUserView

urlpatterns = [
    path('token/', UserTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='auth_register'),
    path('me/', CurrentUserView.as_view(), name='auth_me'),
]
