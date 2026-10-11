# 🖥️ CyberIPS — Panel de Infraestructura y Gestión de Bots

Sistema de gestión y supervisión en tiempo real para máquinas virtuales (VMs) y bots de automatización RPA en red interna, con sincronización automática de procesos desde la API de Izzi.

---

## 🏗️ Arquitectura Spec-Driven Development (SDD)

Este proyecto está construido bajo el estándar **Spec-Driven Development**. Todas las interfaces, modelos de datos y motores de sincronización están formalmente definidos y versionados en el directorio [`specs/`](./specs):

| Especificación | Archivo | Descripción |
| :--- | :--- | :--- |
| **API Contract** | [`specs/openapi.yaml`](./specs/openapi.yaml) | Especificación OpenAPI 3.0 de los endpoints REST del backend. |
| **Data Schema** | [`specs/equipment.schema.json`](./specs/equipment.schema.json) | JSON Schema (Draft-07) que valida la estructura de `data.json`. |
| **Sync Engine** | [`specs/sync-engine.spec.md`](./specs/sync-engine.spec.md) | Especificación formal del hilo de sincronización con la API de Izzi. |
| **System Spec** | [`specs/system-spec.md`](./specs/system-spec.md) | Arquitectura del sistema, topología de componentes y flujo de datos. |

---

## 📁 Estructura del Proyecto

```text
CyberIPS/
├── docs/                      # Manuales operativos y guías técnicas
│   └── manual_comandos_rpa.pdf
├── specs/                     # Contratos y especificaciones del sistema (SDD)
│   ├── openapi.yaml           # Contrato OpenAPI 3.0
│   ├── equipment.schema.json  # Esquema de validación JSON
│   ├── sync-engine.spec.md    # Especificación del daemon de sincronización
│   └── system-spec.md         # Especificación del sistema y arquitectura
├── data.json                  # Catálogo de máquinas y procesos persistidos
├── index.html                 # Dashboard web (interfaz de usuario)
├── Iniciar_Servidor.bat       # Acceso directo para iniciar el servidor en Windows
├── server.py                  # Servidor HTTP Python y motor de sincronización Izzi
├── .gitignore                 # Reglas de exclusión de Git
└── README.md                  # Documentación del proyecto
```

---

## 🚀 Inicio Rápido

### En Windows (Recomendado):
Haz doble clic en el archivo **`Iniciar_Servidor.bat`**.

### Desde Terminal / Línea de Comandos:
```bash
python server.py
```

El servidor responderá en el puerto **`8765`**:
* **Acceso local:** `http://localhost:8765/`
* **Acceso en red local (LAN):** `http://<TU_IP_LOCAL>:8765/`

---

## 🔄 Sincronización Automática con Izzi

El backend (`server.py`) incluye un hilo daemon en segundo plano que consulta periódicamente la API de Izzi (`https://rpabackizzi.azurewebsites.net/Bots/getBots`):
1. **Actualización de procesos:** Actualiza en tiempo real los nombres de los procesos de las IPs existentes.
2. **Auto-registro:** Registra automáticamente cualquier IP nueva que aparezca en el panel de Izzi sin requerir intervención manual.
