# Use a lightweight Debian-based Python image
FROM python:3.11-slim

# Install Node.js, npm, curl, and libatomic1 (required by pnpm on slim debian images)
RUN apt-get update && apt-get install -y \
    curl \
    libatomic1 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire monorepo
COPY . .

# ==========================================
# 1. Setup Backend (FastAPI)
# ==========================================
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt
# Install uvicorn explicitly just in case it's missing from requirements
RUN pip install --no-cache-dir uvicorn[standard] asyncpg bcrypt

# ==========================================
# 2. Setup Frontend (Next.js)
# ==========================================
WORKDIR /app/frontend
# HuggingFace might not have pnpm, use npm for standard Docker building
RUN npm install -g pnpm
RUN pnpm install

# Next.js needs these build-time env vars to compile pages that use Supabase
# In HuggingFace, you will define these in the Space Secrets, but for the Docker build step
# we need dummy values so the build doesn't crash.
ARG NEXT_PUBLIC_SUPABASE_URL="https://placeholder.supabase.co"
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY="placeholder"

# Build the Next.js app
RUN pnpm run build

# ==========================================
# 3. Final Execution Setup
# ==========================================
WORKDIR /app

# Ensure start script is executable
RUN chmod +x start.sh

# Hugging Face exposes port 7860
EXPOSE 7860

# Run the startup script that boots both processes
CMD ["./start.sh"]
