#!/bin/python
#coding: UTF-8
from flask import Flask, url_for, jsonify, request
import csv
import threading
import time
import json
import codecs
import hashlib
# flask webservice fullrest
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
# classificador
from classificador import Classificador

"""
http://blog.luisrei.com/articles/flaskrest.html
http://flask.pocoo.org/docs/0.11/patterns/sqlalchemy/
"""

# fix problemas com cabeçalho HTTP
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

# salva data a cada 60s
def save_data():
    # open file dict json pickle
    try:
        with codecs.open('data.json', 'r', encoding='utf-8') as f:
            fileData = json.load(f)
    except:
        fileData = {}
    while True:
        for key, value in Ws.data.iteritems():
            fileData[key] = value
        # salva data a cada 60s
        with open('data.json',  'w') as f:
            json.dump(fileData, f)

        time.sleep(60)

# Salva users a cada 60s
def save_users():
    # open file dict json pickle
    try:
        with codecs.open('users.json', 'r', encoding='utf-8') as f:
            fileUsers = json.load(f)
    except:
        fileUsers = {}
    while True:
        for key, value in Ws.users.iteritems():
            fileUsers[key] = value
        # salva Users a cada 60s
        with open('users.json',  'w') as f:
            json.dump(fileUsers, f)

        time.sleep(60)

def save_onlineLearning(data, label):
    try:
        with codecs.open("data-onlineLearning.json", 'r', encoding='utf-8') as f:
                fileData = json.load(f)
    except:
        fileData = []

    data.append(label)
    fileData.append(data)

    # salva fileData em json
    with open("data-onlineLearning.json",  'w') as f:
        json.dump(fileData, f)

