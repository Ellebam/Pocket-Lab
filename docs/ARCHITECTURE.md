# Architecture

```mermaid
flowchart LR
  subgraph Users
    U[Admin/Developers]
  end

  U -->|HTTPS| T[Traefik]
  subgraph Edge
    T
  end

  T --> OWUI[Open WebUI]
  T --> RAG[RAGFlow]
  T --> N8N[n8n]
  T --> PDF[Stirling PDF]
  T --> Port[Portainer]
  T --> Sear[SearXNG]
  T --> Graf[Grafana]

  subgraph AI & Apps
    OWUI --> OL[Ollama]
    RAG --> ES[(Elasticsearch/Infinity)]
    RAG --> MY[(MySQL)]
    RAG --> MINIO[(MinIO / S3)]
    RAG --> VK[(Valkey)]
    N8N --> OL
    N8N --> ES
    N8N --> MY
    N8N --> MINIO
    N8N --> VK
  end

  subgraph Observability
    Prom[Prometheus]:::obs --> Graf
    Loki[(Loki)]:::obs --> Graf
  end

  classDef obs fill:#f3f3f3,stroke:#999,color:#000
```

**Notes**
- Traefik terminates TLS (ACME DNS-01). UIs behind basic auth where needed.
- Open WebUI, RAGFlow, and n8n share Ollama as the default LLM backend.
- RAGFlow and n8n use Infinity/Elasticsearch, MySQL, MinIO, and Valkey for pipelines and automations.
- Prometheus/Grafana/Loki provide metrics/logs.
