from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    marca = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nombre} - {self.marca} ({self.stock} disponibles)"

class ConsultaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    consulta = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)  # Permitir valores nulos

    def __str__(self):
        return f"{self.usuario} - {self.consulta} ({self.fecha})"
