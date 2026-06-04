storage "file" {
  path = "/home/michele/TFG/vault/data"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = true
}

seal "awskms" {
  region     = "eu-west-1"
  kms_key_id = "5ef06218-3686-4873-a2a7-dfa3de747a9c"
}

ui = true
disable_mlock = true
