from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Producto, ConsultaUsuario  # Importa el modelo de consultas
from .serializers import ProductoSerializer
from django.http import JsonResponse
from collections import Counter
from django.contrib.auth.models import User  # Para manejar usuarios


class ProductoListView(APIView):
    def get(self, request):
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

def api_home(request):
    return JsonResponse({"mensaje": "🏢 Bienvenido al ChatBot de Buy n Large. Pregunta por el stock, precio o marca de un producto."})


class ChatBotView(APIView):

    def get(self, request):
        return Response({"mensaje": "👋 Bienvenido al ChatBot. Pregunta por el stock, precio o marca de un producto."}, status=status.HTTP_200_OK)

    def post(self, request):
        pregunta = request.data.get("pregunta", "").lower()

        if not pregunta:
            return Response({"mensaje": "⚠️ Por favor, ingresa una pregunta válida."}, status=status.HTTP_400_BAD_REQUEST)

        productos_respuesta = []
        productos_disponibles = Producto.objects.all()
        productos_filtrados = [p for p in productos_disponibles if p.nombre.lower() in pregunta or p.marca.lower() in pregunta]

        pregunta_stock = any(kw in pregunta for kw in ["cuántos", "stock", "disponibles"])
        pregunta_precio = any(kw in pregunta for kw in ["precio", "cuánto cuesta", "vale"])
        pregunta_marca = any(kw in pregunta for kw in ["marca", "de qué marca", "qué marca", "de qué marca es"])
        pregunta_lista_productos = any(kw in pregunta for kw in ["qué productos hay", "lista de productos", "todos los productos", "qué productos tienen disponibles"])
        pregunta_total_productos = any(kw in pregunta for kw in ["cuántos productos hay en total", "cuántos productos tienen en total", "cuántos productos hay", "cuántos productos tienen en stock", "cuántos productos están disponibles"])
        pregunta_marcas_productos = "qué marca" in pregunta or "qué marcas" in pregunta

        if pregunta_lista_productos:
            productos_respuesta = [{"producto": p.nombre, "marca": p.marca} for p in productos_disponibles]
            return Response({"mensaje": "📝 Estos son los productos disponibles en nuestra tienda:", "productos": productos_respuesta}, status=status.HTTP_200_OK)

        if pregunta_total_productos:
            total_stock = Producto.objects.filter(stock__gt=0).count()
            return Response({"mensaje": f"📦 Actualmente hay {total_stock} productos en stock en nuestra tienda."}, status=status.HTTP_200_OK)

        if pregunta_marcas_productos:
            palabras = pregunta.split()
            producto_tipo = next((palabra for palabra in palabras if Producto.objects.filter(nombre__icontains=palabra).exists()), None)
            
            if producto_tipo:
                marcas_disponibles = Producto.objects.filter(nombre__icontains=producto_tipo).values_list("marca", flat=True).distinct()
                return Response({
                    "mensaje": f"🏷️ Estas son las marcas disponibles para {producto_tipo}s:",
                    "marcas": list(marcas_disponibles)
                }, status=status.HTTP_200_OK)

        if productos_filtrados:
            for producto in productos_filtrados:
                if all(word in pregunta for word in producto.nombre.lower().split() + producto.marca.lower().split()):
                    producto_info = {"producto": producto.nombre}
                    if pregunta_stock:
                        producto_info["stock"] = producto.stock
                    if pregunta_precio:
                        producto_info["precio"] = f"${producto.precio:,.2f}"
                    if pregunta_marca:
                        producto_info["marca"] = producto.marca
                    productos_respuesta.append(producto_info)

        if productos_respuesta:
            return Response({
                "mensaje": "📦 ¡Aquí tienes la información de los productos que encontré para ti!",
                "productos": productos_respuesta
            }, status=status.HTTP_200_OK)

        return Response({"mensaje": "😕 No encontré información sobre esos productos en nuestra tienda. ¿Te gustaría preguntar por otro?"}, status=status.HTTP_404_NOT_FOUND)
