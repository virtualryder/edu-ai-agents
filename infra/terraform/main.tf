###############################################################################
# EDU AI Agent Suite - Terraform parity - main
#
# REFERENCE / ACCELERATOR TEMPLATE. Mirrors the CloudFormation topology in
# infra/cloudformation/ (VPC, KMS CMK, Bedrock Guardrail, Cognito + IdP,
# append-only DynamoDB audit + HITL queue, S3 Object Lock WORM, least-privilege
# IAM role, Step Functions with a waitForTaskToken HITL gate). The customer
# must harden, security-review, tune the Guardrail for their student population,
# wire their IdP role mapping, and validate connectors before production use.
#
# Resource topology is intentionally 1:1 with the CloudFormation nested stacks:
#   network.yaml -> VPC block | security.yaml -> KMS/Guardrail/Cognito/IAM
#   data.yaml    -> audit + HITL + WORM | agent-service.yaml -> Step Functions
###############################################################################

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name = "edu-agents-${var.environment}"
  base_tags = merge({
    "edu:suite"       = "edu-ai-agents"
    "edu:environment" = var.environment
  }, var.tags)
  has_idp     = var.idp_metadata_url != ""
  is_native   = var.deploy_mode == "native"
  account_id  = data.aws_caller_identity.current.account_id
  partition   = data.aws_partition.current.partition
}

#==============================================================================
# NETWORK (parity: network.yaml)
#==============================================================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(local.base_tags, { Name = "${local.name}-vpc" })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = merge(local.base_tags, { Name = "${local.name}-igw" })
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false
  tags                    = merge(local.base_tags, { Name = "${local.name}-public-${count.index + 1}", "edu:tier" = "public" })
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags              = merge(local.base_tags, { Name = "${local.name}-private-${count.index + 1}", "edu:tier" = "private" })
}

resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = merge(local.base_tags, { Name = "${local.name}-nat-eip" })
}

# Single NAT for reference; run one per AZ in production.
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  tags          = merge(local.base_tags, { Name = "${local.name}-nat" })
  depends_on    = [aws_internet_gateway.main]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = merge(local.base_tags, { Name = "${local.name}-public-rt" })
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
  tags = merge(local.base_tags, { Name = "${local.name}-private-rt" })
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "agent_runtime" {
  name        = "${local.name}-runtime-sg"
  description = "Agent runtime. No public inbound. HTTPS egress only."
  vpc_id      = aws_vpc.main.id
  egress {
    description = "HTTPS egress to AWS service + connector endpoints"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(local.base_tags, { Name = "${local.name}-runtime-sg" })
}

resource "aws_security_group" "vpce" {
  name        = "${local.name}-vpce-sg"
  description = "Interface VPC endpoints. HTTPS only from the agent runtime SG."
  vpc_id      = aws_vpc.main.id
  ingress {
    description     = "HTTPS from agent runtime"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.agent_runtime.id]
  }
  tags = merge(local.base_tags, { Name = "${local.name}-vpce-sg" })
}

# Bedrock runtime endpoint - private connectivity to the regional Bedrock service via PrivateLink; masked PII reaches Bedrock only over AWS private networking, never the public internet.
resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpce.id]
  tags                = merge(local.base_tags, { Name = "${local.name}-bedrock-runtime-vpce" })
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
  tags              = merge(local.base_tags, { Name = "${local.name}-s3-vpce" })
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
  tags              = merge(local.base_tags, { Name = "${local.name}-dynamodb-vpce" })
}

#==============================================================================
# SECURITY: KMS CMK (parity: security.yaml)
# One key per environment. Losing this CMK loses the data - see runbooks/DR-RUNBOOK.md.
#==============================================================================

resource "aws_kms_key" "env" {
  description             = "EDU AI Agent Suite CMK - ${var.environment}"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AccountRoot"
        Effect    = "Allow"
        Principal = { AWS = "arn:${local.partition}:iam::${local.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid       = "AllowAgentRoleUse"
        Effect    = "Allow"
        Principal = { AWS = aws_iam_role.agent_execution.arn }
        Action    = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
        Resource  = "*"
      }
    ]
  })
  tags = local.base_tags
}

