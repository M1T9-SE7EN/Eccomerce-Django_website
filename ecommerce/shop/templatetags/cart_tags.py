from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_item_count(context):
    """Return total number of items in the shopping cart stored in session."""
    request = context.get('request')
    if not request:
        return 0
    cart = request.session.get('cart', {})
    # values are quantities
    try:
        return sum(int(qty) for qty in cart.values())
    except Exception:
        return 0
