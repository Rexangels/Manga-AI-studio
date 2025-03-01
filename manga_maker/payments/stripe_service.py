# payments/stripe_service.py
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

class StripeService:
    @staticmethod
    def create_checkout_session(user, tier):
        tier_pricing = {
            'BASIC': {'price': 999, 'name': 'Basic Subscription'},
            'PRO': {'price': 1999, 'name': 'Pro Subscription'},
            'ENTERPRISE': {'price': 4999, 'name': 'Enterprise Subscription'}
        }
        
        price_data = tier_pricing[tier]
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': price_data['name'],
                    },
                    'unit_amount': price_data['price'],
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=settings.BASE_URL + '/payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.BASE_URL + '/payment/cancel',
            client_reference_id=str(user.id)
        )
        
        return session.id