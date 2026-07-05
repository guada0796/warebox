# WAREBOX Sandbox - Guía de Instalación y Ejecución

**WAREBOX** es una herramienta automatizada y manual para la detonación y análisis de malware (Sandbox). Utiliza el SDK de VirtualBox para gestionar el ciclo de vida de máquinas virtuales de análisis y red, recolectar evidencias (capturas de red y logs de eventos de Windows como Sysmon) y generar informes técnicos automatizados utilizando el motor de reglas Sigma Hayabusa.

---

## 🛠️ Arquitectura del Proyecto

El sistema se compone de tres partes principales:
1. **Linux Host (Máquina Anfitriona)**: Ejecuta el menú interactivo [warebox.py](file:///home/stvn/github/warebox/warebox.py), controla las máquinas virtuales a través de `VBoxManage`, descomprime las muestras cifradas, extrae las evidencias y compila los reportes PDF.
2. **Debian Gateway VM (`DEBIANET`)**: Actúa como puerta de enlace e interceptor de red. Captura el tráfico de red de la muestra mediante `tcpdump`.
3. **Windows 10 Sandbox VM (`W10PRO`)**: Entorno aislado donde se detona el malware. Tiene instalado Sysmon para registrar actividades del sistema.

---

## 📌 Requisitos Previos en el Host Linux

Antes de instalar WAREBOX, asegúrate de cumplir con los siguientes requisitos en tu sistema Host (Debian/Ubuntu recomendado):

- **VirtualBox** (Versión 7.0 o superior recomendada, testeado con `7.2.6`).
- **Python** (Versión 3.12 o superior recomendada).
- **Herramientas de sistema**: `git`, `unzip`, `wget`, `p7zip-full`.

---

## 🚀 Guía de Instalación Paso a Paso

### Paso 1: Instalar Dependencias Generales del Sistema
Ejecuta el siguiente comando para instalar las herramientas de descompresión y utilidades necesarias en el Host Linux:
```bash
sudo apt update && sudo apt install -y unzip p7zip-full git wget python3-pip python3-venv
```

### Paso 2: Crear el Entorno Virtual de Python y Configurar Librerías
Navega a la raíz del proyecto y crea un entorno virtual de Python:
```bash
python3 -m venv venv
source venv/bin/activate
pip install python-evtx fpdf2 setuptools
```

### Paso 3: Instalar VirtualBox SDK Bindings en el Entorno Virtual
Para interactuar con la API de VirtualBox desde Python, es necesario instalar las bindings oficiales.
El proyecto incluye un script automatizado para descargar e instalar el SDK:
[instalar_virtualbox_sdk.sh](file:///home/stvn/github/warebox/dependencies/linux-host/instalar_virtualbox_sdk.sh)

1. Abre el script y edita la variable `VENV_DIR` (línea 12) para que apunte a la ruta absoluta de tu entorno virtual en el proyecto. Por ejemplo:
   ```bash
   VENV_DIR="/home/stvn/github/warebox/venv"
   ```
2. Ejecuta el script de instalación:
   ```bash
   chmod +x dependencies/linux-host/instalar_virtualbox_sdk.sh
   ./dependencies/linux-host/instalar_virtualbox_sdk.sh
   ```
3. Aplica los cambios en tu sesión actual de terminal:
   ```bash
   source ~/.bashrc
   ```

### Paso 4: Configurar Hayabusa y Reglas Sigma
Hayabusa se encuentra pre-compilado en el proyecto. Sin embargo, requiere descargar las reglas de detección Sigma para poder clasificar amenazas.
1. Ejecuta los siguientes comandos para clonar las reglas oficiales de Hayabusa en el directorio adecuado:
   ```bash
   cd dependencies/hayabusa
   rm -rf rules
   git clone https://github.com/Yamato-Security/hayabusa-rules.git rules
   ```
2. Opcionalmente, asegúrate de que el binario de Hayabusa tenga permisos de ejecución:
   ```bash
   chmod +x hayabusa-3.8.1-lin-x64-gnu
   ```

---

## 🖥️ Requisitos y Preparación de las Máquinas Virtuales

Para que el sandbox funcione correctamente, debes preparar dos máquinas virtuales en VirtualBox con la siguiente configuración:

### 1. Máquina Windows de Detonación (`W10PRO`)
- **Nombre en VirtualBox**: `W10PRO` (coincidente con `VM_NAME` en [config.py](file:///home/stvn/github/warebox/utils/config.py)).
- **Guest Additions**: Deben estar instaladas para permitir la copia de archivos y ejecución remota de comandos.
- **Usuario**: `ucjc` (Privilegios de Administrador).
- **Contraseña**: `ucjc`.
- **Ruta de Herramientas**: La carpeta `C:\Tools` debe existir y contener `Procmon.exe` (Process Monitor) y herramientas auxiliares.
- **Sysmon**: Debe estar instalado como servicio y configurado. Para actualizar su configuración, puedes ejecutar dentro de la VM:
  ```cmd
  cd C:\Tools\Sysmon\
  sysmon64.exe -c sandbox_config.xml
  wevtutil cl "Microsoft-Windows-Sysmon/Operational"
  shutdown /s /t 0
  ```
- **Directorio de Logs**: `C:\Users\ucjc\Desktop\Logs` (será creado si no existe).
- **Snapshot**: Tras configurar la máquina en un estado limpio, realiza un snapshot llamado **`warebox-v18`**.

### 2. Máquina Debian de Intercepción de Red (`DEBIANET`)
- **Nombre en VirtualBox**: `DEBIANET` (coincidente con `NETWORK_VM_NAME` en [config.py](file:///home/stvn/github/warebox/utils/config.py)).
- **Herramientas**: Debe tener instalado `tcpdump` y `pkill`.
- **Usuario**: `ucjc`.
- **Contraseña**: `ucjc`.
- **Snapshot**: Realiza un snapshot en un estado limpio llamado **`fake-network-v3`**.

---

## ⚙️ Configuración del Sandbox ([config.py](file:///home/stvn/github/warebox/utils/config.py))

Puedes modificar el comportamiento y las rutas del sandbox editando el archivo de configuración central [utils/config.py](file:///home/stvn/github/warebox/utils/config.py). Las variables principales son:

- `VM_NAME` / `NETWORK_VM_NAME`: Nombres de las máquinas virtuales.
- `SNAPSHOT_NAME` / `NETWORK_SNAPSHOT_NAME`: Nombres de los snapshots limpios a restaurar en cada detonación.
- `GUEST_USER` / `GUEST_PASS`: Credenciales de Windows.
- `WAIT_START_TIME`: Tiempo de espera (en segundos) para que la VM Windows encienda por completo antes de enviar el payload.
- `WAIT_MALWARE_TIME`: Tiempo de ejecución asignado al malware (en segundos).
- `COMPRESS_KEY`: Clave para descomprimir los archivos malware en formato ZIP (por defecto: `"infected"`).

---

## 🏃 Ejecución de WAREBOX

1. Activa tu entorno virtual de Python:
   ```bash
   source venv/bin/activate
   ```
2. Deposita la muestra que deseas analizar (en formato `.zip` con contraseña) en el directorio de malware del host. Por defecto, la ruta del host es:
   `~/warebox-workspace/Malware_Reports/`
3. Ejecuta el script principal de WAREBOX:
   ```bash
   python warebox.py
   ```

### 📋 Opciones del Menú Principal:
- **c. Cambiar configuración de análisis**: Permite editar temporalmente valores de configuración como el payload o los tiempos de espera.
- **d. Detonar una muestra**: Inicia el ciclo automático de detonación:
  - Descomprime y calcula el hash SHA256 de la muestra en el Host.
  - Restaura e inicia las máquinas virtuales (`W10PRO` en modo gráfico, `DEBIANET` en modo headless).
  - Activa la captura de tráfico (`tcpdump`) y la grabación de pantalla si así se solicita.
  - Transfiere y ejecuta el malware (modo automático) o da tiempo al analista para detonar manualmente.
  - Detiene y recolecta evidencias (Logs de Sysmon e intercepción PCAP).
  - Apaga las máquinas virtuales.
- **a. Analizar resultados (Manual)**: Carga las evidencias recolectadas en una VM Windows de análisis independiente y permite guardar el progreso mediante snapshots.
- **h. Analizar resultados (Automático)**: Procesa los logs EVTX de Sysmon usando Hayabusa, correlaciona las amenazas con tácticas del framework MITRE ATT&CK y genera un informe técnico en formato PDF.
- **g. Gestionar Snapshots de la VM**: Acceso directo para crear, restaurar, listar o eliminar snapshots de la VM principal.

---

## 🧹 Desinstalación del SDK y Entorno Virtual
Si deseas limpiar el SDK instalado y el entorno virtual, puedes ejecutar el script de desinstalación provisto en el proyecto:
[desinstalar_virtualbox_sdk.sh](file:///home/stvn/github/warebox/dependencies/linux-host/desinstalar_virtualbox_sdk.sh)
```bash
chmod +x dependencies/linux-host/desinstalar_virtualbox_sdk.sh
./dependencies/linux-host/desinstalar_virtualbox_sdk.sh
source ~/.bashrc
```
