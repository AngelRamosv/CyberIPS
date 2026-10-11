# Especificación del Motor de Sincronización (Izzi Auto-Sync Daemon)

## 1. Propósito
Definir de forma explícita el comportamiento, contrato de integración y ciclo de vida del proceso en segundo plano que mantiene sincronizados los nombres de proceso entre el sistema externo de Izzi y el repositorio local de CyberIPS.

---

## 2. Parámetros de Integración
* **Fuente Upstream (Izzi API):** `https://rpabackizzi.azurewebsites.net/Bots/getBots`
* **Método:** `GET`
* **Headers:** `User-Agent: Mozilla/5.0`
* **Frecuencia de Polling:** Cada 30 segundos (`time.sleep(30)`)
* **Modelo de Ejecución:** Daemon thread (`threading.Thread(target=sync_izzi_data, daemon=True)`)

---

## 3. Contrato de Datos Upstream (Entrada)
La API de Izzi entrega una lista de objetos JSON con la siguiente estructura mínima requerida:
```json
[
  {
    "botIp": "192.168.49.29",
    "procesoName": "Ajustes (Sin Validacion) - rpaajustes1"
  }
]
```

---

## 4. Algoritmo de Reconciliación

```
   [Inicio del Ciclo (cada 30s)]
                 │
                 ▼
       GET a Izzi API URL
                 │
      ┌──────────┴──────────┐
      │ ¿Respuesta exitosa? │
      └──────────┬──────────┘
           SÍ    │         NO ──► Registrar error en log y esperar 30s
                 ▼
   Normalizar diccionarios por IP
   (izzi_dict[botIp.strip()] = procesoName.strip())
                 │
                 ▼
       Cargar data.json local
                 │
                 ├────────────────────────────────────────┐
                 ▼                                        ▼
    1. Para cada equipo local:                2. Para cada IP en Izzi:
       ¿Existe su IP en Izzi?                   ¿Existe ya en data.json?
       SÍ: ¿Difiere el proceso 'p'?             NO: Generar nuevo registro:
           SÍ: equipo['p'] = nuevo_proceso          - id = max(id) + 1
               marcar cambios = true                 - m = ip
                                                     - ip = ip
                                                     - p = procesoName
                                                     - o = 'LINUX' (default)
                                                     - u = 'ugenome'
                                                     - pw = 'UbuntuCyb2026$'
                                                    marcar cambios = true
                 │                                        │
                 └───────────────────┬────────────────────┘
                                     │
                           ¿Hubo cambios?
                               SÍ    │    NO ──► Esperar 30s
                                     ▼
                        Sobreescribir data.json
                           con indent=4 (UTF-8)
                                     │
                                     ▼
                                Esperar 30s
```

---

## 5. Tolerancia a Fallos
* **Timeout o Caída de Red:** Las excepciones de red (`URLError`, `HTTPError`, `JSONDecodeError`) se capturan mediante bloques `try/except` sin detener la ejecución del servidor web ni bloquear las peticiones de los usuarios.
* **Persistencia Atómica:** La base de datos local `data.json` solo se sobreescribe cuando la petición a la API externa es exitosa y se ha comprobado la integridad del JSON de respuesta.
