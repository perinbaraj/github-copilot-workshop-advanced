import pika
import json
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    # SECURITY ISSUE: Hardcoded credentials
    smtp_host = os.getenv('SMTP_HOST', 'smtp.mailtrap.io')
    smtp_port = int(os.getenv('SMTP_PORT', 2525))
    smtp_user = os.getenv('SMTP_USER', 'your_user')
    smtp_password = os.getenv('SMTP_PASSWORD', 'your_password')
    
    try:
        # PERFORMANCE ISSUE: Creating new connection for each email
        msg = MIMEMultipart()
        msg['From'] = 'noreply@techmart.com'
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f'Email sent to {to_email}')
        return True
    except Exception as e:
        # CODE QUALITY ISSUE: Poor error handling
        print(f'Failed to send email: {e}')
        return False

def process_order_notification(order_data):
    # PERFORMANCE ISSUE: Synchronous email sending
    user_id = order_data.get('userId')
    order_id = order_data.get('orderId')
    total_amount = order_data.get('totalAmount')
    
    # ARCHITECTURE ISSUE: Should fetch user email from user service
    # For demo, using placeholder
    user_email = f'user{user_id}@example.com'
    
    subject = f'Order Confirmation - Order #{order_id}'
    body = f'''
    <html>
        <body>
            <h2>Order Confirmation</h2>
            <p>Your order #{order_id} has been placed successfully!</p>
            <p>Total Amount: ${total_amount}</p>
            <p>Thank you for shopping with TechMart!</p>
        </body>
    </html>
    '''
    
    send_email(user_email, subject, body)

def main():
    # ARCHITECTURE ISSUE: No retry logic for RabbitMQ connection
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://admin:password123@rabbitmq:5672')
    
    try:
        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        channel = connection.channel()
        
        channel.queue_declare(queue='orders')
        
        def callback(ch, method, properties, body):
            try:
                order_data = json.loads(body)
                print(f'Processing notification for order: {order_data}')
                
                # PERFORMANCE ISSUE: Synchronous processing
                process_order_notification(order_data)
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                # CODE QUALITY ISSUE: No dead letter queue
                print(f'Error processing message: {e}')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='orders', on_message_callback=callback)
        
        print('Notification service started. Waiting for messages...')
        channel.start_consuming()
        
    except Exception as e:
        print(f'Failed to connect to RabbitMQ: {e}')
        # ARCHITECTURE ISSUE: No graceful degradation
        time.sleep(5)
        main()  # Retry

if __name__ == '__main__':
    main()
