import getpass
import sys

from duniterpy import __version__

from duniterpy.key import AsciiArmor, SigningKey

# CONFIG #######################################

CLEARTEXT_AA_MESSAGE_PATH = '/tmp/duniter_cleartext_aa_message.txt'

################################################

if __name__ == '__main__':
    # prompt hidden user entry
    salt = getpass.getpass("Enter your passphrase (salt): ")

    # prompt hidden user entry
    password = getpass.getpass("Enter your password: ")

    # init SigningKey instance
    signing_key = SigningKey.from_credentials(salt, password)

    # Enter the multi-line message (stop with Ctrl-D below last line to end)
    print("Enter your message (Ctrl-D below last line to end):")
    message = sys.stdin.read()

    print("Message signed by puplic key : {pubkey}".format(pubkey=signing_key.pubkey))

    comment = "generated by Duniterpy {0}".format(__version__)
    # Dash escape the message and sign it
    aa_cleartext_message = AsciiArmor.create(message, None, [signing_key], None, signatures_comment=comment)

    # Save cleartext ascii armor message in a file
    with open(CLEARTEXT_AA_MESSAGE_PATH, 'w') as file_handler:
        file_handler.write(aa_cleartext_message)

    print("Cleartext Ascii Armor Message saved in file ./{0}".format(CLEARTEXT_AA_MESSAGE_PATH))
