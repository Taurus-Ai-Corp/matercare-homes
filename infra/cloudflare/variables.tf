variable "cloudflare_api_token" {
  description = "Cloudflare API token with Zone:Edit + DNS:Edit permissions"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare Account ID (found in the dashboard sidebar)"
  type        = string
}

variable "google_dkim_public_key" {
  description = "DKIM public key from Google Workspace Admin > Gmail > Authenticate email (just the p= value)"
  type        = string
  sensitive   = true
  default     = "REPLACE_WITH_DKIM_KEY_FROM_GOOGLE_WORKSPACE"
}
