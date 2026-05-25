# Monitor de Red EXELIA

Sistema de monitoreo de red por ubicaciones para infraestructura de EXELIA Logística Integral.

## Características

- ✅ Monitoreo automático por ubicaciones (WEC AICM, WEC AIFA, CORPORATIVO, WEC LOGISTICA)
- ✅ Ping paralelo a todos los dispositivos
- ✅ Gestión de dispositivos (Switches, Servidores, Impresoras, Cámaras)
- ✅ Gestión de enlaces de internet (ISPs)
- ✅ Alertas sonoras para cambios de estado
- ✅ Notificaciones toast en pantalla
- ✅ Exportación de logs
- ✅ Configuración persistente en JSON
- ✅ Interfaz gráfica moderna con CustomTkinter

## Requisitos

- Python 3.8+
- CustomTkinter
- Windows/Linux/macOS

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/TuUsuario/monitor-red-exelia.git
cd monitor-red-exelia

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python monitor_red.py
```

## Uso

1. **Agregar dispositivos:** Click en "➕ Agregar Dispositivo" en cada pestaña de ubicación
2. **Agregar enlaces:** Click en "➕ Agregar Enlace" en la pestaña Enlaces Internet
3. **Monitoreo manual:** Click en "🔄 PROBAR AHORA"
4. **Monitoreo automático:** Click en "▶ INICIAR MONITOREO"
5. **Configurar intervalo:** Ajustar segundos entre revisiones

## Estructura de Archivos

```
monitor-red-exelia/
├── monitor_red.py              # Aplicación principal
├── config_dispositivos.json    # Configuración (auto-generado)
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
├── .gitignore                  # Archivos ignorados por Git
└── LICENSE                     # Licencia MIT
```

## Configuración

El archivo `config_dispositivos.json` se genera automáticamente y almacena:

- Dispositivos por ubicación
- Enlaces de internet
- Estados y timestamps

## Capturas

```
📊 Estadísticas en tiempo real
✅ Interfaz por pestañas
🔔 Log de eventos
⚡ Ping paralelo rápido
```

## Autor

**Gustavo Bermúdez Sotel**  
IT Systems & Security Analyst  
CUALQUIER CORPORATIVO POR RED Y TENANTS DESCENTES
📧 gbermudez@exelia.com.mx (EN DESHUSO)

## Licencia

MIT License - Ver archivo LICENSE para detalles

## Versión

**v1.0.0** - Versión estable inicial
