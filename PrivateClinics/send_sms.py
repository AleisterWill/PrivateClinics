from twilio.rest import Client

account_sid = 'AC4d34b6d76ac9dd53cfab2bbab824240e'
auth_token = '4f99520c1ffbbba30485bb4911d921f3'
client = Client(account_sid, auth_token)


def send(body, to):
    message = client.messages.create(
        body=body,
        from_='+14026736552',
        to=to
    )

