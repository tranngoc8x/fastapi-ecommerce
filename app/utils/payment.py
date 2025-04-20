import uuid
from typing import Dict, Optional

from app.models.order import Order


class PaymentProcessor:
    """
    Mock payment processor for demonstration purposes.
    In a real application, this would integrate with a payment gateway like Stripe, PayPal, etc.
    """
    
    @staticmethod
    def process_payment(order: Order, payment_method: str, card_info: Optional[Dict] = None) -> str:
        """
        Process a payment for an order.
        
        Args:
            order: The order to process payment for
            payment_method: The payment method (e.g., "credit_card", "paypal")
            card_info: Optional card information for credit card payments
            
        Returns:
            payment_id: A unique payment ID
        """
        # In a real application, this would call a payment gateway API
        # For demonstration, we just generate a random payment ID
        payment_id = f"pay_{uuid.uuid4().hex}"
        
        # Simulate payment processing
        print(f"Processing payment for order {order.id} with {payment_method}")
        print(f"Amount: ${order.total_amount:.2f}")
        
        if payment_method == "credit_card" and card_info:
            # Validate card info and process payment
            print(f"Processing credit card payment with card ending in {card_info.get('last4', 'XXXX')}")
        
        # Return a payment ID that would come from the payment gateway
        return payment_id
