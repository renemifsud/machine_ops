#!/usr/bin/env python
import pika, sys, argparse, threading


class Publisher(threading.Thread):
    def send(self, body, q):
        url = "95.217.184.176"
        credentials = pika.PlainCredentials("admin", "iYm8SXYAy6rSPW4umRFS")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(url, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=q)

        channel.basic_publish(exchange="", routing_key=q, body=body)
        print(f"[x] Sent '{body}'")
        connection.close()

    def __init__(self, body, q):
        self.body = body

        print(" [*] Sending messages. To exit press CTRL+C")
        while True:
            self.send(body, q)
