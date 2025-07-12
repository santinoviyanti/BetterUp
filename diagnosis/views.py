from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .forms import CustomUserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse
from .models import HasilKuis, Gejala, Bobot, Penyakit, HasilPenyakit  # Pastikan HasilPenyakit diimport
from django.contrib.auth.models import Group
from django.contrib.auth import logout


# Home view (beranda)
def home(request):
    return render(request, 'home.html')  # Pastikan home.html ada di folder templates

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Mengambil email dan password dari form
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Autentikasi user menggunakan backend custom
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)  # Login user
                
                # Cek apakah user adalah admin
                if user.is_superuser:
                    return redirect('/admin/')  # Jika admin, arahkan ke halaman admin
                else:
                    return redirect('home')  # Jika bukan admin, arahkan ke halaman home
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid login credentials'})
    else:
        form = AuthenticationForm()

    # Render halaman login jika method GET atau form invalid
    return render(request, 'login.html', {'form': form})

# Register view
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            # Cek jika email sudah terdaftar
            if get_user_model().objects.filter(email=email).exists():
                return render(request, 'register.html', {'form': form, 'error': 'Email sudah digunakan'})

            user = form.save()  # Simpan pengguna baru
            login(request, user)  # Otomatis login setelah registrasi
            return redirect('home')  # Redirect ke halaman home setelah registrasi
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


# Forgot password view
def forgot_password_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                token_generator=default_token_generator,
                email_template_name="registration/password_reset_email.html",
                subject_template_name="registration/password_reset_subject.txt",
            )
            return render(request, "registration/password_reset_done.html")
    else:
        form = PasswordResetForm()

    return render(request, "registration/password_reset_form.html", {"form": form})


# Reset password view
def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')  # Redirect ke login setelah reset password
        else:
            form = SetPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        return redirect('password_reset_invalid')  # Redirect ke halaman error jika link tidak valid


# Diagnosa view (halaman kuis) - Tidak memerlukan login
def diagnosa_view(request):
    return render(request, 'diagnosa.html')


# Submit kuis view (proses jawaban)
def submit_quiz(request):
    if request.method == 'POST':
        # Ambil jawaban dari form (anggap ada 20 pertanyaan)
        answers = [request.POST.get(f'question{i}') for i in range(1, 21)]  

        # Ambil Gejala dan Bobot terkait dari database
        gejalas = Gejala.objects.all()
        gejala_cf_values = []
        
        for i, answer in enumerate(answers):
            if answer == '1':  # Jika jawaban "Ya"
                gejala = gejalas[i]
                bobot = Bobot.objects.filter(gejala=gejala).first()  # Ambil Bobot terkait
                if bobot:
                    gejala_cf_values.append((gejala.penyakit, bobot.bobot))  # Simpan CF untuk penyakit terkait

        # Hitung CF untuk setiap Penyakit berdasarkan gejala yang dipilih
        penyakit_cf_map = {}
        for penyakit, bobot in gejala_cf_values:
            penyakit_id = penyakit.id
            if penyakit_id not in penyakit_cf_map:
                penyakit_cf_map[penyakit_id] = 0.0  # Inisialisasi CF penyakit

            # Formula kombinasi CF: CF_combined = 1 - (1 - CF_1) * (1 - CF_2) ...
            penyakit_cf_map[penyakit_id] = 1 - (1 - penyakit_cf_map[penyakit_id]) * (1 - bobot)

        # Cari penyakit dengan CF tertinggi
        max_penyakit_id = max(penyakit_cf_map, key=penyakit_cf_map.get)
        max_cf_value = penyakit_cf_map[max_penyakit_id]

        # Ambil objek Penyakit dengan ID terkait
        detected_penyakit = Penyakit.objects.get(id=max_penyakit_id)

        # Jika pengguna sudah login, simpan hasilnya
        hasil_kuis = HasilKuis(
            user=request.user if request.user.is_authenticated else None,
            nama=request.user.username if request.user.is_authenticated else "Guest",
            email=request.user.email if request.user.is_authenticated else "guest@example.com",
            nilai_cf=max_cf_value,
            penyakit_terdeteksi=detected_penyakit,
            nilai_cf_terdeteksi=max_cf_value
        )
        hasil_kuis.save()

        # Redirect ke halaman 'riwayat' untuk menampilkan hasil
        return redirect('riwayat')

    return redirect('diagnosa')  # Redirect ke halaman diagnosa jika bukan POST


# Riwayat view (tampilkan hasil kuis) - Tidak memerlukan login
def riwayat_view(request):
    hasil_kuis = HasilKuis.objects.all()  # Ambil semua hasil kuis

    return render(request, 'riwayat_template.html', {'hasil_kuis': hasil_kuis})

def cetak_hasil(request, hasil_kuis_id):
    try:
        # Ambil data hasil kuis berdasarkan ID
        hasil_kuis = HasilKuis.objects.get(id=hasil_kuis_id)

        # Menyusun response berisi detail hasil kuis
        response_content = f"Result: Penyakit: {hasil_kuis.penyakit_terdeteksi.nama} - CF: {hasil_kuis.nilai_cf_terdeteksi}"

        # Mengembalikan HttpResponse dengan konten hasil kuis
        return HttpResponse(response_content)

    except HasilKuis.DoesNotExist:
        # Jika data hasil kuis tidak ditemukan, tampilkan pesan error
        return HttpResponse("Result not found", status=404)

# Logout view
def custom_logout(request):
    logout(request)
    return redirect('home')  # Redirect ke home setelah logout
