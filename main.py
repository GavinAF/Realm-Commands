#!/usr/bin/env python

from __future__ import print_function

import getpass
import sys
import re

import time

import sqlite3
import threading

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound, PlayerPositionAndLookPacket

import json

from conf import options

def main():

    my_pos = {
        0 : "",
        1 : "",
        2 : ""
    }


    def teleport(x, name):
        if len(x) != 2:

            packet = serverbound.play.ChatPacket()
            packet.message = ("/msg %s Failed! - Usage: !tp NAME" % (name))
            connection.write_packet(packet)

            print("Teleport Failed - Missing Arguments :(")
            return

        packet = serverbound.play.ChatPacket()
        packet.message = ("/tp %s %s" % (name, x[1]))
        connection.write_packet(packet)
        print("Teleported %s to %s" % (name, x[1]))

    def sethome(x, name):
        # Check valid arguments
        # if len(x) != 4:

        #     packet = serverbound.play.ChatPacket()
        #     packet.message = ("/msg %s Failed! - Usage: !sethome X Y Z" % (name))
        #     connection.write_packet(packet)

        #     print("SetHome Failed - Missing Arguments")
        #     return

        packet = serverbound.play.ChatPacket()
        packet.message = ("/tp %s" % (name))
        connection.write_packet(packet)

        time.sleep(.5)

        packet = serverbound.play.ChatPacket()
        packet.message = ("/tp ~ ~ ~")
        connection.write_packet(packet)

        # Connect to db and set || re-set home coords
        dbcon = sqlite3.connect("mc_server.db")
        cur = dbcon.cursor()

        command1 = """ insert or replace into homes (home_id, user, x, y, z) values
                        ((select home_id from homes where user = ?), ?, ?, ?, ?) """

        cur.execute(command1, (str(name), str(name), str(my_pos[0]), str(my_pos[1]), str(my_pos[2]), ))
        dbcon.commit()

        print("Set home location to: %s, %s, %s" % (str(my_pos[0]), str(my_pos[1]), str(my_pos[2])))

    def home(name):
        dbcon = sqlite3.connect("mc_server.db")
        cur = dbcon.cursor()

        command1 = """ SELECT * FROM homes WHERE user = ? """
        cur.execute(command1, [name])
        
        row = cur.fetchall()

        if len(row) != 1:

            packet = serverbound.play.ChatPacket()
            packet.message = ("/msg %s Failed! - No Home Set :(" % (name))
            connection.write_packet(packet)

            print("Home Failed - No Home Set")
            return

        row = row[0]

        packet = serverbound.play.ChatPacket()
        packet.message = ("/tp %s %s %s %s" % (name, row[2], row[3], row[4]))
        connection.write_packet(packet)

        dbcon.close()

        print("Teleported %s to their home" % (name))

    if options['offline']:
        print("Connecting in offline mode...")
        connection = Connection(
            options['address'], options['port'], username=options['username'])
    else:
        # Connect client to server
        auth_token = authentication.AuthenticationToken()
        try:
            auth_token.authenticate(options['email'], options['password'])
        except YggdrasilError as e:
            print(e)
            sys.exit()
        print("Logging in as %s..." % auth_token.username)
        connection = Connection(
            options['address'], options['port'], auth_token=auth_token)

    def handle_join_game(join_game_packet):
        print('Client Connected.')

    connection.register_packet_listener(
        handle_join_game, clientbound.play.JoinGamePacket)


    # Get name/message from json packet and print if not from client
    def print_chat(chat_packet):

        if chat_packet.field_string('position') == "CHAT":
            chat_dict = json.loads(chat_packet.json_data)

            name = chat_dict['with'][0]['text']
            message = chat_dict['with'][1]

            if name != options['username']:
                print("%s : %s" % (name, message))

            if message[0] == "!":
                x = message.split()

                if x[0] == "!tp":
                    teleport(x, name)
                elif x[0] == "!sethome":
                    sethome(x, name)
                elif x[0] == "!home":
                    home(name)
                else:
                    print("Invalid Command :(")
       
    lock = threading.Lock()
    pos_look = PlayerPositionAndLookPacket.PositionAndLook()

    pos_look_set = threading.Condition(lock)

    def h_position_and_look(packet):
        with lock:
            packet.apply(pos_look)
            pos_look_set.notify_all()

            index = 0

            for x in (pos_look.position,):
                for y in x:
                    my_pos[index] = int(y)
                    index += 1


    connection.register_packet_listener(h_position_and_look, PlayerPositionAndLookPacket)

    connection.register_packet_listener(
        print_chat, clientbound.play.ChatMessagePacket)

    connection.connect()

    with lock:
        pos_look_set.wait()

    while True:
        try:
            text = input()

            # Respawn client
            if text == "/respawn":
                print("respawning...")
                packet = serverbound.play.ClientStatusPacket()
                packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
                connection.write_packet(packet)

            # Shutdown client
            elif text == "/stopclient":
                print("Shutting Down!")
                sys.exit()

            # Send regular message
            else:
                packet = serverbound.play.ChatPacket()
                packet.message = text
                connection.write_packet(packet)

        # Handle exit keystroke
        except KeyboardInterrupt:
            print("Shutting Down!")
            sys.exit()


if __name__ == "__main__":
    main()