import pika
import time

RABBITMQ = "95.217.184.176"
credentials = pika.PlainCredentials('admin', 'iYm8SXYAy6rSPW4umRFS')

def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(2)

if __name__ == "__main__":
    consume()