from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import timedelta


# Kullanıcı modeli (Personel ve Yetkili)
class User(AbstractUser):
    role = models.CharField(max_length=50, choices=[('personel', 'Personel'), ('yetkili', 'Yetkili')])
    annual_leave_days = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    date_joined = models.DateField(auto_now_add=True)
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Burada farklı bir isim kullanıyoruz.
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # Burada da farklı bir isim kullanıyoruz.
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username


# Giriş/Çıkış kayıt modeli
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    late_minutes = models.PositiveIntegerField(default=0)

    def calculate_late_minutes(self, work_start_time="08:00:00"):
        from datetime import datetime
        if self.check_in_time:
            fmt = "%H:%M:%S"
            check_in = datetime.strptime(str(self.check_in_time), fmt)
            work_start = datetime.strptime(work_start_time, fmt)
            if check_in > work_start:
                self.late_minutes = (check_in - work_start).seconds // 60
                self.save()

    def __str__(self):
        return f"{self.user.username} - {self.date}"


# İzin modeli
class Leave(models.Model):
    LEAVE_STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    )
    LEAVE_TYPE_CHOICES = (
        ('annual', 'Yıllık İzin'),
        ('special', 'Özel İzin'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=LEAVE_STATUS_CHOICES, default='pending')
    type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES, default='annual')
    requested_at = models.DateTimeField(auto_now_add=True)

    def leave_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.user.username} - {self.type} ({self.start_date} - {self.end_date})"


# Bildirim modeli
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bildirim ({self.user.username}) - {'Okundu' if self.is_read else 'Okunmadı'}"
