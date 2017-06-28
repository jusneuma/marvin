#!/usr/bin/python
# encoding: utf-8
'''
Licensed under a 3-clause BSD license.
'''

from __future__ import print_function, division
from flask_restful import Api
from flask import Flask, Blueprint, send_from_directory
from flask import session, request, render_template, g, jsonify
import sys
import os
import logging
import flask_profiler
# Marvin imports
from brain.utils.general.general import getDbMachine
from marvin import config, log
from marvin.web.web_utils import updateGlobalSession
from marvin.web.jinja_filters import jinjablue
from marvin.web.error_handlers import errors
from marvin.web.extensions import jsglue, flags, sentry
from marvin.web.settings import ProdConfig, DevConfig, CustomConfig
# Web Views
from marvin.web.controllers.index import index
from marvin.web.controllers.galaxy import galaxy
from marvin.web.controllers.search import search
from marvin.web.controllers.plate import plate
from marvin.web.controllers.images import images
from marvin.web.controllers.users import users
# API Views
from marvin.api.cube import CubeView
from marvin.api.maps import MapsView
from marvin.api.modelcube import ModelCubeView
from marvin.api.plate import PlateView
from marvin.api.rss import RSSView
from marvin.api.spaxel import SpaxelView
from marvin.api.query import QueryView
from marvin.api.general import GeneralRequestsView

# ================================================================================


def create_app(debug=False, local=False, use_profiler=True, object_config=None):

    # ----------------------------------
    # Create App
    marvin_base = os.environ.get('MARVIN_BASE', 'marvin2')
    app = Flask(__name__, static_url_path='/{0}/static'.format(marvin_base))
    api = Blueprint("api", __name__, url_prefix='/{0}/api'.format(marvin_base))
    app.debug = debug

    # Add Marvin Logger
    app.logger.addHandler(log)

    # Turn on debug stuff in config
    if app.debug is True:
        sentry = None
        config.use_sentry = False
        config.add_github_message = False

    # Find which connection to make
    connection = getDbMachine()
    local = (connection == 'local') or local

    # ----------------------------------
    # Set some other variables
    config._inapp = True
    url_prefix = '/marvin2' if local else '/{0}'.format(marvin_base)

    # ----------------------------------
    # Load the appropriate Flask configuration object for debug or production
    if not object_config:
        if app.debug or local:
            app.logger.info('Loading Development Config!')
            object_config = type('Config', (DevConfig, CustomConfig), dict())
        else:
            app.logger.info('Loading Production Config!')
            object_config = type('Config', (ProdConfig, CustomConfig), dict())
    app.config.from_object(object_config)

    # ------------------------------------------
    # Add lib directory as a new static path
    @app.route('/{0}/lib/<path:filename>'.format(marvin_base))
    def lib(filename):
        return send_from_directory(app.config["LIB_PATH"], filename)

    # Register global session update before every request
    @app.before_request
    def global_update():
        ''' updates the global session / config '''
        updateGlobalSession()

    # ----------------------------------
    # Registration
    register_extensions(app, app_base=marvin_base)
    register_api(app, api)
    register_blueprints(app, url_prefix=url_prefix)

    return app


# ================================================================================

def register_api(app, api):
    ''' Register the Flask API routes used '''

    CubeView.register(api)
    MapsView.register(api)
    ModelCubeView.register(api)
    PlateView.register(api)
    RSSView.register(api)
    SpaxelView.register(api)
    GeneralRequestsView.register(api)
    QueryView.register(api)
    app.register_blueprint(api)


def register_extensions(app, app_base=None):
    ''' Register the Flask extensions used '''

    jsglue.JSGLUE_JS_PATH = '/{0}/jsglue.js'.format(app_base)
    jsglue.init_app(app)
    flags.init_app(app)
    if app.config['USE_SENTRY']:
        sentry.init_app(app)

    # Initialize the Flask-Profiler ; see results at localhost:portnumber/app_base/flask-profiler
    if app.config['USE_PROFILER']:
        try:
            flask_profiler.init_app(app)
        except Exception as e:
            pass


def register_blueprints(app, url_prefix=None):
    ''' Register the Flask Blueprints used '''

    app.register_blueprint(index, url_prefix=url_prefix)
    app.register_blueprint(galaxy, url_prefix=url_prefix)
    app.register_blueprint(search, url_prefix=url_prefix)
    app.register_blueprint(plate, url_prefix=url_prefix)
    app.register_blueprint(images, url_prefix=url_prefix)
    app.register_blueprint(users, url_prefix=url_prefix)
    app.register_blueprint(jinjablue)
    app.register_blueprint(errors)
