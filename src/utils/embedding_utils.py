def get_combined_text(product):
    """
    Combine the product name and summary description into one string.
    If summary_description is missing or empty, use only the product name.
    """
    product_name = product.get("name", "").strip()
    summary = product.get("description", "").strip()  # Using the English version
    if summary:
        combined_text = f"{product_name}. {summary}"
    else:
        combined_text = product_name
    return combined_text
