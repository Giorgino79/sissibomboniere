"""
Context processors for core app.
Makes cart and other data available in all templates.
"""

from .models import Cart


def cart_context(request):
    """
    Add cart information to all templates.
    """
    cart = None
    cart_total_items = 0
    
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
        
        if cart:
            cart_total_items = cart.get_total_items()
    except:
        pass
    
    return {
        'cart': cart,
        'cart_total_items': cart_total_items,
    }