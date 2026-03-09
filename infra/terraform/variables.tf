variable "location" {
  type        = string
  description = "Azure region for resource deployment"
  default     = "Central India"
}

variable "project_name" {
  type        = string
  description = "Project name prefix used in resource naming"
  default     = "solar-scope"
}

variable "environment" {
  type        = string
  description = "Environment name (dev/stage/prod)"
  default     = "dev"
}

variable "kubernetes_version" {
  type        = string
  description = "AKS Kubernetes version"
  default     = "1.29"
}

variable "node_count" {
  type        = number
  description = "AKS node count"
  default     = 2
}
