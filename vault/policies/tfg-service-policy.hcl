path "pki/issue/tfg-service" {
  capabilities = ["create", "update"]
}

path "pki/cert/ca" {
  capabilities = ["read"]
}

path "pki/ca" {
  capabilities = ["read"]
}

path "pki/crl" {
  capabilities = ["read"]
}
