# Stage 1: Build robust React Frontend using Vite
FROM node:18 AS frontend-builder
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy source and build the static dist folder
COPY frontend ./
RUN npm run build

# Stage 2: Serve Python Backend + HTML on Hugging Face Spaces port 7860
FROM python:3.10-slim
WORKDIR /app

# Required for Faster-Whisper to decode audio/video files
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces requires running as a non-root user (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install Python requirements
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create temp directories with correct permissions if needed by models
RUN mkdir -p /tmp/scam_call && chmod 777 /tmp/scam_call

# Copy remaining Python files
COPY --chown=user . .

# Copy built frontend assets from Stage 1 into the backend's static directory
COPY --from=frontend-builder --chown=user /app/frontend/dist ./frontend/dist

# Expose Space port
EXPOSE 7860

# Command to run FastAPI server on 0.0.0.0:7860
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
