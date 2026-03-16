output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.solar_scope.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.solar_scope.public_ip
}

output "frontend_url" {
  description = "Frontend URL"
  value       = "http://${aws_instance.solar_scope.public_ip}:5173"
}

output "backend_health_url" {
  description = "Backend health endpoint URL"
  value       = "http://${aws_instance.solar_scope.public_ip}:3000/health"
}

output "ssh_command" {
  description = "SSH command to connect to EC2"
  value       = "ssh -i <path-to-private-key.pem> ubuntu@${aws_instance.solar_scope.public_ip}"
}
