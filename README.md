# Sistema de órdenes con Docker

## Descripción
Proyecto académico desarrollado con SQL Server 2022, Flask, Django y Docker Compose.

## Arquitectura
- SQL Server 2022: base de datos OrdenesDB.
- Flask: API REST para gestionar órdenes.
- Django: interfaz web.
- Docker Compose: administración de contenedores.
- Volumen persistente para SQL Server.

## Servicios
- Base de datos: puerto 1433.
- API Flask: http://localhost:5000
- Django: http://localhost:8000
- Estado API: http://localhost:5000/health

## Ejecución
1. Configurar el archivo .env usando .env.example.
2. Ejecutar: docker compose up -d --build
3. Verificar: docker compose ps

## Base de datos
Base: OrdenesDB
Tablas: ordenes y orden_detalle.

## Estructura
- api/: aplicación Flask.
- db/: inicialización SQL.
- web/: aplicación Django.
- evidencias/: capturas del proyecto.
- compose.yaml: configuración Docker.

## Autor
Proyecto académico de Ingeniería en Electrónica.

## Integrantes

| Nombre completo | Número de cuenta |
|---|---|
| Ismael Edgardo Funez Contreras | 202010010108 |

Proyecto realizado de manera individual.
