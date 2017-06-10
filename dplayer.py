#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#  dodPoker:  a poker server to run automated texas hold'em
#  poker rounds with bots
#  Copyright (C) 2017 wobe-systems GmbH
# -----------------------------------------------------------
# -----------------------------------------------------------
# Configuration
# You need to change the setting according to your environment
gregister_url='http://192.168.0.5:5001'
glocalip_adr='192.168.0.19'

# -----------------------------------------------------------

from flask import Flask, request
from flask_restful import Resource, Api
import sys

from requests import put
import json

app = Flask(__name__)
api = Api(app)

# Web API to be called from the poker manager
class PokerPlayerAPI(Resource):

    ## return bid to caller
    #
    #  Depending on the cards passed to this function in the data parameter,
    #  this function has to return the next bid.
    #  The following rules are applied:
    #   -- fold --
    #   bid < min_bid
    #   bid > max_bid -> ** error **
    #   (bid > min_bid) and (bid < (min_bid+big_blind)) -> ** error **
    #
    #   -- check --
    #   (bid == 0) and (min_bid == 0) -> check
    #
    #   -- call --
    #   (bid == min_bid) and (min_bid > 0)
    #
    #   -- raise --
    #   min_bid + big_blind + x
    #   x is any value to increase on top of the Big blind
    #
    #   -- all in --
    #   bid == max_bid -> all in
    #
    #  @param data : a dictionary containing the following values - example: data['pot']
    #                min_bid   : minimum bid to return to stay in the game
    #                max_bid   : maximum possible bid
    #                big_blind : the current value of the big blind
    #                pot       : the total value of the current pot
    #                board     : a list of board cards on the table as string '<rank><suit>'
    #                hand      : a list of individual hand cards as string '<rank><suit>'
    #
    #                            <rank> : 23456789TJQKA
    #                            <suit> : 's' : spades
    #                                     'h' : hearts
    #                                     'd' : diamonds
    #                                     'c' : clubs
    #
    # @return a dictionary containing the following values
    #         bid  : a number between 0 and max_bid

    def straightFlush(self, cards):
        length = len(cards)
        searchRank = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        cardList = []
        howManyInARow = 0
        for i in range(0, length):
            for j in range(0, 13):
                if cards[i] == searchRank[j]:
                    nextPosition = j +1
                    for k in range(0, length):
                        if cards[k] == searchRank[nextPosition]:
                            nextPosition + 1
                            for k in range(0, length):
                                if cards[k] == searchRank[nextPosition]:
                                    nextPosition + 1
                                    for k in range(0, length):
                                        if cards[k] == searchRank[nextPosition]:
                                            nextPosition + 1
                                            for k in range(0, length):
                                                if cards[k] == searchRank[nextPosition]:
                                                    return True






        return 0


    def __get_bid(self, data):
        whichRound = len(data['board'])

        allCards = data['hand'] + data['board']
        howManyCards = len(allCards)

        searchRank = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        spades = []
        hearts = []
        diamonds = []
        clubs = []





        print(data)

        try:
            for i in range(0, howManyCards):
                if allCards[i][1] == 's':
                    spades.append(allCards[i][1])
                elif allCards[i][1] == 'h':
                    hearts.append(allCards[i][1])
                elif allCards[i][1] == 'd':
                    diamonds.append(allCards[i][1])
                elif allCards[i][1] == 'c':
                    clubs.append(allCards[i][1])

            if len(spades) >= 5:
                if self.straightFlush(self, spades):
                    return data['min_bid'] * 6

            if len(hearts) >= 5:
                if self.straightFlush(self, hearts):
                    return data['min_bid'] * 6

            if len(diamonds) >= 5:
                if self.straightFlush(self, diamonds):
                    return data['min_bid'] * 6

            if len(clubs) >= 5:
                if self.straightFlush(self, clubs):
                    return data['min_bid'] * 6

            #straight flush


            #four of a Kind
            for i in range(0, howManyCards):
                for j in range(0, howManyCards):
                    for k in range(0, howManyCards):
                        for l in range(0, howManyCards):
                            if allCards[l][0] == allCards[k][0]:
                                if allCards[k][0] == allCards[j][0]:
                                    if allCards[j][0] == allCards[i][0]:
                                        return data['min_bid'] * 5

            #full house
            for i in range(0, howManyCards):
                for j in range(0, howManyCards):
                    for k in range(0, howManyCards):
                        if allCards[k][0] == allCards[j][0]:
                            if allCards[j][0] == allCards[i][0]:
                                allCards.pop([i])
                                allCards.pop([j])
                                allCards.pop([k])
                                howManyCards = len(allCards)
                                for i in range(0, howManyCards):
                                    for j in range(1, howManyCards):
                                        if allCards[i][0] == allCards[j][0]:
                                            return data['min_bid'] * 4

            #flush

            # straight


            #three of a kind
            for i in range(0, howManyCards):
                for j in range(0, howManyCards):
                    for k in range(0, howManyCards):
                        if allCards[k][0] == allCards[j][0]:
                            if allCards[j][0] == allCards[i][0]:
                                return data['min_bid'] * 3


            #one pair and two pairs
            for i in range(0, howManyCards):
                for j in range(1, howManyCards):
                    if allCards[i][0] == allCards[j][0]:
                        allCards.pop([i])
                        allCards.pop([j])
                        howManyCards = len(allCards)
                        for k in range(0, howManyCards):
                            for l in range(0, howManyCards):
                                if allCards[k][0] == allCards[l][0]:
                                    return data['min_bid'] * 2
                        return data['min_bid']
        except ValueError:
            return data['min_bid']


        return data['min_bid']
    # dispatch incoming get commands

    def get(self, command_id):

        data = request.form['data']
        data = json.loads(data)

        if command_id == 'get_bid':
            return {'bid': self.__get_bid(data)}
        else:
            return {}, 201

    # dispatch incoming put commands (if any)
    def put(self, command_id):
        return 201


api.add_resource(PokerPlayerAPI, '/dpoker/player/v1/<string:command_id>')

# main function
def main():

    # run the player bot with parameters
    if len(sys.argv) == 4:
        team_name = sys.argv[1]
        api_port = int(sys.argv[2])
        api_url = 'http://%s:%s' % (glocalip_adr, api_port)
        api_pass = sys.argv[3]
    else:
        print("""
DevOps Poker Bot - usage instruction
------------------------------------
python3 dplayer.py <team name> <port> <password>
example:
    python3 dplayer bazinga 40001 x407
        """)
        return 0


    # register player
    r = put("%s/dpoker/v1/enter_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass':api_pass}).json()
    if r != 201:
        raise Exception('registration failed: probably wrong team name')

    else:
        print('registration successful')

    try:
        app.run(host='0.0.0.0', port=api_port, debug=False)
    finally:
        put("%s/dpoker/v1/leave_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass': api_pass}).json()
# run the main function
if __name__ == '__main__':
    main()


