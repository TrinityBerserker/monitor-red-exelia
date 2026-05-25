#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Red - Sistema de monitoreo por ubicaciones
Versión: 1.0.0
Autor: Gustavo Bermúdez Sotel
Empresa: EXELIA Logística Integral
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import threading
import time
import platform
import subprocess
from datetime import datetime
from pathlib import Path

# Configuración de tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ToastNotification:
    """Notificación tipo toast"""
    def __init__(self, parent, mensaje, tipo="info", duracion=3000):
        self.parent = parent
        self.tipo = tipo
        
        # Colores según tipo
        colores = {
            "error": ("#e53935", "#ffcdd2"),
            "success": ("#43a047", "#c8e6c9"),
            "warning": ("#FF8C00", "#ffe0b2"),
            "info": ("#FF8C00", "#ffe0b2")
        }
        bg_color, text_color = colores.get(tipo, colores["info"])
        
        # Crear ventana toast
        self.toast = ctk.CTkToplevel(parent)
        self.toast.withdraw()
        self.toast.overrideredirect(True)
        self.toast.attributes('-topmost', True)
        
        # Frame principal
        frame = ctk.CTkFrame(
            self.toast,
            fg_color=bg_color,
            corner_radius=15,
            border_width=2,
            border_color=bg_color
        )
        frame.pack(padx=0, pady=0, fill="both", expand=True)
        
        # Icono según tipo
        iconos = {
            "error": "❌",
            "success": "✅",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icono = iconos.get(tipo, "ℹ️")
        
        # Contenido
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=15)
        
        ctk.CTkLabel(
            content_frame,
            text=f"{icono} {mensaje}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white" if tipo in ["error", "success"] else "black",
            wraplength=300
        ).pack()
        
        # Posicionar en esquina inferior derecha
        self.toast.update_idletasks()
        width = self.toast.winfo_reqwidth()
        height = self.toast.winfo_reqheight()
        
        screen_width = self.toast.winfo_screenwidth()
        screen_height = self.toast.winfo_screenheight()
        
        x = screen_width - width - 20
        y = screen_height - height - 80
        
        self.toast.geometry(f"+{x}+{y}")
        
        # Mostrar con animación
        self.mostrar_animado(duracion)
    
    def mostrar_animado(self, duracion):
        """Muestra el toast con animación de fade in"""
        self.toast.deiconify()
        self.toast.attributes('-alpha', 0.0)
        
        # Fade in
        for i in range(10):
            alpha = i / 10
            self.toast.attributes('-alpha', alpha)
            self.toast.update()
            time.sleep(0.03)
        
        # Esperar
        self.toast.after(duracion, self.ocultar_animado)
    
    def ocultar_animado(self):
        """Oculta el toast con animación de fade out"""
        # Fade out
        for i in range(10, -1, -1):
            alpha = i / 10
            try:
                self.toast.attributes('-alpha', alpha)
                self.toast.update()
                time.sleep(0.03)
            except:
                break
        
        try:
            self.toast.destroy()
        except:
            pass


