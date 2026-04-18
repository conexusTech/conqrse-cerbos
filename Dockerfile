FROM ghcr.io/cerbos/cerbos:0.51.0

# Copy configuration
COPY cerbos.yaml /etc/cerbos/cerbos.yaml

# Copy policies and schemas
COPY k8s/base/policies /policies
COPY k8s/base/schemas /schemas

CMD ["server", "--config=/etc/cerbos/cerbos.yaml"]