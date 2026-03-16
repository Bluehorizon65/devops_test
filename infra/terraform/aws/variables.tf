variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name used in tags and resource naming"
  type        = string
  default     = "solar-scope"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type for full-stack deployment."
  type        = string
  default     = "t3.medium"
}

variable "allowed_cidr" {
  description = "CIDR block allowed to access exposed ports"
  type        = string
  default     = "0.0.0.0/0"
}

variable "ssh_key_name" {
  description = "Existing AWS EC2 key pair name for SSH access"
  type        = string
}

variable "repo_url" {
  description = "Git repository URL to clone on EC2"
  type        = string
  default     = "https://github.com/Bluehorizon65/devops_test.git"
}

variable "repo_branch" {
  description = "Git branch to deploy"
  type        = string
  default     = "main"
}

variable "project_dir" {
  description = "Absolute path on EC2 where project is cloned"
  type        = string
  default     = "/opt/solar-scope"
}

variable "expose_service_ports" {
  description = "Expose internal service ports for direct debugging access"
  type        = bool
  default     = false
}
