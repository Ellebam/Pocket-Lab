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
  end

  subgraph Observability
    Prom[Prometheus]:::obs --> Graf
    Loki[(Loki)]:::obs --> Graf
  end

  classDef obs fill:#f3f3f3,stroke:#999,color:#000
```

**Notes**
- Traefik terminates TLS (ACME DNS-01). UIs behind basic auth where needed.
- Open WebUI talks to Ollama. RAGFlow uses Infinity/Elasticsearch, MySQL, MinIO, Valkey.
- Prometheus/Grafana/Loki provide metrics/logs.
