# Create your views here.
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
from .models import User, Attendance, Leave, Notification
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    AttendanceSerializer,
    LeaveSerializer,
    NotificationSerializer,
    UserUpdateSerializer
)

# Kullanıcı Kayıt (Register)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# Kullanıcı Profil Görüntüleme ve Güncelleme
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user


# Kullanıcı Giriş (Token Oluşturma)
class LoginView(APIView):
    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"detail": "Geçersiz kimlik bilgileri!"}, status=status.HTTP_401_UNAUTHORIZED)


# Kullanıcı Giriş-Çıkış Kaydı
class AttendanceView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        # Yetkililer tüm kayıtları görebilir, personel yalnızca kendi kayıtlarını görebilir.
        if self.request.user.role == 'yetkili':
            return Attendance.objects.all()
        return Attendance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# İzin Talebi Görüntüleme ve Oluşturma
class LeaveView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveSerializer

    def get_queryset(self):
        # Yetkililer tüm izinleri görebilir, personel yalnızca kendi izinlerini görebilir.
        if self.request.user.role == 'yetkili':
            return Leave.objects.all()
        return Leave.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# İzin Onaylama/Reddetme (Yetkili)
class LeaveApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != 'yetkili':
            return Response({"detail": "Bu işlem için yetkiniz yok!"}, status=status.HTTP_403_FORBIDDEN)
        try:
            leave = Leave.objects.get(pk=pk)
            status_value = request.data.get('status')
            if status_value not in ['approved', 'rejected']:
                return Response({"detail": "Geçersiz durum!"}, status=status.HTTP_400_BAD_REQUEST)
            leave.status = status_value
            leave.save()
            return Response({"detail": "İzin güncellendi!"})
        except Leave.DoesNotExist:
            return Response({"detail": "İzin bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)


# Bildirimler
class NotificationView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


# Yıllık Çalışma Raporu
class WorkSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'yetkili':
            return Response({"detail": "Bu işlem için yetkiniz yok!"}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.filter(role='personel')
        summary = []
        for user in users:
            total_hours = 0
            attendances = Attendance.objects.filter(user=user)
            for record in attendances:
                if record.check_in_time and record.check_out_time:
                    total_hours += (record.check_out_time.hour - record.check_in_time.hour)
            summary.append({
                "username": user.username,
                "total_hours": total_hours,
                "annual_leave_days": user.annual_leave_days
            })
        return Response(summary)
