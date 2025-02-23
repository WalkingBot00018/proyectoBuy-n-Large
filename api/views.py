from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Producto  # Importa el modelo correctamente
from .serializers import ProductoSerializer
from django.http import JsonResponse
from collections import Counter

# Simulación de historial de consultas para recomendaciones
consulta_historial = Counter()

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

        # Detectar qué información se busca en la pregunta
        pregunta_stock = any(kw in pregunta for kw in ["cuántos", "stock", "disponibles"])
        pregunta_precio = any(kw in pregunta for kw in ["precio", "cuánto cuesta", "vale"])
        pregunta_marca = any(kw in pregunta for kw in ["marca", "de qué marca", "qué marca", "de qué marca es"])
        pregunta_lista_productos = any(kw in pregunta for kw in ["qué productos hay", "lista de productos", "todos los productos", "qué productos tienen disponibles"])
        pregunta_total_productos = any(kw in pregunta for kw in ["cuántos productos hay en total", "cuántos productos tienen en total"])
        pregunta_mas_consultados = any(kw in pregunta for kw in ["productos más consultados", "más buscados", "populares"])
        pregunta_productos_stock = any(kw in pregunta for kw in ["qué productos tienen en stock", "productos disponibles"])

        # Caso especial: Listar todos los productos en la tienda
        if pregunta_lista_productos:
            productos_respuesta = [{"producto": p.nombre, "marca": p.marca} for p in productos_disponibles]
            if productos_respuesta:
                return Response({"mensaje": "📝 Estos son los productos disponibles en nuestra tienda:", "productos": productos_respuesta}, status=status.HTTP_200_OK)
            else:
                return Response({"mensaje": "😕 No hay productos disponibles en este momento."}, status=status.HTTP_404_NOT_FOUND)

        # Caso especial: Contar todos los productos
        if pregunta_total_productos:
            total = productos_disponibles.count()
            return Response({"mensaje": f"Actualmente tenemos {total} productos en nuestra tienda. 🛒"}, status=status.HTTP_200_OK)

        # Caso especial: Productos más consultados
        if pregunta_mas_consultados:
            if consulta_historial:
                recomendaciones = consulta_historial.most_common(3)  # Top 3 productos más consultados
                recomendaciones_lista = [rec[0] for rec in recomendaciones]
            else:
                # Si no hay datos en el historial, recomendar productos disponibles
                recomendaciones_lista = [f"{p.nombre} ({p.marca})" for p in productos_disponibles[:3]]

            return Response({
                "mensaje": "🔥 Estos son los productos más consultados por nuestros clientes:",
                "productos_mas_consultados": recomendaciones_lista
            }, status=status.HTTP_200_OK)

        # Caso especial: Productos en stock
        if pregunta_productos_stock:
            productos_respuesta = [{"producto": p.nombre, "marca": p.marca, "stock": p.stock} for p in productos_disponibles if p.stock > 0]
            if productos_respuesta:
                return Response({"mensaje": "📦 Estos productos están en stock:", "productos": productos_respuesta}, status=status.HTTP_200_OK)
            else:
                return Response({"mensaje": "😕 No hay productos en stock actualmente."}, status=status.HTTP_404_NOT_FOUND)

        # Diccionario de sinónimos de productos
        sinonimos_productos = {
            "computador": ["computadora", "pc", "laptop"],
            "teclado": ["keyboard"],
            "monitor": ["pantalla", "display"],
            "mouse": ["ratón"],
            "impresora": ["printer"],
            "televisor": ["tv", "pantalla", "smart tv"],
            "nevera": ["refrigerador", "frigorífico"],
            "celular": ["móvil", "smartphone", "teléfono"],
            "tablet": ["tableta", "ipad"],
            "consola": ["playstation", "xbox", "nintendo"]
        }

        # Buscar productos en la pregunta
        for producto in productos_disponibles:
            nombres_posibles = [producto.nombre.lower(), producto.marca.lower()]
            for key, values in sinonimos_productos.items():
                if producto.nombre.lower() in values or producto.nombre.lower() == key:
                    nombres_posibles.extend(values)
                    nombres_posibles.append(key)

            if any(nombre in pregunta for nombre in nombres_posibles):
                producto_info = {"producto": producto.nombre, "marca": producto.marca}
                consulta_historial[f"{producto.nombre} ({producto.marca})"] += 1  # Registrar consulta

                if pregunta_stock:
                    producto_info = {"producto": producto.nombre, "stock": producto.stock}
                elif pregunta_precio:
                    producto_info = {"producto": producto.nombre, "precio": f"${producto.precio:,.2f}"}
                elif pregunta_marca:
                    producto_info = {"producto": producto.nombre, "marca": producto.marca}
                
                productos_respuesta.append(producto_info)

        if productos_respuesta:
            return Response({"mensaje": "📦 ¡Aquí tienes la información de los productos que encontré para ti!", "productos": productos_respuesta}, status=status.HTTP_200_OK)

        return Response({"mensaje": "😕 No encontré información sobre esos productos en nuestra tienda. ¿Te gustaría preguntar por otro?"}, status=status.HTTP_404_NOT_FOUND)
