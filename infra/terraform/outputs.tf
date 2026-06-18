###############################################################################
# EDU AI Agent Suite - Terraform parity - outputs
# Mirrors the CloudFormation master stack outputs (quickstart.yaml).
###############################################################################

output "vpc_id" {
  description = "Suite VPC ID."
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "Private subnet IDs (agent runtime + Lambdas)."
  value       = aws_subnet.private[*].id
}

output "agent_runtime_security_group_id" {
  description = "Security group for agent runtime compute."
  value       = aws_security_group.agent_runtime.id
}

output "kms_key_arn" {
  description = "Per-environment customer-managed KMS key ARN."
  value       = aws_kms_key.env.arn
}

output "guardrail_id" {
  description = "Bedrock Guardrail ID applied on every LLM call."
  value       = aws_bedrock_guardrail.agent.guardrail_id
}

output "guardrail_version" {
  description = "Published Guardrail version."
  value       = aws_bedrock_guardrail_version.agent.version
}

output "user_pool_id" {
  description = "Cognito user pool federating the institution IdP."
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_client_id" {
  description = "Cognito app client ID (gateway authorizer audience)."
  value       = aws_cognito_user_pool_client.main.id
}

output "identity_pool_id" {
  description = "Cognito identity pool ID."
  value       = aws_cognito_identity_pool.main.id
}

output "agent_execution_role_arn" {
  description = "Least-privilege agent execution role ARN."
  value       = aws_iam_role.agent_execution.arn
}

output "audit_table_name" {
  description = "Append-only DynamoDB audit table name."
  value       = aws_dynamodb_table.audit.name
}

output "audit_table_arn" {
  description = "Append-only DynamoDB audit table ARN (agent role has PutItem only)."
  value       = aws_dynamodb_table.audit.arn
}

output "hitl_queue_table_name" {
  description = "HITL approval-queue DynamoDB table name."
  value       = aws_dynamodb_table.hitl_queue.name
}

output "worm_bucket_name" {
  description = "S3 Object Lock (COMPLIANCE) WORM bucket name."
  value       = aws_s3_bucket.worm.bucket
}

output "gateway_authorizer_param" {
  description = "SSM parameter holding the gateway authorizer (Cognito) config."
  value       = aws_ssm_parameter.gateway_authorizer.name
}

output "gateway_target_params" {
  description = "SSM parameter names for the four systems-of-record targets."
  value       = { for k, p in aws_ssm_parameter.gateway_target : k => p.name }
}

output "state_machine_arn" {
  description = "Step Functions state machine ARN (native path, includes the HITL gate). Empty for container mode."
  value       = local.is_native ? aws_sfn_state_machine.agent[0].arn : ""
}

output "deploy_mode_used" {
  description = "Runtime path provisioned for the agent."
  value       = var.deploy_mode
}