class MonitorRed:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Red - EXELIA")
        self.root.geometry("1400x850")
        
        # Variables
        self.monitoreando = False
        self.config_file = "config_dispositivos.json"
        self.intervalo = ctk.IntVar(value=60)
        self.estados_previos = {}
        
        # Colores personalizados
        self.colors = {
            'primary': '#FFB800',
            'success': '#43a047',
            'danger': '#e53935',
            'warning': '#FFB800',
            'dark': '#1a1a1a',
            'card_bg': '#2b2b2b',
            'hover': '#3a3a3a'
        }
        
        # Ubicaciones
        self.ubicaciones = ["WEC AICM", "WEC AIFA", "CORPORATIVO", "WEC LOGISTICA"]
        
        # Tipos de dispositivos
        self.tipos_dispositivos = ["Switch", "Servidor", "Impresora", "Cámara", "Otro"]
        
        # Cargar configuración
        self.dispositivos = self.cargar_config()
        self.inicializar_estados_previos()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Bind para cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.al_cerrar)
    
    def inicializar_estados_previos(self):
        """Inicializa el diccionario de estados previos"""
        for ubicacion in self.dispositivos.get('ubicaciones', {}):
            for disp in self.dispositivos['ubicaciones'][ubicacion]:
                key = f"{disp['ip']}_{disp['nombre']}"
                self.estados_previos[key] = disp.get('estado', 'Desconocido')
        
        for enlace in self.dispositivos.get('enlaces_internet', []):
            key = f"{enlace['ip']}_{enlace['nombre']}"
            self.estados_previos[key] = enlace.get('estado', 'Desconocido')
    
    def crear_interfaz(self):
        """Crea la interfaz"""
        # Header
        header_frame = ctk.CTkFrame(self.root, fg_color=self.colors['primary'], height=100)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="🌐 Monitor de Red EXELIA",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="Sistema de Monitoreo por Ubicaciones",
            font=ctk.CTkFont(size=14),
            text_color="white"
        ).pack(side="left", padx=(0, 30), pady=20)
        
        # Panel de control
        control_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=15)
        
        buttons_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        buttons_frame.pack(side="left", fill="x", expand=True)
        
        self.btn_iniciar = ctk.CTkButton(
            buttons_frame,
            text="▶ INICIAR MONITOREO",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.iniciar_monitoreo,
            width=200,
            height=45,
            fg_color=self.colors['success'],
            hover_color="#388e3c",
            corner_radius=10
        )
        self.btn_iniciar.pack(side="left", padx=5)
        
        self.btn_detener = ctk.CTkButton(
            buttons_frame,
            text="⏹ DETENER",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.detener_monitoreo,
            width=160,
            height=45,
            fg_color=self.colors['danger'],
            hover_color="#c62828",
            state="disabled",
            corner_radius=10
        )
        self.btn_detener.pack(side="left", padx=5)
        
        self.btn_probar = ctk.CTkButton(
            buttons_frame,
            text="🔄 PROBAR AHORA",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.probar_una_vez,
            width=180,
            height=45,
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color="#E6A500"
        )
        self.btn_probar.pack(side="left", padx=5)
        
        # Intervalo
        interval_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        interval_frame.pack(side="right", padx=10)
        
        ctk.CTkLabel(
            interval_frame,
            text="Intervalo (seg):",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=5)
        
        self.entry_intervalo = ctk.CTkEntry(
            interval_frame,
            textvariable=self.intervalo,
            width=80,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.entry_intervalo.pack(side="left", padx=5)
        
        # Estadísticas
        stats_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.card_total = self.crear_stat_card(stats_frame, "📊 Total", "0", self.colors['primary'])
        self.card_online = self.crear_stat_card(stats_frame, "✅ En Línea", "0", self.colors['success'])
        self.card_offline = self.crear_stat_card(stats_frame, "❌ Caídos", "0", self.colors['danger'])
        
        self.lbl_estado = ctk.CTkLabel(
            stats_frame,
            text="⚪ DETENIDO",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="gray"
        )
        self.lbl_estado.pack(side="right", padx=20)
        
        # Tabview
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tabview = ctk.CTkTabview(main_container, corner_radius=15)
        self.tabview.pack(fill="both", expand=True)
        
        self.tabs = {}
        
        for ubicacion in self.ubicaciones:
            tab = self.tabview.add(f"📍 {ubicacion}")
            self.crear_tab_ubicacion(tab, ubicacion)
            self.tabs[ubicacion] = tab
        
        self.tab_enlaces = self.tabview.add("🌐 Enlaces Internet")
        self.crear_tab_enlaces()
        
        self.tab_log = self.tabview.add("📋 Log")
        self.crear_tab_log()
        
        self.tabview.set(f"📍 {self.ubicaciones[0]}")
    
    def crear_stat_card(self, parent, titulo, valor, color):
        card = ctk.CTkFrame(parent, fg_color=self.colors['card_bg'], corner_radius=15)
        card.pack(side="left", padx=10, fill="x", expand=True)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(padx=20, pady=15)
        
        ctk.CTkLabel(
            content_frame,
            text=titulo,
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).pack()
        
        valor_label = ctk.CTkLabel(
            content_frame,
            text=valor,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=color
        )
        valor_label.pack()
        
        return valor_label
    
    def crear_tab_ubicacion(self, tab, ubicacion):
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(
            btn_frame,
            text="➕ Agregar Dispositivo",
            command=lambda: self.agregar_dispositivo_ubicacion(ubicacion),
            width=180,
            height=35,
            corner_radius=8,
            fg_color=self.colors['success'],
            hover_color="#388e3c"
        ).pack(side="left", padx=5)
        
        table_frame = ctk.CTkScrollableFrame(
            container,
            fg_color=self.colors['card_bg'],
            corner_radius=15
        )
        table_frame.pack(fill="both", expand=True)
        
        header = ctk.CTkFrame(table_frame, fg_color=self.colors['primary'], corner_radius=10)
        header.pack(fill="x", padx=5, pady=(5, 10))
        
        headers = [("Tipo", 0.15), ("IP", 0.2), ("Nombre", 0.3), ("Estado", 0.15), ("Última Rev.", 0.15)]
        for texto, peso in headers:
            ctk.CTkLabel(
                header,
                text=texto,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            ).pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        rows_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        rows_container.pack(fill="both", expand=True)
        
        tab.rows_container = rows_container
        tab.ubicacion = ubicacion
        
        self.actualizar_tabla_ubicacion(ubicacion, tab)
    
    def crear_tab_enlaces(self):
        container = ctk.CTkFrame(self.tab_enlaces, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(
            btn_frame,
            text="➕ Agregar Enlace",
            command=self.agregar_enlace,
            width=180,
            height=35,
            corner_radius=8,
            fg_color=self.colors['success'],
            hover_color="#388e3c"
        ).pack(side="left", padx=5)
        
        table_frame = ctk.CTkScrollableFrame(
            container,
            fg_color=self.colors['card_bg'],
            corner_radius=15
        )
        table_frame.pack(fill="both", expand=True)
        
        header = ctk.CTkFrame(table_frame, fg_color=self.colors['primary'], corner_radius=10)
        header.pack(fill="x", padx=5, pady=(5, 10))
        
        headers = [("Nombre", 0.25), ("IP", 0.2), ("Proveedor", 0.2), ("Ubicación", 0.15), ("Estado", 0.1)]
        for texto, peso in headers:
            ctk.CTkLabel(
                header,
                text=texto,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            ).pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        rows_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        rows_container.pack(fill="both", expand=True)
        
        self.tab_enlaces.rows_container = rows_container
        
        self.actualizar_tabla_enlaces()
    
    def crear_tab_log(self):
        container = ctk.CTkFrame(self.tab_log, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Limpiar Log",
            command=self.limpiar_log,
            width=140,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Log",
            command=self.guardar_log,
            width=140,
            height=35
        ).pack(side="left", padx=5)
        
        self.txt_log = ctk.CTkTextbox(
            container,
            font=ctk.CTkFont(size=11, family="Consolas"),
            fg_color="#1a1a1a"
        )
        self.txt_log.pack(fill="both", expand=True)
    
    def actualizar_tabla_ubicacion(self, ubicacion, tab):
        for widget in tab.rows_container.winfo_children():
            widget.destroy()
        
        dispositivos = self.dispositivos.get('ubicaciones', {}).get(ubicacion, [])
        
        for i, disp in enumerate(dispositivos):
            self.crear_fila_dispositivo(tab.rows_container, disp, i)
    
    def actualizar_tabla_enlaces(self):
        for widget in self.tab_enlaces.rows_container.winfo_children():
            widget.destroy()
        
        enlaces = self.dispositivos.get('enlaces_internet', [])
        
        for i, enlace in enumerate(enlaces):
            self.crear_fila_enlace(self.tab_enlaces.rows_container, enlace, i)
    
    def crear_fila_dispositivo(self, parent, disp, index):
        estado = disp.get('estado', 'Desconocido')
        
        if estado == 'En línea':
            color_estado = self.colors['success']
            icon = "✅"
        elif estado == 'Caído':
            color_estado = self.colors['danger']
            icon = "❌"
        else:
            color_estado = self.colors['warning']
            icon = "⚠️"
        
        bg_color = self.colors['hover'] if index % 2 == 0 else "transparent"
        row = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=8)
        row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(row, text=disp.get('tipo', 'Otro'), font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(side="left", padx=15, pady=12, fill="x", expand=True)
        ctk.CTkLabel(row, text=disp['ip'], font=ctk.CTkFont(size=13, family="Consolas", weight="bold"), anchor="w").pack(side="left", padx=15, pady=12, fill="x", expand=True)
        ctk.CTkLabel(row, text=disp['nombre'], font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(side="left", padx=15, pady=12, fill="x", expand=True)
        ctk.CTkLabel(row, text=f"{icon} {estado}", font=ctk.CTkFont(size=12, weight="bold"), text_color=color_estado).pack(side="left", padx=15, pady=12, fill="x", expand=True)
        ctk.CTkLabel(row, text=disp.get('ultima_revision', '-'), font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=15, pady=12, fill="x", expand=True)
    
    def crear_fila_enlace(self, parent, enlace, index):
        estado = enlace.get('estado', 'Desconocido')
        
        if estado == 'En línea':
            color_estado = self.colors['success']
            icon = "✅"
        elif estado == 'Caído':
            color_estado = self.colors['danger']
            icon = "❌"
        else:
            color_estado = self.colors['warning']
            icon = "⚠️"
        
        bg_color = self.colors['hover'] if index % 2 == 0 else "transparent"
        row = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=8)
        row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(row, text=enlace['nombre'], font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(side="left", padx=15, pady=12, fill="x", expand=True)
        ctk.CTkLabel(row, text=enlace['ip'], font=ctk.CTkFont(size=13, family="Consolas", weight="bold"), anchor="w").pack(side="left", padx=15, pady=12, fill="x", expand=True)
        ctk.CTkLabel(row, text=enlace.get('proveedor', '-'), font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(side="left", padx=15, pady=12, fill="x", expand=True)
        ctk.CTkLabel(row, text=enlace.get('ubicacion', '-'), font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(side="left", padx=15, pady=12, fill="x", expand=True)
        ctk.CTkLabel(row, text=f"{icon}", font=ctk.CTkFont(size=12, weight="bold"), text_color=color_estado).pack(side="left", padx=15, pady=12, fill="x", expand=True)
    
    def agregar_dispositivo_ubicacion(self, ubicacion):
        """Agrega dispositivo a ubicación"""
        dialog = ctk.CTkInputDialog(
            text=f"Ingresa IP del nuevo dispositivo para {ubicacion}:",
            title="Agregar Dispositivo"
        )
        ip = dialog.get_input()
        
        if ip:
            if 'ubicaciones' not in self.dispositivos:
                self.dispositivos['ubicaciones'] = {}
            if ubicacion not in self.dispositivos['ubicaciones']:
                self.dispositivos['ubicaciones'][ubicacion] = []
            
            nombre = f"Dispositivo-{ip.split('.')[-1]}"
            
            nuevo = {
                'tipo': 'Otro',
                'ip': ip,
                'nombre': nombre,
                'estado': 'Desconocido',
                'ultima_revision': '-'
            }
            
            self.dispositivos['ubicaciones'][ubicacion].append(nuevo)
            self.estados_previos[f"{ip}_{nombre}"] = 'Desconocido'
            
            for tab_nombre, tab in self.tabs.items():
                if tab.ubicacion == ubicacion:
                    self.actualizar_tabla_ubicacion(ubicacion, tab)
                    break
            
            self.guardar_config()
            ToastNotification(self.root, f"Dispositivo agregado: {ip}", "success")
    
    def agregar_enlace(self):
        """Agrega enlace de internet"""
        dialog = ctk.CTkInputDialog(text="Ingresa IP del enlace:", title="Agregar Enlace")
        ip = dialog.get_input()
        
        if ip:
            if 'enlaces_internet' not in self.dispositivos:
                self.dispositivos['enlaces_internet'] = []
            
            nombre = f"Enlace-{ip.split('.')[-1]}"
            
            nuevo = {
                'nombre': nombre,
                'ip': ip,
                'proveedor': 'ISP',
                'ubicacion': self.ubicaciones[0],
                'estado': 'Desconocido',
                'ultima_revision': '-'
            }
            
            self.dispositivos['enlaces_internet'].append(nuevo)
            self.estados_previos[f"{ip}_{nombre}"] = 'Desconocido'
            
            self.actualizar_tabla_enlaces()
            self.guardar_config()
            ToastNotification(self.root, f"Enlace agregado: {ip}", "success")
    
    def ping(self, ip):
        try:
            sistema = platform.system().lower()
            if sistema == 'windows':
                comando = ['ping', '-n', '1', '-w', '1000', ip]
                flags = subprocess.CREATE_NO_WINDOW
            else:
                comando = ['ping', '-c', '1', '-W', '1', ip]
                flags = 0
            
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=2,
                creationflags=flags if sistema == 'windows' else 0
            )
            return resultado.returncode == 0
        except:
            return False
    
    def probar_dispositivos(self):
        total = 0
        online = 0
        offline = 0
        
        # Probar ubicaciones
        for ubicacion in self.dispositivos.get('ubicaciones', {}):
            for disp in self.dispositivos['ubicaciones'][ubicacion]:
                total += 1
                resultado = self.ping(disp['ip'])
                ahora = datetime.now().strftime('%H:%M:%S')
                disp['ultima_revision'] = ahora
                
                key = f"{disp['ip']}_{disp['nombre']}"
                estado_anterior = self.estados_previos.get(key, 'Desconocido')
                
                if resultado:
                    disp['estado'] = 'En línea'
                    online += 1
                    if estado_anterior == 'Caído':
                        self.agregar_log(f"[{ahora}] ✅ {ubicacion} - {disp['nombre']} - RECUPERADO\n")
                else:
                    disp['estado'] = 'Caído'
                    offline += 1
                    if estado_anterior == 'En línea':
                        self.agregar_log(f"[{ahora}] ❌ {ubicacion} - {disp['nombre']} - CAÍDO\n")
                
                self.estados_previos[key] = disp['estado']
            
            for tab_nombre, tab in self.tabs.items():
                if tab.ubicacion == ubicacion:
                    self.root.after(0, lambda u=ubicacion, t=tab: self.actualizar_tabla_ubicacion(u, t))
                    break
        
        # Probar enlaces
        for enlace in self.dispositivos.get('enlaces_internet', []):
            total += 1
            resultado = self.ping(enlace['ip'])
            ahora = datetime.now().strftime('%H:%M:%S')
            enlace['ultima_revision'] = ahora
            
            key = f"{enlace['ip']}_{enlace['nombre']}"
            estado_anterior = self.estados_previos.get(key, 'Desconocido')
            
            if resultado:
                enlace['estado'] = 'En línea'
                online += 1
                if estado_anterior == 'Caído':
                    self.agregar_log(f"[{ahora}] ✅ ENLACE - {enlace['nombre']} - RECUPERADO\n")
            else:
                enlace['estado'] = 'Caído'
                offline += 1
                if estado_anterior == 'En línea':
                    self.agregar_log(f"[{ahora}] ❌ ENLACE - {enlace['nombre']} - CAÍDO\n")
            
            self.estados_previos[key] = enlace['estado']
        
        self.root.after(0, lambda: self.actualizar_tabla_enlaces())
        
        # Actualizar stats
        self.root.after(0, lambda: self.card_total.configure(text=str(total)))
        self.root.after(0, lambda: self.card_online.configure(text=str(online)))
        self.root.after(0, lambda: self.card_offline.configure(text=str(offline)))
        
        return offline > 0
    
    def ciclo_monitoreo(self):
        while self.monitoreando:
            self.probar_dispositivos()
            for _ in range(self.intervalo.get()):
                if not self.monitoreando:
                    break
                time.sleep(1)
    
    def iniciar_monitoreo(self):
        if self.monitoreando:
            return
        
        self.monitoreando = True
        self.btn_iniciar.configure(state="disabled")
        self.btn_detener.configure(state="normal")
        self.lbl_estado.configure(text="🟢 MONITOREANDO", text_color=self.colors['success'])
        
        thread = threading.Thread(target=self.ciclo_monitoreo, daemon=True)
        thread.start()
        
        self.agregar_log(f"[{datetime.now().strftime('%H:%M:%S')}] ▶️ Monitoreo iniciado\n")
        ToastNotification(self.root, "Monitoreo iniciado", "info")
    
    def detener_monitoreo(self):
        self.monitoreando = False
        self.btn_iniciar.configure(state="normal")
        self.btn_detener.configure(state="disabled")
        self.lbl_estado.configure(text="⚪ DETENIDO", text_color="gray")
        
        self.agregar_log(f"[{datetime.now().strftime('%H:%M:%S')}] ⏹️ Monitoreo detenido\n")
        ToastNotification(self.root, "Monitoreo detenido", "info")
    
    def probar_una_vez(self):
        thread = threading.Thread(target=self.probar_dispositivos, daemon=True)
        thread.start()
    
    def agregar_log(self, texto):
        self.txt_log.insert("end", texto)
        self.txt_log.see("end")
    
    def limpiar_log(self):
        self.txt_log.delete("0.0", "end")
    
    def guardar_log(self):
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt")],
            initialfile=f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(self.txt_log.get("0.0", "end"))
            messagebox.showinfo("Éxito", "Log guardado")
    
    def cargar_config(self):
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.crear_config_default()
        except:
            return self.crear_config_default()
    
    def crear_config_default(self):
        return {
            "ubicaciones": {
                "WEC AICM": [],
                "WEC AIFA": [],
                "CORPORATIVO": [],
                "WEC LOGISTICA": []
            },
            "enlaces_internet": []
        }
    
    def guardar_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.dispositivos, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
    
    def al_cerrar(self):
        if self.monitoreando:
            if messagebox.askyesno("Confirmar", "¿Detener monitoreo y salir?"):
                self.detener_monitoreo()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    app = MonitorRed(root)
    root.mainloop()


if __name__ == "__main__":
    main()
