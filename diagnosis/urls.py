from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # URL untuk halaman home
    path('login/', views.login_view, name='login'),  # Login menggunakan custom view
    path('register/', views.register_view, name='register'),  # Registrasi
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),  # Lupa password
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),  # Reset password
    path('diagnosa/', views.diagnosa_view, name='diagnosa'),  # Halaman diagnosa
    path('submit_quiz/', views.submit_quiz, name='submit_quiz'),  # Kirim kuis
    path('riwayat/', views.riwayat_view, name='riwayat'),  # Riwayat hasil kuis
    path('cetak_hasil/<int:hasil_kuis_id>/', views.cetak_hasil, name='cetak_hasil'),  # Cetak hasil kuis
    path('logout/', views.custom_logout, name='logout'),  # Logout
]
