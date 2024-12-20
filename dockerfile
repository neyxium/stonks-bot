FROM python:3.9

# Delovna mapa
WORKDIR /app

# Kopiraj datoteke
COPY . /app

# Namesti odvisnosti
RUN pip install --no-cache-dir -r requirements.txt

# Zaženi aplikacijo
CMD ["python", "src/main.py"]