resource "aws_kms_alias" "env" {
  name          = "alias/${local.name}"
  target_key_id = aws_kms_key.env.key_id
}

#==============================================================================
# SECURITY: Bedrock Guardrail (parity: security.yaml)
# Reference config - customer MUST tune for their population (minors / COPPA <13).
#==============================================================================

resource "aws_bedrock_guardrail" "agent" {
  name                      = "${local.name}-guardrail"
  description               = "EDU compliance Guardrail - PII denial, age-appropriate content, prohibited-behavior topic filters."
  blocked_input_messaging   = "This request cannot be processed. If you need help, please contact your school's support team."
  blocked_outputs_messaging = "This response was withheld by the institution's content safeguards."
  kms_key_arn               = aws_kms_key.env.arn

  content_policy_config {
    filters_config {
      type            = "SEXUAL"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "VIOLENCE"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "HATE"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "PROMPT_ATTACK"
      input_strength  = "HIGH"
      output_strength = "NONE"
    }
  }

  sensitive_information_policy_config {
    pii_entities_config {
      type   = "US_SOCIAL_SECURITY_NUMBER"
      action = "BLOCK"
    }
    pii_entities_config {
      type   = "NAME"
      action = "ANONYMIZE"
    }
    pii_entities_config {
      type   = "EMAIL"
      action = "ANONYMIZE"
    }
    pii_entities_config {
      type   = "AGE"
      action = "ANONYMIZE"
    }
  }

  topic_policy_config {
    topics_config {
      name       = "ProhibitedAssessmentCompletion"
      definition = "Requests for the agent to directly complete a graded assessment on a student's behalf in violation of academic-integrity policy."
      examples   = ["Write my entire graded essay and submit it as mine.", "Give me the exam answer key."]
      type       = "DENY"
    }
  }

  tags = local.base_tags
}

resource "aws_bedrock_guardrail_version" "agent" {
  guardrail_arn = aws_bedrock_guardrail.agent.guardrail_arn
  description   = "Initial published version - ${var.environment}"
}

#==============================================================================
# SECURITY: Cognito + IdP federation (parity: security.yaml)
# custom:edu_role carries student | guardian | educator | counselor | administrator
#==============================================================================

resource "aws_cognito_user_pool" "main" {
  name                     = local.name
  mfa_configuration        = "OPTIONAL"
  auto_verified_attributes = []

  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  password_policy {
    minimum_length    = 14
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }

  schema {
    name                = "edu_role"
    attribute_data_type = "String"
    mutable             = true
    string_attribute_constraints {
      min_length = "1"
      max_length = "32"
    }
  }
  schema {
    name                = "under_13"
    attribute_data_type = "String"
    mutable             = true
  }
  schema {
    name                = "rights_transferred"
    attribute_data_type = "String"
    mutable             = true
  }

  tags = local.base_tags
}

# Institution IdP (SAML/OIDC). Customer owns the IdP group -> edu_role mapping
# and the age-of-majority / FERPA rights-transfer logic.
resource "aws_cognito_identity_provider" "institution" {
  count         = local.has_idp ? 1 : 0
  user_pool_id  = aws_cognito_user_pool.main.id
  provider_name = "InstitutionIdP"
  provider_type = var.idp_provider_type

  provider_details = var.idp_provider_type == "SAML" ? {
    MetadataURL = var.idp_metadata_url
  } : {
    oidc_issuer      = var.idp_metadata_url
    authorize_scopes = "openid email profile"
  }

  attribute_mapping = {
    email                         = "email"
    "custom:edu_role"             = "edu_role"
    "custom:under_13"             = "under_13"
    "custom:rights_transferred"   = "rights_transferred"
  }
}

