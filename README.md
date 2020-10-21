
# Realm Commands
Teleportation & home system for non-op players on a Minecraft Realm server

## Contents
1. [Dependencies](#dependencies)
2. [Installation and Usage](#installation-and-usage)
3. [Commands](#commands)

## Dependencies

### Required
* [Python](http://python.org/) 3
* [future](http://python-future.org)
* [Spare Minecraft Account](http://minecraft.net)
* requests
	```
	pip install requests
	```
* cryptograpghy
	```
	pip install cryptograpghy
	```
* pynbt
	```
	pip install pynbt
	```

## Installation and Usage

1.  Clone this repository into an empty directory:
    ```
    git clone https://github.com/GavinAF/Realm-Commands
    cd Realm-Commands
    ```

2.  Enter your information into `conf.py`

3.  Invite spare account to Realm

4.  OP/Promote the account using the Realm's control panel

5.  Accept invite on spare account through Minecraft client

6.  Run `main.py` to start the bot:
    ```
    python main.py
    ```

7. Recommend putting bot account into spectator mode

## Commands
All commands have a prefix of !

* Teleport
	```
	!tp [name]
	```
* Set Home
	```
	!sethome
	```
* Home
	```
	!home
	```

