import pika
import time
import sys

RABBITMQ = "95.217.184.176"
credentials = pika.PlainCredentials('admin', 'iYm8SXYAy6rSPW4umRFS')

def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=sys.argv[1])
    channel.basic_consume(queue=sys.argv[1],
                      auto_ack=True,
                      on_message_callback=callback)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

if __name__ == "__main__":
    consume()