resource "aws_cognito_user_pool_client" "main" {
  name                                 = "${local.name}-client"
  user_pool_id                         = aws_cognito_user_pool.main.id
  generate_secret                      = true
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  supported_identity_providers         = local.has_idp ? ["InstitutionIdP"] : ["COGNITO"]
  callback_urls                        = ["https://localhost/callback"]
  explicit_auth_flows                  = ["ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH"]
}

resource "aws_cognito_identity_pool" "main" {
  identity_pool_name               = replace("${local.name}", "-", "_")
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id     = aws_cognito_user_pool_client.main.id
    provider_name = aws_cognito_user_pool.main.endpoint
  }
  tags = local.base_tags
}

#==============================================================================
# SECURITY: least-privilege agent execution role (parity: security.yaml)
# No direct system-of-record credentials - SoR access is brokered by Layer 3
# with short-lived scoped tokens. Append-only audit = PutItem only.
#==============================================================================

resource "aws_iam_role" "agent_execution" {
  name = "${local.name}-agent-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = ["lambda.amazonaws.com", "states.amazonaws.com", "bedrock.amazonaws.com"]
      }
      Action = "sts:AssumeRole"
    }]
  })
  managed_policy_arns = [
    "arn:${local.partition}:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  ]
  tags = local.base_tags
}

resource "aws_iam_role_policy" "agent_bedrock" {
  name = "BedrockInvokeWithGuardrail"
  role = aws_iam_role.agent_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "InvokeClaudeInAccount"
      Effect   = "Allow"
      Action   = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:ApplyGuardrail"]
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy" "agent_audit_append_only" {
  name = "AppendOnlyAudit"
  role = aws_iam_role.agent_execution.id
  # Append-only: PutItem only. UpdateItem / DeleteItem intentionally absent.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "AppendAuditOnly"
      Effect   = "Allow"
      Action   = "dynamodb:PutItem"
      Resource = aws_dynamodb_table.audit.arn
    }]
  })
}

resource "aws_iam_role_policy" "agent_secrets_kms" {
  name = "ScopedSecretsAndKms"
  role = aws_iam_role.agent_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadConnectorSecrets"
        Effect   = "Allow"
        Action   = "secretsmanager:GetSecretValue"
        Resource = "arn:${local.partition}:secretsmanager:${var.aws_region}:${local.account_id}:secret:edu-agents/${var.environment}/*"
      },
      {
        Sid      = "UseEnvCmk"
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:GenerateDataKey"]
        Resource = aws_kms_key.env.arn
      }
    ]
  })
}

#==============================================================================
# DATA: append-only audit table (parity: data.yaml)
# Append-only enforced at the principal (PutItem-only above). PITR enabled.
#==============================================================================

resource "aws_dynamodb_table" "audit" {
  name         = "${local.name}-audit"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "sk"
    type = "S"
  }
  attribute {
    name = "outcome" # ALLOW | DENY | PENDING_APPROVAL | ERROR
    type = "S"
  }

  global_secondary_index {
    name            = "outcome-index"
    hash_key        = "outcome"
    range_key       = "sk"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.env.arn
  }
  deletion_protection_enabled = true

  tags = merge(local.base_tags, { "edu:dataclass" = "audit-append-only" })
}

#==============================================================================
# DATA: HITL approval-queue table (parity: data.yaml)
# The waitForTaskToken gate writes a PENDING item; a verified reviewer identity
# must be bound before the scoped write token is minted.
#==============================================================================

resource "aws_dynamodb_table" "hitl_queue" {
  name         = "${local.name}-hitl-queue"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"

  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "status" # PENDING | APPROVED | REJECTED | EXPIRED
    type = "S"
  }
  attribute {
    name = "createdAt"
    type = "S"
  }

  global_secondary_index {
    name            = "status-index"
    hash_key        = "status"
    range_key       = "createdAt"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expiresAt"
    enabled        = true
  }
  point_in_time_recovery {
    enabled = true
  }
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.env.arn
  }
  deletion_protection_enabled = true

  tags = merge(local.base_tags, { "edu:dataclass" = "hitl-queue" })
}

