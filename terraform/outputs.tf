# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.aws_integrator.name
}

output "provides" {
  value = {
    aws = "aws"
    rds_mysql = "rds-mysql"
  }
}
