locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "solar_scope" {
  name        = "${local.name_prefix}-sg"
  description = "Security group for Solar Scope stack"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  ingress {
    description = "Frontend UI"
    from_port   = 5173
    to_port     = 5173
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  ingress {
    description = "Backend health/API"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  dynamic "ingress" {
    for_each = var.expose_service_ports ? [1] : []
    content {
      description = "AI service"
      from_port   = 8005
      to_port     = 8005
      protocol    = "tcp"
      cidr_blocks = [var.allowed_cidr]
    }
  }

  dynamic "ingress" {
    for_each = var.expose_service_ports ? [1] : []
    content {
      description = "PV simulation service"
      from_port   = 8001
      to_port     = 8001
      protocol    = "tcp"
      cidr_blocks = [var.allowed_cidr]
    }
  }

  dynamic "ingress" {
    for_each = var.expose_service_ports ? [1] : []
    content {
      description = "Satellite service"
      from_port   = 8000
      to_port     = 8000
      protocol    = "tcp"
      cidr_blocks = [var.allowed_cidr]
    }
  }

  dynamic "ingress" {
    for_each = var.expose_service_ports ? [1] : []
    content {
      description = "STL service"
      from_port   = 8007
      to_port     = 8007
      protocol    = "tcp"
      cidr_blocks = [var.allowed_cidr]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${local.name_prefix}-sg"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_instance" "solar_scope" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.ssh_key_name
  vpc_security_group_ids = [aws_security_group.solar_scope.id]

  user_data = templatefile("${path.module}/templates/user_data.sh.tftpl", {
    repo_url    = var.repo_url
    repo_branch = var.repo_branch
    project_dir = var.project_dir
  })

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name        = local.name_prefix
    Project     = var.project_name
    Environment = var.environment
  }
}
