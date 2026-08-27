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

# Build the Next.js app - uses build args for Supabase credentials
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY

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
