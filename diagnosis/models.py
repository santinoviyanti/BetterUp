from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Model untuk Penyakit
class Penyakit(models.Model):
    nama = models.CharField(max_length=200)  # Nama penyakit

    def __str__(self):
        return self.nama

# Model untuk Gejala yang terkait dengan Penyakit
class Gejala(models.Model):
    penyakit = models.ForeignKey(Penyakit, on_delete=models.CASCADE)  # Penyakit terkait dengan gejala
    nama = models.CharField(max_length=200)  # Nama gejala
    nilai_cf = models.FloatField(default=0)  # Nilai Certainty Factor (CF)

    def clean(self):
        if not (0 <= self.nilai_cf <= 1):
            raise ValidationError('Nilai CF harus antara 0 dan 1.')  # Validasi nilai CF agar berada di antara 0 dan 1

    def __str__(self):
        return f"{self.nama} - Nilai CF: {self.nilai_cf}"

# Model Bobot yang menghubungkan Gejala dengan Penyakit
class Bobot(models.Model):
    penyakit = models.ForeignKey(Penyakit, on_delete=models.CASCADE, related_name='bobot')  # Penyakit yang berhubungan
    gejala = models.ForeignKey(Gejala, on_delete=models.CASCADE, related_name='bobot')  # Gejala yang berhubungan
    bobot = models.FloatField()  # Bobot yang ditentukan untuk hubungan penyakit-gejala

    def __str__(self):
        return f"Bobot untuk {self.gejala.nama} pada {self.penyakit.nama}"

# Model untuk menyimpan Hasil Kuis
class HasilKuis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hasil_kuis', null=True)  # User yang melakukan kuis
    nilai_cf = models.FloatField()  # Nilai CF yang dihitung berdasarkan jawaban kuis
    nama = models.CharField(max_length=100)  # Nama pengguna
    email = models.EmailField()  # Email pengguna
    tanggal = models.DateTimeField(auto_now_add=True)  # Waktu pengisian kuis (tanggal dan waktu)
    penyakit_terdeteksi = models.ForeignKey(Penyakit, null=True, blank=True, on_delete=models.SET_NULL)  # Penyakit yang terdeteksi dari perhitungan CF
    nilai_cf_terdeteksi = models.FloatField(null=True, blank=True)  # Nilai CF yang terdeteksi dari perhitungan CF

    def __str__(self):
        return f"Hasil Kuis untuk {self.nama} pada {self.tanggal} - Penyakit: {self.penyakit_terdeteksi} - CF: {self.nilai_cf_terdeteksi}"

    class Meta:
        # Menjamin bahwa hasil kuis disimpan berdasarkan user dan tanggal
        unique_together = ('user', 'tanggal')  # Menjamin bahwa hasil kuis disimpan berdasarkan user dan tanggal

# Model untuk menyimpan hasil diagnosis penyakit berdasarkan perhitungan CF
class HasilPenyakit(models.Model):
    hasil_kuis = models.ForeignKey(HasilKuis, on_delete=models.CASCADE, related_name='hasil_penyakit')  # Menghubungkan dengan hasil kuis
    penyakit = models.ForeignKey(Penyakit, on_delete=models.CASCADE)  # Penyakit yang terdeteksi
    nilai_cf = models.FloatField()  # Nilai Certainty Factor untuk penyakit yang terdiagnosis

    def __str__(self):
        return f"Penyakit {self.penyakit.nama} - CF: {self.nilai_cf} untuk {self.hasil_kuis.nama}"

    class Meta:
        # Untuk menghindari hasil yang sama disimpan berkali-kali untuk satu hasil kuis
        unique_together = ('hasil_kuis', 'penyakit')
