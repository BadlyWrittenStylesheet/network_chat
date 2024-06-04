# How the protocol is structured, methods and other:

## Structure:
METHOD
PARAM1:sth
PARAM2:sth
...

### So you could do:
KEY_EXCHANGE
DH_BASE:1267
DH_MOD:398
DH_KEY:4539
RSA_KEY:3290

### Raw that would be:
r"KEY_EXCHANGE\nDH_BASE:1267\nDH_MOD:398\nDH_KEY:4539\nRSA_KEY:3290"

## Methods:
- MSG: indicates that its sending a message
- KEY_EXCHANGE: Indicating that its sending keys to exchange
- INFO: for stuff?



# CURRENT EVENTS FOR METHOD=ACTION
- set_username
- send_public_message
- user_join
- **TODO**
- send_private_message
- user_leave
- ...

## Also want to add a secret 'uwu' command, it will use a lib libe uwuipy and well, uwuify messages ;)
