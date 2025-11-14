FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
<<<<<<< HEAD
COPY . . 
ENV PORT=5005
EXPOSE 5005
CMD ["python3", "youface.py"]
=======
COPY . .
EXPOSE 5000
CMD ["python3", "youface.py"]

>>>>>>> bd8ab37 (updates)
