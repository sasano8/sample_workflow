variable "minio_endpoint" {
  type = string
  default = "http://localhost:9000"
}

variable "minio_root_user" {
  type = string
  default = "adminuser"
}

variable "minio_root_password" {
  type = string
  sensitive = true
  default = "adminuser"
}

variable "minio_region" {
  type    = string
  default = "us-east-1"
}

variable "network_name" {
  type = string
  default = "internal"
}

variable "buckets" {
  type    = map(string)
  default = {
    "tf-state-store" = "private",
    "hummock001" = "private",
    "mlflow" = "public",
    "warehouse" = "public",
    "gmailattachments" = "public",
  }
}
