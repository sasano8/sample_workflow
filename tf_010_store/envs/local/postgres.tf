resource "docker_image" "postgres" {
  name = "postgres:16"
}

resource "docker_container" "postgres" {
  name  = "postgres"
  image = docker_image.postgres.name
  ports {
    internal = 5432
    external = 5432
  }
  env = [
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}",
    "TZ=UTC"
  ]
  networks_advanced {
    name = docker_network.internal.name
  }
  command = [
    "postgres",
    "-c",
    "wal_level=logical"
  ]
}

provider "postgresql" {
  alias           = "postgresql"
  host            = var.postgres_host
  port            = var.postgres_port
  username        = var.postgres_user
  password        = var.postgres_password
  database        = var.postgres_db
  sslmode         = "disable"
}

resource "null_resource" "wait_for_postgres" {
  depends_on = [docker_container.postgres]

  provisioner "local-exec" {
    command = "bash -c 'for i in {1..10}; do pg_isready -h ${var.postgres_host} -p ${var.postgres_port} && exit 0 || sleep 2; done; exit 1'"
  }
}

resource "postgresql_schema" "db_schemas" {
  provider = postgresql.postgresql
  depends_on = [null_resource.wait_for_postgres]

  for_each = var.postgres_schemas
  name  = each.key
  owner = each.value
}
