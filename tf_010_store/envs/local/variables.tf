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

variable "postgres_host" {
  type = string
  default = "localhost"
}

variable "postgres_port" {
  type = number
  default = 5432
}

variable "postgres_user" {
  type    = string
  default = "adminuser"
}

variable "postgres_password" {
  type    = string
  default = "adminuser"
}

variable "postgres_db" {
  type    = string
  default = "dev"
}

variable "postgres_schemas" {
  type = map(string) # schema名 => オーナー
  default = {
    kestra          = "adminuser"
    mlflow_catalog  = "adminuser"
  }
}
