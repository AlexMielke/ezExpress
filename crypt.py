# ----------------------------------------------------------------------------------------------------------------- #
# ---  ezExpress v1.0.6                                                                                         --- #
# ---                                                                                                           --- #
# ---  Modul : crypt                                                                                            --- #
# ---                                                                                                           --- #
# ---  Ausgelagerte Methode zur Verschlüsselung des Userpasswortes zur Anmeldung am Emailserver                 --- #
# ---                                                                                                           --- #
# ---                                                                                                           --- #
# ---  Das Modul wurde in Python (Version 3.8.6) geschrieben. Folgende externe Bibliotheken wurden benutzt:     --- #
# ---                                                                                                           --- #
# ---  - cryptography      (https://github.com/pyca/cryptography)                                               --- #
# ---                      (Lizenz: http://www.apache.org/licenses/LICENSE-2.0)                                 --- #
# ---                                                                                                           --- #
# ---  Lizenzinformation:                                                                                       --- #
# ---                                                                                                           --- #
# ---  Das Programm ezExpress wird under der Apache License, Version 2.0 veröffentlicht.                        --- #
# ---  (http://www.apache.org/licenses/LICENSE-2.0.html)                                                        --- #
# ---                                                                                                           --- #
# ---  Bei Fragen, gefundenen Fehlern oder Verbesserungsvorschlägen bitte eine Email schreiben.                 --- #
# ---                                                                                                           --- #
# ---  mailto: alexandermielke@t-online.de                                                                      --- #
# ---                                                                                                           --- #
# ---  Alexander Mielke, November 2020                                                                          --- #
# ---                                                                                                           --- #
# ----------------------------------------------------------------------------------------------------------------- #

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

############################## Create Key ############################

password = "mysecretpassword"
passnew = password.encode()
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"staticsalt", iterations=100000, backend=default_backend())
key = base64.urlsafe_b64encode(kdf.derive(passnew))
f = Fernet(key)

############################## Encode PW #############################


def encode(message):
    messnew = message.encode()
    encrypted = f.encrypt(messnew)
    return encrypted.decode()

############################## Decode PW #############################


def decode(encrypted):
    decrypted = f.decrypt(encrypted.encode())
    return decrypted.decode()
