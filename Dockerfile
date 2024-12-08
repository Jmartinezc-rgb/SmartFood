# Imagen
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Configura las variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Actualiza pip
RUN python3.10 -m pip install --upgrade pip

# Copia el archivo de requisitos e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . /app

# Opcional: crea un usuario no root y ajusta permisos
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Durante la depuración, este punto de entrada será sobrescrito
CMD ["python3.10", "train.py"]
