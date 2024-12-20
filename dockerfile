# Uporabi uradno Python sliko
FROM python:3.9-slim

# Nastavi delovni direktorij
WORKDIR /app

# Kopiraj vse datoteke v delovni direktorij
COPY . /app

# Namesti odvisnosti
RUN pip install --no-cache-dir -r requirements.txt

# Nastavi privzeti ukaz za zagon bota
CMD ["python", "src/main.py"]
