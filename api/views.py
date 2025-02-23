from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Producto, ConsultaUsuario  # Importa el modelo de consultas
from .serializers import ProductoSerializer
from django.http import JsonResponse
from collections import Counter
from django.contrib.auth.models import User  # Para manejar usuarios

# Simulación de historial de consultas para recomendaciones
consulta_historial = Counter()
usuario_historial = {}

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
        usuario = request.user if request.user.is_authenticated else None

        if not pregunta:
            return Response({"mensaje": "⚠️ Por favor, ingresa una pregunta válida."}, status=status.HTTP_400_BAD_REQUEST)

        productos_respuesta = []
        productos_disponibles = Producto.objects.all()
        producto_consultado = None

        # 🔍 Buscar productos en la pregunta
        for producto in productos_disponibles:
            if producto.nombre.lower() in pregunta or producto.marca.lower() in pregunta:
                producto_consultado = producto
                break

        # Registrar la consulta en la base de datos con el producto asociado si se encuentra, sino dejarlo como None
        ConsultaUsuario.objects.create(usuario=usuario, consulta=pregunta, producto=producto_consultado)

        # Inicializar historial de usuario
        if usuario not in usuario_historial:
            usuario_historial[usuario] = Counter()

        # 🔍 Detectar qué información se busca en la pregunta
        pregunta_stock = any(kw in pregunta for kw in ["cuántos", "stock", "disponibles"])
        pregunta_precio = any(kw in pregunta for kw in ["precio", "cuánto cuesta", "vale"])
        pregunta_marca = any(kw in pregunta for kw in ["marca", "de qué marca", "qué marca", "de qué marca es"])
        pregunta_lista_productos = any(kw in pregunta for kw in ["qué productos hay", "lista de productos", "todos los productos", "qué productos tienen disponibles"])
        pregunta_total_productos = any(kw in pregunta for kw in ["cuántos productos hay en total", "cuántos productos tienen en total"])
        pregunta_mas_consultados = any(kw in pregunta for kw in ["productos más consultados", "más buscados", "populares"])
        pregunta_productos_stock = any(kw in pregunta for kw in ["qué productos tienen en stock", "productos disponibles"])

        # 📌 Caso especial: Listar todos los productos en la tienda
        if pregunta_lista_productos:
            productos_respuesta = [{"producto": p.nombre, "marca": p.marca} for p in productos_disponibles]
            return Response({"mensaje": "📝 Estos son los productos disponibles en nuestra tienda:", "productos": productos_respuesta}, status=status.HTTP_200_OK)

        # 📌 Caso especial: Contar todos los productos
        if pregunta_total_productos:
            total = productos_disponibles.count()
            return Response({"mensaje": f"Actualmente tenemos {total} productos en nuestra tienda. 🛒"}, status=status.HTTP_200_OK)

        # 📌 Caso especial: Productos más consultados
        if pregunta_mas_consultados:
            recomendaciones = usuario_historial.get(usuario, Counter()).most_common(3)
            recomendaciones_lista = [rec[0] for rec in recomendaciones] if recomendaciones else []
            return Response({"mensaje": "🔥 Estos son los productos más consultados por ti:", "productos_mas_consultados": recomendaciones_lista}, status=status.HTTP_200_OK)

        # 📌 Caso especial: Productos en stock
        if pregunta_productos_stock:
            productos_respuesta = [{"producto": p.nombre, "marca": p.marca, "stock": p.stock} for p in productos_disponibles if p.stock > 0]
            return Response({"mensaje": "📦 Estos productos están en stock:", "productos": productos_respuesta}, status=status.HTTP_200_OK)

        # 📌 Buscar productos en la pregunta
        if producto_consultado:
            usuario_historial[usuario][producto_consultado.nombre] += 1  # Guardar consulta del usuario
            producto_info = {"producto": producto_consultado.nombre}

            if pregunta_stock:
                producto_info["stock"] = producto_consultado.stock
            elif pregunta_precio:
                producto_info["precio"] = f"${producto_consultado.precio:,.2f}"
            elif pregunta_marca:
                producto_info["marca"] = producto_consultado.marca
            else:
                # Si no se especifica qué se quiere saber, se muestra toda la info
                producto_info["marca"] = producto_consultado.marca
                producto_info["stock"] = producto_consultado.stock
                producto_info["precio"] = f"${producto_consultado.precio:,.2f}"

            productos_respuesta.append(producto_info)

        if productos_respuesta:
            # Generar recomendaciones según historial del usuario
            recomendaciones = usuario_historial.get(usuario, Counter()).most_common(3)
            recomendaciones_lista = [rec[0] for rec in recomendaciones]

            return Response({
                "mensaje": "📦 ¡Aquí tienes la información de los productos que encontré para ti!",
                "productos": productos_respuesta,
                "recomendaciones": recomendaciones_lista
            }, status=status.HTTP_200_OK)

        return Response({"mensaje": "😕 No encontré información sobre esos productos en nuestra tienda. ¿Te gustaría preguntar por otro?"}, status=status.HTTP_404_NOT_FOUND)
