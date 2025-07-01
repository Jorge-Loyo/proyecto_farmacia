from django.db import models

class Laboratorio(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre

class Monodroga(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre

class Medicamento(models.Model):
    id_alfabeta = models.IntegerField(primary_key=True)
    nombre_comercial = models.CharField(max_length=255)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    monodroga = models.ForeignKey(Monodroga, on_delete=models.CASCADE) # <-- ¡LA LÍNEA QUE FALTABA!
    precio_caja = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.nombre_comercial

class Equivalencia(models.Model):
    medicamento_alfabeta = models.OneToOneField(Medicamento, on_delete=models.CASCADE, primary_key=True)
    # Aquí puedes añadir los otros códigos en el futuro

class RegistroCarga(models.Model):
    fuente = models.CharField(max_length=50, unique=True)
    fecha_carga = models.DateTimeField()
    def __str__(self):
        return f"Última carga de {self.fuente}"