#==============================================================================
# DATA: S3 Object Lock WORM store (parity: data.yaml)
# COMPLIANCE mode - write-once, read-many; retention cannot be shortened.
#==============================================================================

resource "aws_s3_bucket" "worm" {
  bucket              = "${local.name}-worm-${local.account_id}"
  object_lock_enabled = true
  tags                = merge(local.base_tags, { "edu:dataclass" = "worm-records" })
}

resource "aws_s3_bucket_versioning" "worm" {
  bucket = aws_s3_bucket.worm.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_object_lock_configuration" "worm" {
  bucket = aws_s3_bucket.worm.id
  rule {
    default_retention {
      mode = "COMPLIANCE"
      days = var.worm_retention_days
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "worm" {
  bucket = aws_s3_bucket.worm.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.env.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "worm" {
  bucket                  = aws_s3_bucket.worm.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "worm" {
  bucket = aws_s3_bucket.worm.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyInsecureTransport"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [aws_s3_bucket.worm.arn, "${aws_s3_bucket.worm.arn}/*"]
      Condition = { Bool = { "aws:SecureTransport" = "false" } }
    }]
  })
}

#==============================================================================
# GATEWAY topology-as-IaC (parity: agentcore-gateway.yaml)
# AgentCore Gateway / Identity resource types are not yet first-class in the
# AWS provider; the target topology + authorizer config are recorded in SSM and
# reconciled into AgentCore Gateway by the deployment pipeline / a custom
# provisioner, exactly as in the CloudFormation parity stack.
#==============================================================================

locals {
  gateway_targets = {
    sis  = { desc = "SIS (PowerSchool/Banner/Workday Student)", read = "sis.get_student_schedule,sis.check_application_status", write = "sis.create_advising_case,sis.write_extracted_document", consequential = "sis.write_extracted_document" }
    lms  = { desc = "LMS (Canvas/Blackboard/Schoology/Moodle/D2L)", read = "lms.get_course_roster,lms.get_assignment", write = "lms.update_assignment_due_date,lms.post_announcement", consequential = "lms.post_announcement" }
    crm  = { desc = "CRM (Slate/Salesforce EDU)", read = "crm.get_contact,crm.check_inquiry_status", write = "crm.create_advising_case,crm.draft_family_message", consequential = "crm.draft_family_message" }
    itsm = { desc = "ITSM (ServiceNow/Jira)", read = "itsm.get_ticket_status,itsm.search_knowledge", write = "itsm.submit_it_ticket", consequential = "" }
  }
}

resource "aws_ssm_parameter" "gateway_target" {
  for_each    = local.gateway_targets
  name        = "/edu-agents/${var.environment}/gateway/targets/${each.key}"
  type        = "String"
  description = "AgentCore Gateway target spec - ${each.key} (system of record)."
  value = jsonencode({
    system        = each.key
    desc          = each.value.desc
    read          = each.value.read
    write         = each.value.write
    consequential = each.value.consequential
  })
  tags = local.base_tags
}

resource "aws_ssm_parameter" "gateway_authorizer" {
  name        = "/edu-agents/${var.environment}/gateway/authorizer"
  type        = "String"
  description = "Inbound authorizer wiring (deny-by-default; role from custom:edu_role)."
  value = jsonencode({
    type          = "cognito"
    userPoolId    = aws_cognito_user_pool.main.id
    clientId      = aws_cognito_user_pool_client.main.id
    roleClaim     = "custom:edu_role"
    denyByDefault = true
  })
  tags = local.base_tags
}

#==============================================================================
# AGENT SERVICE - native path: Step Functions + waitForTaskToken HITL gate
# (parity: agent-service.yaml). Lambda function resources are omitted here for
# brevity in the reference; wire packaged artifacts from lambda_code_bucket.
#==============================================================================

resource "aws_iam_role" "sfn" {
  count = local.is_native ? 1 : 0
  name  = "${local.name}-${var.agent_id}-sfn-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "states.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
  tags = local.base_tags
}

# Specialist agent state machine. The HitlApprovalGate is the waitForTaskToken
# state - it suspends until a verified reviewer approval resumes it. No path to
# Finalize bypasses the gate for a consequential action (the bright line).
resource "aws_sfn_state_machine" "agent" {
  count    = local.is_native ? 1 : 0
  name     = "${local.name}-${var.agent_id}"
  role_arn = aws_iam_role.sfn[0].arn
  tags     = merge(local.base_tags, { "edu:agent" = var.agent_id })

  definition = jsonencode({
    Comment = "EDU specialist agent - native path with waitForTaskToken HITL gate"
    StartAt = "IntakeRetrieveDraft"
    States = {
      IntakeRetrieveDraft = {
        Type    = "Task"
        Comment = "Intake, gateway-brokered retrieval, Bedrock draft/analyze (Guardrail applied, PII masked)"
        Resource = "arn:${local.partition}:states:::lambda:invoke"
        Parameters = { "FunctionName" = "${local.name}-${var.agent_id}-core" }
        Next    = "PolicyComplianceGate"
      }
      PolicyComplianceGate = {
        Type     = "Task"
        Comment  = "Grounding + bright-line classification"
        Resource = "arn:${local.partition}:states:::lambda:invoke"
        Parameters = { "FunctionName" = "${local.name}-${var.agent_id}-policy-gate" }
        Next     = "Routing"
      }
      Routing = {
        Type    = "Choice"
        Comment = "clean -> HITL gate; revise -> one bounded revision; prohibited -> escalate"
        Choices = [
          { Variable = "$.routing.decision", StringEquals = "REVISE", Next = "IntakeRetrieveDraft" },
          { Variable = "$.routing.decision", StringEquals = "PROHIBITED", Next = "Escalate" }
        ]
        Default = "HitlApprovalGate"
      }
      HitlApprovalGate = {
        Type           = "Task"
        Comment        = "Suspend until a verified reviewer approves; binds reviewer identity before resume"
        Resource       = "arn:${local.partition}:states:::lambda:invoke.waitForTaskToken"
        TimeoutSeconds = 259200
        Parameters = {
          "FunctionName" = "${local.name}-${var.agent_id}-hitl-enqueue"
          "Payload" = {
            "taskToken.$"  = "$$.Task.Token"
            "draft.$"      = "$.draft"
            "compliance.$" = "$.compliance"
            "requester.$"  = "$.requester"
          }
        }
        Next = "Finalize"
        Catch = [
          { ErrorEquals = ["States.Timeout"], Next = "Escalate" },
          { ErrorEquals = ["ApprovalRejected"], Next = "Escalate" }
        ]
      }
      Finalize = {
        Type     = "Task"
        Comment  = "Reached only after verified approval - mints scoped token, performs action, writes ALLOW audit"
        Resource = "arn:${local.partition}:states:::lambda:invoke"
        Parameters = { "FunctionName" = "${local.name}-${var.agent_id}-finalize" }
        End      = true
      }
      Escalate = {
        Type    = "Succeed"
        Comment = "Routed to a human; no autonomous consequential action taken"
      }
    }
  })
}

# CONTAINER path (parity: agent-service.yaml): AgentCore Runtime resource types
# are not yet first-class; the container contract (ARM64, /invocations, /ping,
# port 8080) is recorded in SSM and reconciled by the deployment pipeline.
resource "aws_ssm_parameter" "container_contract" {
  count       = local.is_native ? 0 : 1
  name        = "/edu-agents/${var.environment}/runtime/${var.agent_id}"
  type        = "String"
  description = "AgentCore Runtime container contract for this agent."
  value = jsonencode({
    agentId     = var.agent_id
    mode        = "container"
    image       = var.container_image_uri
    arch        = "arm64"
    port        = 8080
    invokePath  = "/invocations"
    healthPath  = "/ping"
    roleArn     = aws_iam_role.agent_execution.arn
    guardrailId = aws_bedrock_guardrail.agent.guardrail_id
  })
  tags = local.base_tags
}