class Ws:
    try:
        with codecs.open('session.json', 'r', encoding='utf-8') as f:
            countSession = json.load(f)
    except:
        countSession = 0
    # dict dados
    try:
        with codecs.open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
    # dict users
    try:
        with codecs.open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
    except:
        users = {}
    def __init__(self):
        # init flask
        self.app = Flask("UB")
        self.vdebug = True
        # init thread que salva dados
        self.threadData = threading.Thread(target=save_data)
        self.threadData.start()
         # init thread que salva users
        self.threadUsers = threading.Thread(target=save_users)
        self.threadUsers.start()
        # init classificador
        self.classificador = Classificador("data-inicial.json")

        # init routes
        @self.app.route('/')
        def api_root():
            return jsonify({'status': 'Welcome to UB'})

        @self.app.route('/getData', methods = ['GET'])
        @crossdomain(origin='*')
        def api_getData():
            # informaçoes do usuário, para a geração do token unico
            try:
                #
                rWidth = request.args['rWidth']
                #
                rHeight = request.args['rHeight']
                # interações com elementos do tipo A
                countA = request.args['countA']
                # intereções com elementos do tipo B
                countB = request.args['countB']
                # interações com elementos do tipo A
                clickA = request.args['clickA']
                # intereções com elementos do tipo B
                clickB = request.args['clickB']
                # tempo em elementos do tipo A
                timeA = request.args['timeA']
                # tempo em elementos do tipo B
                timeB = request.args['timeB']
                # interva da amostra (default 5s)
                intervalSample = request.args['intervalSample']
                # tempo total na página
                sessionTime = request.args['sessionTime']
                # id da sessão
                sessionId = request.args['sessionId']
                # ident user
                user = request.args['user']

                self.deBug("WidthxHeight: %sx%s"%(rWidth, rHeight))
                # save in data
                Ws.data[sessionId] = {'rWidth':rWidth,'rHeight':rHeight,
                                      'countA':countA,'countB':countB,
                                      'clickA':clickA,'clickB':clickB,
                                      'timeA':timeA,'timeB':timeB,
                                      'intervalSample':intervalSample,
                                      'sessionTime':sessionTime,
                                      'user':user
                                     }
                if user not in Ws.users.keys():
                    Ws.users[user] = {'sessionId': sessionId,
                                      'feedback': "None",
                                      'classe': "None",
                                      'data': []
                                     }
                else:
                    # atualiza apenas a utlima sessão
                    Ws.users[user]['sessionId'] = sessionId
            except:
                self.error("[getData] Falta de parametros ;(")

            return ''

        @self.app.route('/getSessionId', methods = ['GET'])
        @crossdomain(origin='*')
        def api_getSessionId():
            # retorna um id único para esta sessao
            Ws.countSession += 1
            # salva Session em json
            with open('session.json',  'w') as f:
                json.dump(Ws.countSession, f)

            self.deBug('sessionId: %s'%(Ws.countSession))
            #self.deBug('Data: %s'%(self.data))
            return jsonify({'sessionId': Ws.countSession})

        @self.app.route('/createIdentUser', methods = ['GET'])
        @crossdomain(origin='*')
        def api_getIdSessao():
            # retorna um id único para esta sessao
            identUser = hashlib.md5(str(time.time())).hexdigest()
            return jsonify({'identUser': str(identUser)})

        # busca user e sua classificação
        @self.app.route('/getUser', methods = ['GET'])
        @crossdomain(origin='*')
        def api_getUser():
            # acessa dict dos users classificados e verifica se não existe
            # verifica se existe dados referente a este usuário
            # se sim classifica ele salva e envia a resposta
            classe = "None"
            feedback = "NULL"
            pergunta = "NULL"
            dataFormat = []
            try:
                user = request.args['user']
                if user in Ws.users.keys():
                    # existe
                    if Ws.users[user]['classe'] == "None":
                        # não foi classificado.
                        sessionId = Ws.users[user]['sessionId']
                        data = Ws.data[sessionId]
                        self.deBug("[getUser] Tenta classificar user")
                        predict, dataFormat = self.classificador.my_predict(data)
                        if len(predict) > 0:
                            classe = predict[0]
                            feedback = "TRUE"
                            self.deBug("[getUser] Classificado + Feedback")
                        else:
                            # o dado foi descartado ;x o que fazer?
                            # não classifico
                            self.deBug("[getUser] Dado descartado, não foi possivel classificar")
                            pass
                    else:
                        # já classificado
                        # classifica e ve se é igual, se não pergunta
                        sessionId = Ws.users[user]['sessionId']
                        data = Ws.data[sessionId]
                        predict, dataFormat = self.classificador.my_predict(data)
                        if Ws.users[user]['feedback'] != "False":
                            if len(predict) > 0:
                                classe = predict[0]
                                feedback = "TRUE"
                                self.deBug("[getUser] Classificado + Feedback")
                            else:
                                # o dado foi descartado ;x o que fazer?
                                # não classifico
                                self.deBug("[getUser] Dado descartado, não foi possivel classificar")
                                pass
                            if classe != Ws.users[user]['classe'] and classe != 'None':
                                # classes diferentes, pergunta se o usuário gostaria
                                # de testar a outra interface
                                # classe de layout será a antiga
                                self.deBug("[getUser] Classes diferentes + Pergunta")
                                classe = Ws.users[user]['classe']
                                pergunta = "TRUE"
                            else:
                                # classes iguais
                                self.deBug("[getUser] Classes iguais")
                                classe = Ws.users[user]['classe']
                        else:
                            # já classificado e não gostou
                            # deixa no generico ;x
                            classe = "generico"
                    # add nova classe
                    Ws.users[user]['classe'] = classe
                    Ws.users[user]['data'] = dataFormat

                else:
                    # usuário não existe? :@
                    self.error("[getUser] Usuário  não existe")
            except KeyError:
                self.error("[getUser] Falta de parametros ;(")


            return jsonify({'classe': classe,'feedback': feedback, 'pergunta': pergunta})
        # salva feedback
        @self.app.route('/getFeedback', methods = ['GET'])
        @crossdomain(origin='*')
        def api_getFeedback():
            # pega a resposta do feedbak do usuário
            # salva no dict de classificados
            try:
                # value feedback
                value = str(request.args['feedback'])
                # ident user
                user = str(request.args['user'])
                if user in Ws.users.keys():
                    # existe
                    Ws.users[user]['feedback'] = value
                    # Online Learning
                    data = Ws.users[user]['data']
                    classe = Ws.users[user]['classe']
                    if value != "True":
                        # errei! inverte classe
                        if classe == "typeA":
                            classe = "typeB"
                        else:
                            classe = "typeA"
                    # adiciona no classificador os novos dados com Feedback
                    try:
                        self.classificador.cla.partial_fit(data, [classe])
                        save_onlineLearning(data[0], classe)
                    except:
                        self.error("[getFeedback] Falha no partial_fit")
                else:
                    # não existe user :@
                    self.error("[getFeedback] User \"%s\" não existe - value \"%s\""%(user, value))
            except KeyError:
                self.error("Falta de parametros ;(")
            return ''

        # custom error
        @self.app.errorhandler(404)
        @crossdomain(origin='*')
        def not_found(error=None):
            message = {
                    'status': 404,
                    'message': 'Not Found',
            }
            resp = jsonify(message)
            resp.status_code = 404

            return resp

    # start flask
    def run(self):
        self.app.run(host="0.0.0.0", port=5000, threaded=True)
    # deBug
    def deBug(self, value):
        if self.vdebug:
            print '[DEBUG]', value
    # error
    def error(self, value):
        print '[ERROR]', value
