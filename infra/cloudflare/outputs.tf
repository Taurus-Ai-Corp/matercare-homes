output "nameservers" {
  description = "Cloudflare nameservers — update these at Squarespace registrar"
  value       = cloudflare_zone.matermariahomes.name_servers
}

output "zone_id" {
  description = "Cloudflare Zone ID"
  value       = cloudflare_zone.matermariahomes.id
}
