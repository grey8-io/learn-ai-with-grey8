# =============================================================================
# Web — Next.js frontend for Learn AI With Grey8
# =============================================================================
# Multi-stage build: install + build in a large image, then copy the
# standalone output into a minimal runner image.
#
# Build:  docker build -f docker/web.Dockerfile -t learn-ai-web .
# Run:    docker run -p 3000:3000 learn-ai-web
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — Builder
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies (cached unless package files change)
COPY platform/web/package.json platform/web/package-lock.json* ./
RUN npm ci

# Copy the full web source and build
COPY platform/web/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2 — Runner (minimal image)
# ---------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy the standalone build output from the builder stage
# Next.js standalone mode produces a self-contained server
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
