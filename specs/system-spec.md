# Especificación de Arquitectura de Sistema (Spec-Driven Development)

## 1. Visión General del Proyecto
**CyberIPS** es un panel de supervisión y gestión de infraestructura de máquinas virtuales (VMs) y bots de automatización RPA en red interna, diseñado para operar tanto de forma centralizada como distribuida entre equipos de ingeniería.

---

## 2. Principios de Arquitectura SDD (Spec-Driven Development)
1. **Especificaciones como Fuente Única de Verdad (SSOT):**  
   Cualquier nuevo campo, endpoint o comportamiento debe definirse primero en la carpeta `specs/` (`openapi.yaml`, `equipment.schema.json`, `sync-engine.spec.md`).
2. **Cero Dependencias Pesadas de Ejecución:**  
   El backend se ejecuta sobre la librería estándar de Python (`http.server`, `urllib.request`, `threading`), garantizando portabilidad instantánea en cualquier entorno Windows o Linux sin necesidad de `npm install` ni entornos virtuales pesados.
3. **Persistencia Basada en Documentos (`data.json`):**  
   Almacenamiento directo y legible en formato JSON para facilitar versionamiento en Git y control de auditoría de infraestructura.

---

## 3. Topología de Componentes

```
┌────────────────────────────────────────────────────────┐
│                   Navegador Web (Cliente)             │
│  - index.html (Vanilla JS, CSS Variables, Responsive)  │
│  - Filtros en tiempo real por SO y Proceso             │
│  - Edición en línea, Importador CSV & Exportador Excel │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP (GET/POST /api/data)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Servidor Local (server.py)                 │
│  - Puerto: 8765                                        │
│  - Rutas: GET / | GET /api/data | POST /api/data      │
│  - Servidor de archivos estáticos y CORS               │
└─────────────┬────────────────────────────┬─────────────┘
              │ Lectura/Escritura          │ Consulta periódica (cada 30s)
              ▼                            ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   Base de Datos Local    │  │    API Externa de Izzi   │
│       data.json          │  │   (Azure RPA Backend)    │
└──────────────────────────┘  └──────────────────────────┘
```

---

## 4. Requisitos No Funcionales
* **Disponibilidad en Red Local (LAN):** Expuesto para acceso departamental vía `http://<IP_LOCAL>:8765/`.
* **Concurrencia:** Hilo dedicado (daemon) para reconciliación externa que no bloquea la atención de peticiones web concurrentes.
* **Compatibilidad de Plataforma:** Launcher por lotes `.bat` para operadores Windows y soporte directo POSIX para servidores Linux.
