# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variable "app_name" {
  description = "Name of the application in the Juju model."
  type        = string
  default     = "aws-integrator"
}

variable "base" {
  description = "Ubuntu bases to deploy the charm onto"
  type        = string
  default     = "ubuntu@22.04"

  validation {
    condition     = contains(["ubuntu@22.04", "ubuntu@24.04"], var.base)
    error_message = "Base must be one of ubuntu@22.04, ubuntu@24.04"
  }
}

variable "channel" {
  description = "The channel to use when deploying a charm."
  type        = string
  default     = "latest/stable"
}

variable "config" {
  description = "Application config. Details about available options can be found at https://charmhub.io/aws-integrator/configurations."
  type        = map(string)
  default     = {}
}

variable "constraints" {
  description = "Juju constraints to apply for this application."
  type        = string
  default     = "arch=amd64"
}

variable "model" {
  description = "Reference to a `juju_model` where this application is to be managed."
  type        = string
}

variable "resources" {
  description = "Resources to use with the application. Details about available options can be found at https://charmhub.io/aws-integrator/resources."
  type        = map(string)
  default     = {}
}

variable "revision" {
  description = "Revision number of the charm"
  type        = number
  default     = null
}

variable "units" {
  description = "Number of units to deploy"
  type        = number
  default     = 1
}
