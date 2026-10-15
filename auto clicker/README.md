# 🖱️ AutoClicker Pro

Auto-clic de escritorio **ligero, moderno y multiplataforma** para Windows, macOS y Linux.
Configura el intervalo, el botón, el número de clics y déjalo trabajar mientras tú haces otra cosa.
Se activa y se desactiva con una sola tecla desde **cualquier programa**.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows%20%7C%20macOS%20%7C%20Linux-7aa2f7)
![Licencia](https://img.shields.io/badge/Licencia-MIT-9ece6a)
![Estado](https://img.shields.io/badge/Estado-estable-brightgreen)

---

## ✨ Características

| Función | Descripción |
| --- | --- |
| ⌨️ **Tecla rápida global** | `F6` inicia y detiene el auto-clic sin importar dónde estés. |
| ⏱️ **Intervalo configurable** | Ajusta el tiempo entre clics en milisegundos y ve los **CPS** en vivo. |
| 🖱️ **Tipo de botón** | Clic izquierdo, derecho o central. |
| ⚡ **Doble clic** | Envía dos pulsaciones por ciclo. |
| 📍 **Posición fija** | Bloquea el cursor en la posición actual para clics precisos. |
| 🎲 **Jitter aleatorio** | Varia el intervalo ±30% para un patrón menos mecánico. |
| 🔢 **Límite de clics** | Detén la automatización automáticamente tras *N* clics. |
| 📊 **Contador en vivo** | Cuenta y permite reiniciar los clics realizados. |
| 🌙 **Interfaz oscura** | UI limpia construida con Tkinter, sin dependencias pesadas. |

---

## 🚀 Instalación

### 1. Requisitos

- **Python 3.8 o superior** → [descargar aquí](https://www.python.org/downloads/).
  En Windows marca la casilla **"Add Python to PATH"** durante la instalación.

### 2. Descargar el proyecto

```bash
git clone https://github.com/TU_USUARIO/autoclicker.git
cd autoclicker
```

> También puedes descargarlo como ZIP y descomprimirlo.

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ▶️ Uso

```bash
python autoclicker.py
```

En Windows, para ejecutarlo **sin la ventana negra de consola**:

```bash
pythonw autoclicker.py
```

### Cómo usarlo en 4 pasos

1. Abre el programa con el comando de arriba.
2. Ajusta el **intervalo**, el **botón** y las opciones que quieras.
3. Pulsa **Iniciar** o presiona `F6`.
4. Cambia a tu juego o aplicación: los clics seguirán ejecutándose. Presiona `F6` para detener.

---

## ⌨️ Atajos

| Tecla | Acción |
| --- | --- |
| `F6` | Iniciar / Detener el auto-clic |

---

## 📖 Ejemplos de configuración

| Escenario | Intervalo | Opciones |
| --- | --- | --- |
| Clic rápido para idle games | `10 ms` (100 CPS) | Botón izquierdo |
| Clic humano y natural | `250 ms` | Jitter activado |
| Cliquear en un punto fijo | `100 ms` | Posición fija + límite `500` |
| Menú contextual repetido | `400 ms` | Botón derecho |

> **Consejo:** un intervalo de `1 ms` produce ~1000 CPS, pero muchos sistemas no procesan
> tantos eventos. Empieza con `50–100 ms` y ajusta según necesites.

---

## 🗂️ Estructura del proyecto

```
autoclicker/
├── autoclicker.py      # Programa principal (GUI + motor de clics)
├── requirements.txt    # Dependencias
├── README.md           # Este archivo
├── LICENSE             # Licencia MIT
└── .gitignore          # Exclusiones de Git
```

---

## 🧠 Cómo funciona

- **Tkinter** dibuja la interfaz (incluida en Python, sin instalación extra).
- **pynput** controla el ratón y escucha el atajo `F6` a nivel global.
- El motor de clics corre en un **hilo aparte** para que la ventana nunca se congele.
- La comunicación entre el hilo y la interfaz usa una **cola thread-safe**, evitando
  errores por acceso concurrente a Tkinter.

---

## ❓ Preguntas frecuentes

<details>
<summary><b>El atajo F6 no responde</b></summary>

- Otro programa puede estar capturando `F6`. Ciérralo o cambia la constante `HOTKEY`
  en la parte superior de `autoclicker.py`.
- En **Linux** puede que necesites ejecutar el programa con permisos (ver abajo).
</details>

<details>
<summary><b>En macOS se pide permiso de Accesibilidad</b></summary>

Ve a **Ajustes del Sistema → Privacidad y seguridad → Accesibilidad** y activa la
casilla para tu terminal o para Python. Es necesario para simular clics.
</details>

<details>
<summary><b>En Linux no funciona bajo Wayland</b></summary>

`pynput` requiere X11. Inicia sesión con una sesión **Xorg** o ejecuta con `sudo`
si tu sistema lo permite.
</details>

<details>
<summary><b>¿Funciona en juegos?</b></summary>

Depende del juego. Algunos anticheat bloquean la simulación de entrada; en esos casos
el auto-clic no tendrá efecto. Úsalo solo donde esté permitido.
</details>

> ⚠️ **Aviso:** el uso de auto-clic puede estar prohibido por las normas de ciertos juegos
> o servicios en línea. Úsalo de forma responsable y bajo tu propia responsabilidad.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Haz un *fork* del repositorio.
2. Crea una rama: `git checkout -b feature/mi-mejora`.
3. Confirma tus cambios: `git commit -m "Añade mi mejora"`.
4. Envía la rama: `git push origin feature/mi-mejora`.
5. Abre un *Pull Request*.

---

## 📄 Licencia

Distribuido bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

<p align="center">Hecho con ❤️ usando Python</p>
