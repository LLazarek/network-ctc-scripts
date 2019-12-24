from collections import namedtuple

Session = namedtuple('Session', ['client', 'chunk'])

def encodeSession(session):
    return [session.client, session.chunk]
def decodeSession(session_encoding):
    return Session(session_encoding[0], session_encoding[1])
