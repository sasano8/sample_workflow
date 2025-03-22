variable "rw_user" {
  type    = string
  default = "root"
}

variable "rw_password" {
  type    = string
  default = ""
}

variable "rw_db" {
  type    = string
  default = "dev"
}

variable "rw_schemas" {
  type = map(string)
  default = {
    warehouse        = "admin"
    gmailattachments = "admin"
  }
}

variable "enable_telemetry" {
  type    = bool
  default = true
}

variable "rw_telemetry_type" {
  type    = string
  default = "docker-compose"
}

resource "docker_image" "risingwave" {
  name = "risingwavelabs/risingwave:v2.2.3"
}

resource "docker_container" "risingwave" {
  depends_on = [docker_container.minio]
  networks_advanced {
    name = docker_network.internal.name
  }

  name  = "risingwave-standalone"
  image = docker_image.risingwave.name

  command = [
    "standalone",
    "--meta-opts=--listen-addr 0.0.0.0:5690 --advertise-addr 0.0.0.0:5690 --dashboard-host 0.0.0.0:5691 --prometheus-host 0.0.0.0:1250 --prometheus-endpoint http://prometheus-0:9500 --backend sql --sql-endpoint sqlite:///meta-data/metadata.db?mode=rwc --state-store ${var.rw_state_store_endpoint} --data-directory hummock_001 --config-path /risingwave.toml",
    "--compute-opts=--config-path /risingwave.toml --listen-addr 0.0.0.0:5688 --prometheus-listener-addr 0.0.0.0:1250 --advertise-addr 0.0.0.0:5688 --async-stack-trace verbose --parallelism 8 --total-memory-bytes 21474836480 --role both --meta-address http://0.0.0.0:5690",
    "--frontend-opts=--config-path /risingwave.toml --listen-addr 0.0.0.0:4566 --advertise-addr 0.0.0.0:4566 --prometheus-listener-addr 0.0.0.0:1250 --health-check-listener-addr 0.0.0.0:6786 --meta-addr http://0.0.0.0:5690",
    "--compactor-opts=--listen-addr 0.0.0.0:6660 --prometheus-listener-addr 0.0.0.0:1250 --advertise-addr 0.0.0.0:6660 --meta-address http://0.0.0.0:5690"
  ]

  env = [
    "RUST_BACKTRACE=1",
    "ENABLE_TELEMETRY=${var.enable_telemetry}",
    "RW_TELEMETRY_TYPE=${var.rw_telemetry_type}"
  ]

  ports {
    internal = 4566
    external = 4566  # db port
  }
  ports {
    internal = 5690
    external = 5690
  }
  ports {
    internal = 5691
    external = 5691  # UI
  }
  ports {
    internal = 1250
    external = 1250  # log?
  }

  volumes {
    host_path      = abspath("./.configs/risingwave.toml")
    container_path = "/risingwave.toml"
  }

  volumes {
    host_path      = abspath("./.volumes/risingwave-0")
    container_path = "/meta-data"
  }

  restart = "always"

  healthcheck {
    test = ["CMD-SHELL", "bash -c 'printf \"GET / HTTP/1.1\\n\\n\" > /dev/tcp/127.0.0.1/6660'", "bash -c 'printf \"GET / HTTP/1.1\\n\\n\" > /dev/tcp/127.0.0.1/5688'", "bash -c 'printf \"GET / HTTP/1.1\\n\\n\" > /dev/tcp/127.0.0.1/4566'", "bash -c 'printf \"GET / HTTP/1.1\\n\\n\" > /dev/tcp/127.0.0.1/5690'"]
    interval = "1s"
    timeout  = "5s"
  }
}
