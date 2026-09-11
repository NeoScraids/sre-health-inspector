# Multi-stage minimal container build
FROM python:3.11-alpine AS base

WORKDIR /app

# Security: Create unprivileged user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy application source code
COPY src/ /app/src/

USER appuser

ENTRYPOINT ["python", "-m", "src.inspector"]
CMD ["--help"]
