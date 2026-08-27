# Use a lightweight Debian-based Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install Node.js 22 (latest LTS), npm, curl, and libatomic1 (required by pnpm)
RUN apt-get update && apt-get install -y \
    curl \
    libatomic1 \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire monorepo
COPY . .

# ==========================================
# 1. Setup Backend (FastAPI) using uv
# ==========================================
WORKDIR /app/backend
# Install dependencies using uv (much faster, uses lockfile)
RUN uv sync --frozen

# ==========================================
# 2. Setup Frontend (Next.js)
# ==========================================
WORKDIR /app/frontend
# Install pnpm and dependencies
RUN npm install -g pnpm
RUN pnpm install

# Create .env.production with hardcoded Supabase credentials for build time
RUN echo "NEXT_PUBLIC_SUPABASE_URL=https://rmeaxsqojjdaalufjkkv.supabase.co" > .env.production && \
    echo "NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZWF4c3FvampkYWFsdWZqa2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc4MjEwNjQsImV4cCI6MjEwMzM5NzA2NH0.5Ne93lEEpANNrZPU41lYfvV4WP5LZ01zoMKqyuRcp_0" >> .env.production

# Build the Next.js app
RUN pnpm run build

# ==========================================
# 3. Final Execution Setup
# ==========================================
WORKDIR /app

# Ensure start script is executable
RUN chmod +x start.sh

# ModelScope exposes port 7860
EXPOSE 7860

# Run the startup script that boots both processes
CMD ["./start.sh"]
