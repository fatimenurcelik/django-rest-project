from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    AttendanceView,
    LeaveView,
    LeaveApprovalView,
    NotificationView,
    WorkSummaryView
)

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),

    # Giriş/Çıkış
    path('attendance/', AttendanceView.as_view(), name='attendance'),

    # İzinler
    path('leaves/', LeaveView.as_view(), name='leaves'),
    path('leaves/<int:pk>/approve/', LeaveApprovalView.as_view(), name='leave-approval'),

    # Bildirimler
    path('notifications/', NotificationView.as_view(), name='notifications'),

    # Çalışma Saatleri Raporu
    path('work-summary/', WorkSummaryView.as_view(), name='work-summary'),
]
