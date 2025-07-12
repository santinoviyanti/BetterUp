from django.contrib import admin
from .models import HasilKuis, HasilPenyakit, Penyakit, Gejala, Bobot

# Jika Anda juga ingin mendaftarkan model lainnya (seperti Penyakit, Gejala, Bobot)
admin.site.register(Penyakit)
admin.site.register(Gejala)
admin.site.register(Bobot)