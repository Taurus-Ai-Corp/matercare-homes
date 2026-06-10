terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# ── Zone ──────────────────────────────────────────────────────────────────────
resource "cloudflare_zone" "matermariahomes" {
  account_id = var.cloudflare_account_id
  zone       = "matermariahomes.com"
  plan       = "free"
}

# ── Vercel — root domain ──────────────────────────────────────────────────────
# proxied = false so Vercel can issue its own TLS certificate via ACME.
# Switch to proxied = true only if you want Cloudflare WAF in front of Vercel.
resource "cloudflare_record" "root_cname" {
  zone_id = cloudflare_zone.matermariahomes.id
  name    = "@"
  type    = "CNAME"
  content = "cname.vercel-dns.com"
  proxied = false
}

resource "cloudflare_record" "www_cname" {
  zone_id = cloudflare_zone.matermariahomes.id
  name    = "www"
  type    = "CNAME"
  content = "cname.vercel-dns.com"
  proxied = false
}

# ── Google Workspace — Mail ───────────────────────────────────────────────────
resource "cloudflare_record" "mx_google" {
  zone_id  = cloudflare_zone.matermariahomes.id
  name     = "@"
  type     = "MX"
  content  = "smtp.google.com"
  priority = 1
}

# ── SPF ───────────────────────────────────────────────────────────────────────
resource "cloudflare_record" "spf" {
  zone_id = cloudflare_zone.matermariahomes.id
  name    = "@"
  type    = "TXT"
  content = "v=spf1 include:_spf.google.com ~all"
}

# ── DMARC ─────────────────────────────────────────────────────────────────────
resource "cloudflare_record" "dmarc" {
  zone_id = cloudflare_zone.matermariahomes.id
  name    = "_dmarc"
  type    = "TXT"
  content = "v=DMARC1; p=reject; rua=mailto:dmarc@matermariahomes.com; ruf=mailto:dmarc@matermariahomes.com; adkim=s; aspf=s"
}

# ── DKIM — Google Workspace ───────────────────────────────────────────────────
# Get your DKIM key from Google Workspace Admin:
#   Admin console → Apps → Google Workspace → Gmail → Authenticate email
# Then set var.google_dkim_public_key to the p= value (the long base64 string).
resource "cloudflare_record" "dkim_google" {
  zone_id = cloudflare_zone.matermariahomes.id
  name    = "google._domainkey"
  type    = "TXT"
  content = "v=DKIM1; k=rsa; p=${var.google_dkim_public_key}"
}
