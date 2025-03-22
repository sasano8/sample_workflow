terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

resource "docker_image" "minio" {
  name = "minio/minio:latest"
}

resource "docker_container" "minio" {
  name  = "minio"
  image = docker_image.minio.name
  ports {
    internal = 9000
    external = 9000
  }
  ports {
    internal = 9001
    external = 9001
  }

  command = [
    "server",
    "/data",
    "--console-address", ":9001",
    "--address", "0.0.0.0:9000"
  ]

  env = [
    "MINIO_ROOT_USER=${var.minio_root_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_root_password}",
    "MINIO_DOMAIN=minio",
  ]
}

provider "aws" {
  alias   = "minio"
  region  = var.minio_region
  access_key = var.minio_root_user
  secret_key = var.minio_root_password
  endpoints {
    s3 = var.minio_endpoint
  }

  s3_use_path_style = true

  # aws そのものの機能はスキップする
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

resource "null_resource" "wait_for_minio" {
  depends_on = [docker_container.minio]

  provisioner "local-exec" {
    command = "bash -c 'for i in {1..10}; do curl -s ${var.minio_endpoint}/minio/health/ready && exit 0 || sleep 2; done; exit 1'"
  }
}

resource "aws_s3_bucket" "buckets" {
  depends_on = [null_resource.wait_for_minio]
  provider   = aws.minio

  for_each = var.buckets
  bucket = each.key
}

resource "aws_s3_bucket_policy" "policies" {
  depends_on = [aws_s3_bucket.buckets]
  provider = aws.minio

  for_each = aws_s3_bucket.buckets
  bucket = each.value.id

  policy = jsonencode(
    var.buckets[each.key] == "public" ? {
      Version = "2012-10-17",
      Statement = [
        {
          Effect  = "Allow",
          Principal = {
            AWS = [
              "*"
            ]
          },
          Action = [
            "s3:GetBucketLocation",
            "s3:ListBucket",
            "s3:ListBucketMultipartUploads"
          ],
          Resource = [
            "arn:aws:s3:::${each.value.id}"
          ]
        },
        {
          Effect  = "Allow",
          Principal = {
            AWS = [
              "*"
            ]
          },
          Action = [
            "s3:PutObject",
            "s3:AbortMultipartUpload",
            "s3:DeleteObject",
            "s3:GetObject",
            "s3:ListMultipartUploadParts",
          ],
          Resource = [
            "arn:aws:s3:::${each.value.id}/*"
          ]
        },
      ]
    } : {
      Version = "2012-10-17",
      Statement = []
    }
  )
}
