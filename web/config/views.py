
import requests
from django.shortcuts import render, redirect

API_URL = "http://api:5000/api/ordenes"

def listar_ordenes(request):
    mensaje = None
    error = None

    if request.method == "POST":
        datos = {
            "cliente": request.POST.get("cliente"),
            "estado": request.POST.get("estado"),
            "total": request.POST.get("total")
        }

        try:
            respuesta = requests.post(
                API_URL,
                json=datos,
                timeout=10
            )
            respuesta.raise_for_status()
            return redirect("listar_ordenes")

        except requests.RequestException as e:
            error = str(e)

    try:
        respuesta = requests.get(API_URL, timeout=10)
        respuesta.raise_for_status()
        ordenes = respuesta.json()

    except requests.RequestException as e:
        ordenes = []
        error = str(e)

    return render(request, "ordenes.html", {
        "ordenes": ordenes,
        "error": error
    })


def eliminar_orden(request, order_id):
    if request.method == "POST":
        try:
            respuesta = requests.delete(
                f"{API_URL}/{order_id}",
                timeout=10
            )
            respuesta.raise_for_status()
        except requests.RequestException as e:
            return render(request, "ordenes.html", {
                "ordenes": [],
                "error": str(e)
            })

    return redirect("listar_ordenes")