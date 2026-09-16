"""
AI shopping assistant used by the header's "Ask AI" search feature.

Uses the Gemini API when GEMINI_API_KEY is configured; otherwise falls back
to simple keyword matching against the product catalog, so the feature works
end-to-end even with zero external setup.
"""
from django.conf import settings


def _keyword_fallback(query, products):
    query_words = [w.lower() for w in query.split() if len(w) > 2]
    scored = []
    for product in products:
        haystack = f"{product.name} {product.description} {product.category.name}".lower()
        score = sum(1 for word in query_words if word in haystack)
        if score > 0:
            scored.append((score, product))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:6]]


def _serialize(products):
    return [
        {
            'id': p.id,
            'name': p.name,
            'price': str(p.current_price),
            'original_price': str(p.price) if p.discount_price else None,
            'image': p.image,
            'url': p.get_absolute_url(),
            'rating': str(p.rating),
        }
        for p in products
    ]


def get_ai_recommendations(query, products):
    """
    Returns {'message': str, 'products': [ {...}, ... ], 'source': 'gemini'|'fallback'}
    """
    message = None
    source = 'fallback'

    gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
    if gemini_key:
        try:
            from google import genai

            client = genai.Client(api_key=gemini_key)
            categories = sorted(set(products.values_list('category__name', flat=True)))
            catalog_summary = ", ".join(categories)

            prompt = (
                "You are a friendly shopping assistant for an online store called "
                f"ShopinglyX. The store sells products in these categories: {catalog_summary}. "
                f"A customer said: \"{query}\". "
                "In one short, warm sentence (max 30 words), tell them what kind of "
                "product to look for and which single category best matches their "
                "need. Do not invent specific product names or prices."
            )
            response = client.models.generate_content(
                model=getattr(settings, 'AI_MODEL', 'gemini-flash-latest'),
                contents=prompt,
            )
            text = (response.text or '').strip()
            if text:
                message = text
                source = 'gemini'
        except Exception:
            # Any network/library/quota issue - fall back silently, don't break the UI.
            message = None
            source = 'fallback'

    top_products = _keyword_fallback(query, products)

    if not top_products:
        top_products = list(products.order_by('-rating')[:6])
        if not message:
            message = "I couldn't find an exact match, but here are some popular picks."
    elif not message:
        message = f"Here's what I found for \"{query}\"."

    return {
        'message': message,
        'products': _serialize(top_products),
        'source': source,
    }
