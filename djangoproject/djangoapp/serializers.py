from rest_framework import serializers
from .models import User, Attendance, Leave, Notification


# Kullanıcı Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'annual_leave_days', 'date_joined']


# Yeni Kullanıcı Kayıt (Register) Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Şifreler uyuşmuyor!"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Bu alan veritabanında saklanmayacak.
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])  # Şifreyi hash'leyerek kaydeder.
        user.save()
        return user


# Giriş/Çıkış Serializer
class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Kullanıcı bilgileri sadece okunabilir.

    class Meta:
        model = Attendance
        fields = ['id', 'user', 'date', 'check_in_time', 'check_out_time', 'late_minutes']

    def create(self, validated_data):
        attendance = Attendance.objects.create(**validated_data)
        # Geç kalma süresini hesapla
        attendance.calculate_late_minutes()
        return attendance


# İzin Serializer
class LeaveSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # İzin talep eden kullanıcı bilgileri.

    class Meta:
        model = Leave
        fields = ['id', 'user', 'start_date', 'end_date', 'status', 'type', 'requested_at']

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("İzin başlangıç tarihi, bitiş tarihinden önce olmalıdır.")
        return data

    def create(self, validated_data):
        leave = Leave.objects.create(**validated_data)
        return leave


# Bildirim Serializer
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Bildirim ile ilgili kullanıcı bilgileri.

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']


# Kullanıcının Kendi Bilgilerini Güncelleme Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'annual_leave_days']

    def update(self, instance, validated_data):
        # Yıllık izin güncelleniyorsa sadece yetkili güncelleyebilir.
        if 'annual_leave_days' in validated_data and self.context['request'].user.role != 'yetkili':
            raise serializers.ValidationError("Yıllık izin güncelleme yetkiniz yok!")
        return super().update(instance, validated_data)
