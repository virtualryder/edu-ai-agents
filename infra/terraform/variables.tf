###############################################################################
# EDU AI Agent Suite - Terraform parity - variables
#
# REFERENCE / ACCELERATOR. Mirrors the CloudFormation parameter surface
# (infra/cloudformation/) so platform teams standardized on Terraform get the
# same resource topology. The customer must harden and validate before
# production use.
###############################################################################

variable "environment" {
  description = "Deployment environment (drives naming, the per-env CMK, and tags)."
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "test", "stage", "prod"], var.environment)
    error_message = "environment must be one of: dev, test, stage, prod."
  }
}

variable "agent_id" {
  description = "Agent to deploy (e.g. 01-concierge - the recommended best-first deployment)."
  type        = string
  default     = "01-concierge"
}

variable "deploy_mode" {
  description = "native = Step Functions + Lambda; container = AgentCore Runtime container."
  type        = string
  default     = "native"
  validation {
    condition     = contains(["native", "container"], var.deploy_mode)
    error_message = "deploy_mode must be 'native' or 'container'."
  }
}

variable "aws_region" {
  description = "Region. Choose to satisfy data-residency / state data-localization obligations and Bedrock + Guardrail availability."
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the agent suite VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "idp_metadata_url" {
  description = "SAML/OIDC metadata document URL for the institution's IdP. Empty to skip federation (early demo)."
  type        = string
  default     = ""
}

variable "idp_provider_type" {
  description = "Federation protocol for the institution IdP."
  type        = string
  default     = "SAML"
  validation {
    condition     = contains(["SAML", "OIDC"], var.idp_provider_type)
    error_message = "idp_provider_type must be 'SAML' or 'OIDC'."
  }
}

variable "lambda_code_bucket" {
  description = "S3 bucket holding packaged Lambda deployment artifacts (native path)."
  type        = string
  default     = ""
}

variable "lambda_code_key_prefix" {
  description = "Key prefix within lambda_code_bucket for this agent's Lambda zips."
  type        = string
  default     = "lambdas"
}

variable "container_image_uri" {
  description = "ECR image URI for the AgentCore Runtime container (ARM64). Required when deploy_mode = container."
  type        = string
  default     = ""
}

variable "worm_retention_days" {
  description = "Object Lock COMPLIANCE retention in days (default ~7 years). Set to your records-retention schedule. COMPLIANCE retention cannot be shortened."
  type        = number
  default     = 2555
}

variable "tags" {
  description = "Additional tags merged onto every resource."
  type        = map(string)
  default     = {}
}
