FROM python:3.11-slim

# Munkakönyvtár beállítása
WORKDIR /app

# Rendszerszintű függőségek telepítése (PostgreSQL kliens könyvtárak)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Requirements másolása és telepítése
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Alkalmazás fájlok másolása
COPY . .

# Port beállítása
EXPOSE 8000

# Alkalmazás futtatása
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
