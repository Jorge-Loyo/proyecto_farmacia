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
    ESTADO_HABILITADO = 0
    ESTADO_DESCONTINUADO = 1
    ESTADO_CHOICES = [
        (ESTADO_HABILITADO, 'Habilitado'),
        (ESTADO_DESCONTINUADO, 'Descontinuado'),
    ]

    id_alfabeta = models.IntegerField(primary_key=True)
    nombre_comercial = models.CharField(max_length=255)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    monodroga = models.ForeignKey(Monodroga, on_delete=models.CASCADE)
    precio_caja = models.DecimalField(max_digits=16, decimal_places=2)

    # CAMBIO: Hacemos que este campo no sea editable y se calcule solo
    from decimal import Decimal
    precio_unitario = models.DecimalField(max_digits=16, decimal_places=2, editable=False, default=Decimal('0.00'))

    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_HABILITADO)
    cantidad = models.IntegerField(null=True, blank=True, help_text="Unidades por caja")
    

    def __str__(self):
        return self.nombre_comercial
    def save(self, *args, **kwargs):
        # Si hay precio y la cantidad es mayor a cero, calcula el precio unitario
        if self.precio_caja and self.cantidad and self.cantidad > 0:
            self.precio_unitario = self.precio_caja / self.cantidad
        else:
            self.precio_unitario = self.precio_caja # Si no hay cantidad, el unitario es igual al de la caja
        super().save(*args, **kwargs) # Llama al método de guardado original

class Equivalencia(models.Model):
    medicamento_alfabeta = models.OneToOneField(Medicamento, on_delete=models.CASCADE, primary_key=True)
    # Aquí puedes añadir los otros códigos en el futuro

class RegistroCarga(models.Model):
    fuente = models.CharField(max_length=50, unique=True)
    fecha_carga = models.DateTimeField()
    def __str__(self):
        return f"Última carga de {self.fuente}"
    

class HistorialPrecio(models.Model):
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, related_name='historial_precios')
    precio_caja = models.DecimalField(max_digits=16, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=16, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicamento.nombre_comercial} - ${self.precio_caja} ({self.fecha_registro.strftime('%d/%m/%Y')})"