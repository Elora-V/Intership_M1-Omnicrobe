#
# Copyright 2022 Sandra Dérozier (INRAE)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os

# Omnicrobe version
VERSION = "0.1"

# Database Informations

#DB_USER = "omi_user"
#DB_PWD = "omi_user"
#DB_NAME = "omnicrobev0long"
#DB_HOST = "localhost"
#DB_PORT = "5432"

DB_USER = "omielo_user"
DB_PWD = "mdp!omielo"
DB_NAME = "omnicrobev0"
DB_HOST = "localhost"
DB_PORT = "5432"

# Link to AlvisIR
URL_ALVISIR = "https://bibliome.migale.inrae.fr/omnicrobe/alvisir/webapi/"

# Directory Informations
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "templates"))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "static"))

