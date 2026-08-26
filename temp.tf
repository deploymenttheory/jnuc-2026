locals {
  categories = [
    "Category 1",
    "Category 2",
    "Category 3"
  ]
}

resource "jamfpro_category" "example" {
  for_each = toset(local.categories)

  name = each.value
}