from common.util import *
from collections import namedtuple
import re

Session = namedtuple('Session', ['client', 'chunk'])

def encodeSession(session):
    return [session.client, session.chunk]
def decodeSession(session_encoding):
    return Session(session_encoding[0], session_encoding[1])

# fromCSVs: (Sequenceof (and String PathToSomeFile)) -> (Sequenceof Session)
def fromCSVs(file_list):
    client_file_pattern = "/cb(_[^/]+.csv)$"
    # is_client_file: String -> Boolean
    def is_client_file(path):
        return True if re.search(client_file_pattern, path) else False
    def client_file_to_session(client_path):
        chunk_path = re.sub(client_file_pattern, "/vid\\1", client_path)
        return Session(client_path, chunk_path)
    client_files = filter(is_client_file, file_list)
    return map(client_file_to_session, client_files)

# mapSessionsIn: (Session -> A) PathToSomeDirectory -> (Sequenceof A)
def mapSessionsIn(f, path):
    all_files = listDir(path)
    sessions = fromCSVs(all_files)
    return map(f, sessions)

# filterSessionsIn: (Session -> Boolean) PathToSomeDirectory -> (Sequenceof Session)
def filterSessionsIn(f, path):
    return filter(f, mapSessionsIn(identity, path))
