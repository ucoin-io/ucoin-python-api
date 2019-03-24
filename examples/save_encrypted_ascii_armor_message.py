import getpass
from duniterpy import __version__

from duniterpy.key import AsciiArmor, SigningKey

# CONFIG #######################################

ENCRYPTED_AA_MESSAGE_PATH = '/tmp/duniter_aa_encrypted_message.txt'

################################################

if __name__ == '__main__':
    # Ask public key of the recipient
    pubkeyBase58 = input("Enter public key of the message recipient: ")

    # prompt hidden user entry
    salt = getpass.getpass("Enter your passphrase (salt): ")

    # prompt hidden user entry
    password = getpass.getpass("Enter your password: ")

    # init SigningKey instance
    signing_key = SigningKey.from_credentials(salt, password)

    # Enter the message
    message = input("Enter your message: ")

    print("Message signed by puplic key : {pubkey}".format(pubkey=signing_key.pubkey))

    comment = "generated by Duniterpy {0}".format(__version__)
    # Encrypt the message, only the recipient secret key will be able to decrypt the message
    encrypted_message = AsciiArmor.create(message, pubkeyBase58, [signing_key], message_comment=comment,
                                          signatures_comment=comment)

    # Save encrypted message in a file
    with open(ENCRYPTED_AA_MESSAGE_PATH, 'w') as file_handler:
        file_handler.write(encrypted_message)

    print("Encrypted Ascii Armor Message saved in file {0}".format(ENCRYPTED_AA_MESSAGE_PATH))
