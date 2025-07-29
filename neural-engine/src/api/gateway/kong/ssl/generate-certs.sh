#!/bin/bash

# Generate SSL Certificates for Kong Gateway
# NeuraScale Neural Engine - Development Environment Only

set -e

CERT_DIR="$(dirname "$0")"
cd "$CERT_DIR"

echo "🔒 Generating SSL certificates for Kong Gateway..."

# Generate private key for Kong proxy
openssl genrsa -out kong.key 2048

# Generate certificate signing request for Kong proxy
openssl req -new -key kong.key -out kong.csr -subj "/C=US/ST=CA/L=San Francisco/O=NeuraScale/OU=Neural Engine/CN=api.neurascale.local"

# Generate self-signed certificate for Kong proxy
openssl x509 -req -in kong.csr -signkey kong.key -out kong.crt -days 365 -extensions v3_req -extfile <(
cat <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = api.neurascale.local
DNS.2 = kong-gateway
DNS.3 = localhost
DNS.4 = neurascale-kong-gateway
IP.1 = 127.0.0.1
IP.2 = 10.0.0.1
EOF
)

# Generate private key for Kong admin
openssl genrsa -out admin.key 2048

# Generate certificate signing request for Kong admin
openssl req -new -key admin.key -out admin.csr -subj "/C=US/ST=CA/L=San Francisco/O=NeuraScale/OU=Neural Engine Admin/CN=admin.neurascale.local"

# Generate self-signed certificate for Kong admin
openssl x509 -req -in admin.csr -signkey admin.key -out admin.crt -days 365 -extensions v3_req -extfile <(
cat <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = admin.neurascale.local
DNS.2 = kong-admin
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF
)

# Set appropriate permissions
chmod 600 *.key
chmod 644 *.crt

# Clean up CSR files
rm -f *.csr

echo "✅ SSL certificates generated successfully!"
echo "📄 Files created:"
echo "   - kong.crt / kong.key (Proxy SSL)"
echo "   - admin.crt / admin.key (Admin API SSL)"
echo ""
echo "⚠️  IMPORTANT: These are self-signed certificates for development only!"
echo "   For production, use certificates from a trusted CA."
echo ""
echo "🔧 Add to /etc/hosts for local development:"
echo "   127.0.0.1 api.neurascale.local"
echo "   127.0.0.1 admin.neurascale.local"
