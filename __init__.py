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

from flask import Flask, Blueprint
from flask import url_for
from flask import render_template
from flask import request
from flask import g, jsonify
from omnicrobe_web.config import *
from omnicrobe_web.database import *
from flask_restx import Resource, Api, fields


# Application
app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_url_path='',
            static_folder=STATIC_DIR)
app.debug = True
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

# API
api = Api(app,
          version=VERSION,
          title='Omnicrobe API',
          description='API to access data in Omnicrobe, a reference database of microorganism biodiversity.',
          doc='/api-doc',
          default_label='',
          base_url='/omnicrobe-api.yaml'
)

# Database connexion
conn = None
with app.app_context():
    app.config['postgreSQL_pool'] = psycopg2.pool.SimpleConnectionPool(1,
                                                                       20,
                                                                       user = DB_USER,
                                                                       password = DB_PWD,
                                                                       host = DB_HOST,
                                                                       port = DB_PORT,
                                                                       database = DB_NAME)

    @app.teardown_appcontext
    def close_conn(e):
        db = g.pop('db', None)
        if db is not None:
            app.config['postgreSQL_pool'].putconn(db)

# Home page
@app.route('/index')
def index():
    return render_template('index.html')

# API page
@app.route('/api')
def home_api():
    return render_template('api.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Release page
@app.route('/release')
def release():
    return render_template('release.html')

# Help page
@app.route('/help')
def help():
    return render_template('help.html')

# Demonstration page (@todo)
@app.route('/demo')
def demo():
    return render_template('demo.html')

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Search by Taxon page (habitat)
@app.route('/searchByTaxon/')
@app.route('/searchByTaxon')
def searchByTaxon():
    taxon = request.args.get('taxon', None)
    habitat = request.args.get('habitat', None)
    qps = request.args.get('qps', None)
    sources = request.args.getlist("source", None)
    score = request.args.get('score', None)
    return render_template('searchByTaxon.html', taxon=taxon,
                                                 habitat=habitat,
                                                 qps=qps,
                                                 sources=sources,
                                                 version=VERSION,
                                                 alvisir=URL_ALVISIR,score=score)
# Search by Habitat page
@app.route('/searchByHabitat/')
@app.route('/searchByHabitat')
def searchByHabitat():
    habitat = request.args.get('habitat', None)
    taxon = request.args.get('taxon', None)
    qps = request.args.get('qps', None)
    sources = request.args.getlist("source", None)
    score = request.args.get('score', None)
    return render_template('searchByHabitat.html', habitat=habitat,
                                                   taxon=taxon,
                                                   qps=qps,
                                                   sources=sources,
                                                   version=VERSION,
                                                   alvisir=URL_ALVISIR,score=score)
# Search by Taxon page (phenotype)
@app.route('/searchByTaxonForPhenotype/')
@app.route('/searchByTaxonForPhenotype')
def searchByTaxonForPhenotype():
    taxon = request.args.get('taxon', None)
    phenotype = request.args.get('phenotype', None)
    qps = request.args.get('qps', None)
    score = request.args.get('score', None)
    return render_template('searchByTaxonForPhenotype.html', taxon=taxon,
                                                             phenotype=phenotype,
                                                             qps=qps,
                                                             version=VERSION,
                                                             alvisir=URL_ALVISIR,score=score)
# Search by Phenotype page
@app.route('/searchByPhenotype/')
@app.route('/searchByPhenotype')
def searchByPhenotype():
    phenotype = request.args.get('phenotype', None)
    taxon = request.args.get('taxon', None)
    qps = request.args.get('qps', None)
    score = request.args.get('score', None)
    return render_template('searchByPhenotype.html', phenotype=phenotype,
                                                     taxon=taxon, qps=qps,
                                                     version=VERSION,
                                                     alvisir=URL_ALVISIR,score=score)
# Search by Taxon page (use)
@app.route('/searchByTaxonForUse/')
@app.route('/searchByTaxonForUse')
def searchByTaxonForUse():
    taxon = request.args.get('taxon', None)
    use = request.args.get('use', None)
    qps = request.args.get('qps', None)
    score = request.args.get('score', None)
    return render_template('searchByTaxonForUse.html', taxon=taxon, use=use,
                                                       qps=qps, version=VERSION,
                                                       alvisir=URL_ALVISIR,score=score)
# Search by Use page
@app.route('/searchByUse/')
@app.route('/searchByUse')
def searchByUse():
    use = request.args.get('use', None)
    taxon = request.args.get('taxon', None)
    qps = request.args.get('qps', None)
    score = request.args.get('score', None)
    app.logger.info("score ")
    app.logger.info(score) 
    return render_template('searchByUse.html', use=use, taxon=taxon, qps=qps, 
                                               version=VERSION,
                                               alvisir=URL_ALVISIR, score=score)

# Advanced Search page
@app.route('/advancedSearch/')
@app.route('/advancedSearch')
def advancedSearch():
    return render_template('advancedSearch.html', version=VERSION, alvisir=URL_ALVISIR)

# Advanced Search page
@app.route('/searchTaxon/')
@app.route('/searchTaxon')
def searchTaxon():
    taxon = request.args.get('taxon', None)
    habitat = request.args.get('habitat', None)
    qps = request.args.get('qps', None)
    sources = request.args.getlist("source", None)
    return render_template('searchByTaxon0.html', taxon=taxon,
                                                  habitat=habitat,
                                                  qps=qps,
                                                  sources=sources,
                                                  version=VERSION,
                                                  alvisir=URL_ALVISIR)

# SourceAbstract
@app.route('/sourceAbstract/')
@app.route('/sourceAbstract')
def sourceAbstract():
    id_source = request.args.get('id_source', None)
    id_relation = request.args.get('id_relation', None)
    return render_template('sourceAbstract.html', id_source=id_source,
                                                  id_relation=id_relation,
                                                  )

# Database queries
@app.route('/_get_list_term')
def get_list_term():
    table = request.args.get('table', None)
    return(jsonify(list_terms(app, conn, table)))

@app.route('/_get_path')
def get_path():
    name = request.args.get('name', None)
    table = request.args.get('table', None)
    return(jsonify(path_term(app, conn, name, table)))
@app.route('/_get_path_taxon')
def get_path_taxon():
    name = request.args.get('name', None)
    table = request.args.get('table', None)
    return(jsonify(path_term(app, conn, name, table)))
@app.route('/_get_path_habitat')
def get_path_habitat():
    name = request.args.get('name', None)
    table = request.args.get('table', None)
    return(jsonify(path_term(app, conn, name, table)))
@app.route('/_get_path_phenotype')
def get_path_phenotype():
    name = request.args.get('name', None)
    table = request.args.get('table', None)
    return(jsonify(path_term(app, conn, name, table)))

@app.route('/_get_search_relations')
def get_search_relations():
    source = request.args.getlist('source', None)
    taxonid = request.args.getlist('taxonid', None)
    qps = request.args.get('qps', None)
    ontobiotopeid = request.args.getlist('ontobiotopeid', None)
    type = request.args.getlist('type', None)
    return(jsonify(search_relations(app, conn, source, taxonid, qps, ontobiotopeid, type)))

# Get abstarct
@app.route('/_get_abstract')
def get_abstract():
    id_source = request.args.get('id_source', None)
    id_relation = request.args.get('id_relation', None)
    return(jsonify(list_sourceAbstract(app, conn, id_source,id_relation)))

# Search habitat, phenotype, use relations
@app.route('/_get_list_relations')
def get_list_relations():
    source = request.args.get('source', None)
    taxonid = request.args.get('taxonid', None)
    qps = request.args.get('qps', None)
    ontobiotopeid = request.args.get('ontobiotopeid', None)
    type = request.args.getlist('type', None)
    return(jsonify(list_relations(app, conn, source, taxonid, qps, ontobiotopeid, type)))

# Search advanced relations without join
@app.route('/_get_list_advanced_relations')
def get_list_advanced_relations():
    source = request.args.get('source', None)
    taxonid = request.args.get('taxonid', None)
    qps = request.args.get('qps', None)
    ontobiotopeid = request.args.get('ontobiotopeid', None)
    type = request.args.get('type', None)
    return(jsonify(list_advanced_relations(app, conn, source, taxonid, qps, ontobiotopeid, type)))
@app.route('/_get_list_advanced_relations_2')
def get_list_advanced_relations_2():
    source = request.args.get('source', None)
    taxonid = request.args.get('taxonid', None)
    qps = request.args.get('qps', None)
    ontobiotopeid = request.args.get('ontobiotopeid', None)
    type = request.args.get('type', None)
    return(jsonify(list_advanced_relations_2(app, conn, source, taxonid, qps, ontobiotopeid, type)))
@app.route('/_get_list_advanced_relations_3')
def get_list_advanced_relations_3():
    source = request.args.get('source', None)
    taxonid = request.args.get('taxonid', None)
    qps = request.args.get('qps', None)
    ontobiotopeid = request.args.get('ontobiotopeid', None)
    type = request.args.get('type', None)
    return(jsonify(list_advanced_relations_3(app, conn, source, taxonid, qps, ontobiotopeid, type)))
@app.route('/_get_list_advanced_relations_4')
def get_list_advanced_relations_4():
    test = request.args.get('test', None)
    source = request.args.get('source', None)
    taxonid = request.args.get('taxonid', None)
    ontobiotopeid = request.args.get('ontobiotopeid', None)
    return(jsonify(list_advanced_relations_4(app, conn, test, source, taxonid, ontobiotopeid)))

# List OBT class and Taxon scientific name
@app.route('/_get_list_obt_class')
def get_list_obt_class():
    table = request.args.get('table', None)
    return(jsonify(list_obt_class(app, conn, table)))
@app.route('/_get_list_taxon_name')
def get_list_taxon_name():
    return(jsonify(list_taxon_name(app, conn)))

# OntoBiotope
@app.route('/_get_ontobiotope_habitat')
def get_ontobiotope_habitat():
    with open(STATIC_DIR+"/files/habitat.json", "r") as ontobiotope_habitat:
        return ontobiotope_habitat.read()
@app.route('/_get_ontobiotope_phenotype')
def get_ontobiotope_phenotype():
    with open(STATIC_DIR+"/files/phenotype.json", "r") as ontobiotope_phenotype:
        return ontobiotope_phenotype.read()
@app.route('/_get_ontobiotope_use')
def get_ontobiotope_use():
    with open(STATIC_DIR+"/files/use.json", "r") as ontobiotope_use:
        return ontobiotope_use.read()
# Taxonomy
@app.route('/_get_taxid')
def get_taxid():
    path = request.args.get('path', None)
    qps = request.args.get('qps', None)
    return(jsonify(list_taxid(app, conn, path, qps)))

# API
source_choices = ["pubmed", "CIRM-BIA", "CIRM-CFBP", "CIRM-Levures", "dsmz", "genbank"]
qps_choices = ["yes", "no", "true", "false"]
type_choices = ["taxon", "habitat", "phenotype", "use"]

# Models
version_model = api.model('Version', {
    "omnicrobe": fields.String(description="Version number or ISO 8601", example="2020-11-09"),
    "taxonomy": fields.String(description="Version number or ISO 8601", example="2020-01-13"),
    "ontobiotope": fields.String(description="Version number or ISO 8601", example="2020-11-06"),
    "cirmbia": fields.String(description="Version number or ISO 8601", example="2019-07-05"),
    "cirmlevures": fields.String(description="Version number or ISO 8601", example="2019-07-05"),
    "cirmcfbp": fields.String(description="Version number or ISO 8601", example="2019-07-05"),
    "pubmed": fields.String(description="Version number or ISO 8601", example="2020-09-01"),
    "dsmz": fields.String(description="Version number or ISO 8601", example="2018-01-26"),
    "genbank": fields.String(description="Version number or ISO 8601", example="2021-09-20")
})
taxon_model = api.model('Taxon', {
    "id": fields.String(default="ncbi:1423", description="Taxon identifier", example="ncbi:1423"),
    "name": fields.String(description="Canonical name of this taxon", example="Bacillus subtilis"),
    "path": fields.List(fields.String(description="Taxon lineage from root to self", example="ncbi:1/ncbi:131567/ncbi:2/ncbi:1783272/ncbi:1239/ncbi:91061/ncbi:1385/ncbi:186817/ncbi:1386/ncbi:653685/ncbi:1423")),
    "qps": fields.String(description="Either this taxon is listed in QPS", enum=['yes', 'true', 'no', 'false'], example="yes")
})
obt_model = api.model('Obt', {
    "id": fields.String(description="OntoBiotope identifier", example="OBT:000427"),
    "type": fields.String(description="OntoBiotope type", enum=['habitat', 'phenotype', 'use'], example="habitat"),
    "name": fields.String(description="Canonical name of this concept", example="soil"),
    "synonyms": fields.List(fields.String(description="All the synonyms of this concept", example="soilborne")),
    "path": fields.List(fields.String(description="Path from root to this concept", example="OBT:000001/OBT:000013/OBT:000158/OBT:000427"))
})
doc_model = api.model('Doc', {
    "url": fields.String(description="Document identifiers where relations were found", example="https://www.ncbi.nlm.nih.gov/pubmed/6229999")
})
taxonid_model = api.model('TaxonID', {
    "id": fields.String(description="Taxon identifier", example="ncbi:1423")
})
taxonobj_model = api.model('TaxonObj', {
    "name": fields.String(description="Canonical name of this taxon", example="Bacillus subtilis"),
    "taxid": fields.String(default="ncbi:1423", description="Taxon identifier", example="ncbi:1423")
})
obtid_model = api.model('ObtID', {
    "id": fields.String(description="OntoBiotope identifier", example="OBT:000427"),
})
obtobj_model = api.model('ObtObj', {
    "name": fields.String(description="Canonical name of this concept", example="soil"),
    "obtid": fields.String(description="OntoBiotope identifier", example="OBT:000427")
})
relation_model = api.model('Relations', {
    "taxid": fields.String(description="Taxon identifier", example="ncbi:1423"),
    "obtid": fields.String(description="OntoBiotope identifier", example="OBT:000427"),
    "type": fields.String(description="OntoBiotope type", enum="['habitat', 'phenotype', 'use']", example="habitat"),
    "source": fields.String(description="OntoBiotope type", enum="['PubMed', 'GenBank', 'DSMZ', 'CIRM-BIA', 'CIRM-Levures']", example="PubMed", default="PubMed"),
    "docs": fields.List(fields.String(description="Document identifiers and document scores where relations were found (dictionary)", example={'id_doc':['10049283','2117'], 'score': [1.0,0.77]})),
    "taxon_forms": fields.List(fields.String(description="All surface forms and scores of the taxon (left-hand argument,dictionary)", example={'form':['subtilis'], 'score': [1.0]})),
    "tax_root": fields.String(example="ncbi:1423"),
    "taxon_objects": fields.Nested(taxonobj_model),
    "obt_forms": fields.List(fields.String(description="All surface forms of the OntoBiotope concept (right-hand argument, dictionnary)", example={'form':["infectious pathogenic", "pathogens"], 'score': [1.0,0.5]})),
    "obt_root": fields.String(example="ALL"),
    "obt_objects": fields.Nested(obtobj_model),
    "global_score": fields.String(description=" Global score of the relation" ,example=0.93)
})
join_relation_model = api.model('JoinRelations', {
    "joinId": fields.String(example="ncbi:1428"),
    "joinType": fields.String(example="taxon"),
    "leftDocs": fields.List(fields.String(example={'id_doc':["2117","1534"], 'score':[1.0,0.77]})),
    "leftId": fields.String(example="OBT:001893"),
    "leftRoot": fields.String(example="OBT:000008"),
    "leftSource": fields.String(example="DSMZ"),
    "leftType": fields.String(example="habitat"),
    "rightDocs": fields.List(fields.String(example={'id_doc':["2121","912"], 'score':[0.83,0.67]})),
    "rightId": fields.String(example="OBT:001620"),
    "rightRoot": fields.String(example="OBT:000003"),
    "rightSource": fields.String(example="DSMZ"),
    "rightType": fields.String(example="habitat"),
    "LeftRelationScore": fields.String(example=0.75),
    "RightRelationScore": fields.String(example=0.86)
})

# ***** /get/version ***** #
@api.route('/api/get/version', doc={"description": "Returns version information about this instance."})
class ApiVersion(Resource):
    @api.doc(model=version_model)
    def get(self):
        return jsonify(get_version(app, conn))

# ***** /get/taxon ***** #
@api.route('/api/get/taxon/<string:taxid>', doc={"description": "Returns the properties of a taxon given a taxon identifier."})
@api.route('/api/get/taxon/', doc=False)
@api.route('/api/get/taxon', doc=False)
@api.doc(params={'taxid': 'Taxon identifier (example: ncbi:1423)'})
class ApiGetTaxon(Resource):
    @api.doc(model=taxon_model)
    @api.doc(responses={
        200: 'Success',
        404: 'Missing mandatory parameter'
    })
    def get(self, taxid=None):
        if taxid == None:
            return {'error': 'TaxonID required'}, 404
        else:
            return jsonify(get_taxon(app, conn, taxid))

# ***** /get/obt ***** #
@api.route('/api/get/obt/<string:obtid>', doc={"description": "Returns the properties of an OntoBiotope concept given an OBT identifier."})
@api.route('/api/get/obt/', doc=False)
@api.route('/api/get/obt', doc=False)
@api.doc(params={'obtid': 'Concept OntoBiotope identifier (example: OBT:000427)'})
class ApiGetOntoBiotope(Resource):
    @api.doc(model=obt_model)
    @api.doc(responses={
        200: 'Success',
        404: 'Missing mandatory parameter'
    })
    def get(self, obtid=None):
        if obtid == None:
            return {'error': 'OntoBiotopeID required'}, 404
        else:
            return jsonify(get_ontobiotope(app, conn, obtid))

# ***** /get/doc ***** #
@api.route('/api/get/doc/<string:source>/<string:docid>', doc={"description": "Returns an URL that describes a document."})
@api.route('/api/get/doc/<string:docid>', doc=False)
@api.route('/api/get/doc/', doc=False)
@api.route('/api/get/doc', doc=False)
@api.doc(params={'docid': 'Document identifier (example: 6229999)'})
@api.doc(params={'source': 'Document source name (example: PubMed)'})
class ApiGetDocument(Resource):
    @api.doc(model=doc_model)
    @api.doc(responses={
        200: 'Success',
        400: 'Unrecognized source',
        404: 'DocumentID not found'
    })
    def get(self, source=None, docid=None):
        if source == None or docid == None:
            return {'error': 'Source and DocumentID required'}, 404
        else :
            results = get_doc(app, conn, source, docid)
            if results == "no":
                return {'error': 'Unrecognized source'}, 400
            elif results != {}:
                return jsonify(get_doc(app, conn, source, docid))
            else:
                return {'error': 'DocumentID not found'}, 404

# ***** /search/taxon ***** #
@api.route('/api/search/taxon/', doc=False)
@api.route('/api/search/taxon', doc={"description": "This function returns a list of taxon identifiers that match the constraints given as parameters. All parameters are optional but at least one must be provided (otherwise 400). Constraints are connected with the intersection (AND) operator."})
@api.doc(params={'s': 'Name or synonym (example: subtilis)'})
@api.doc(params={'root': 'Identifier of the ancestor taxon (example: ncbi:2)'})
@api.doc(params={'qps': 'Qualified Presumption of Safety (QPS) status (example: yes, no, true, false)'})
class ApiSearchTaxon(Resource):
    @api.doc(model=taxonid_model)
    @api.doc(responses={
        200: 'Success',
        400: 'Missing mandatory parameter'
    })
    def get(self):
        root = request.args.get('root', None)
        qps = request.args.get('qps', None)
        name = request.args.get('s', None)
        if root == None and qps == None and name == None:
            return {'error': 'At least one parameter required'}, 400
        else:
            return jsonify(search_taxon(app, conn, root, qps, name))

# ***** /search/ontobiotope ***** #
@api.route('/api/search/obt/', doc=False)
@api.route('/api/search/obt', doc={"description": "This function returns a list of OntoBiotope concept identifiers that match the constraints given as parameters. All parameters are optional but at least one must be provided (otherwise 400). Constraints are connected with the intersection (AND) operator."})
@api.doc(params={'s': 'Name or synonym (example: soil)'})
@api.doc(params={'root': 'Identifier of the ancestor taxon (example: OBT:000427)'})
@api.doc(params={'type': 'Concept type (example: habitat, phenotype, use)'})
class ApiSearchOBT(Resource):
    @api.doc(model=obtid_model)
    @api.doc(responses={
        200: 'Success',
        400: 'Missing mandatory parameter'
    })
    def get(self):
        root = request.args.get('root', None)
        type = request.args.get('type', None)
        name = request.args.get('s', None)
        if root == None and type == None and name == None:
            return {'error': 'At least one parameter required'}, 400
        else:
            return jsonify(search_ontobiotope(app, conn, root, type, name))

# ***** search/relations ***** #
@api.route('/api/search/relations/', doc=False)
@api.route('/api/search/relations', doc={"description": "This function returns a list of relations that match the constraints given as parameters. All parameters are optional but at least one must be provided (otherwise 400). Constraints are connected with the intersection (AND) operator."})
@api.doc(params={'source': 'Source name (example: PubMed, CIRM-BIA, CIRM-Levures, DSMZ, GenBank)'})
@api.doc(params={'taxid': 'NCBI identifier of taxa ancestor (left-hand argument)'})
@api.doc(params={'qps': 'Qualified Presumption of Safety (QPS) status (example: yes, no, true, false)'})
@api.doc(params={'obtid': 'OBT identifier of OntoBiotope concept ancestor (right-hand argument)'})
@api.doc(params={'type': 'Types of OntoBiotope concepts (example: habitat, phenotype, use)'})
class ApiSearchRelations(Resource):
    @api.doc(model=relation_model)
    @api.doc(responses={
        200: 'Success',
        400: 'Missing mandatory parameter'
    })
    def get(self):
        source = request.args.getlist('source', None)
        taxid = request.args.getlist('taxid', None)
        qps = request.args.get('qps', None)
        obtid = request.args.getlist('obtid', None)
        type = request.args.getlist('type', None)
        if source == None and taxid == None and qps == None and obtid == None and type == None:
            return {'error': 'At least one parameter required'}, 400
        else:
            return jsonify(search_relations(app, conn, source, taxid, qps, obtid, type))

# ***** search/join-relations ***** #
@api.route('/api/search/join-relations/', doc=False)
@api.route('/api/search/join-relations', doc={"description": "Searches for joined relations."})
@api.doc(params={'source': 'Source name (example: PubMed, CIRM-BIA, CIRM-Levures, DSMZ, GenBank)'})
@api.doc(params={'qps': 'Qualified Presumption of Safety (QPS) status (example: yes, no, true, false)'})
@api.doc(params={'left-type': 'Type of the left-hand entity (example: habitat, phenotype, use, taxon)'})
@api.doc(params={'left-root': 'Identifier of left-hand concept ancestor. If provided, then this function \
                               only returns relations whose left-hand concept is a descendent of the provided \
                               concept. If not provided, then relations are not restricted by their concept ancestor.'})
@api.doc(params={'right-type': 'Type of the right-hand entity (example: habitat, phenotype, use, taxon)'})
@api.doc(params={'right-root': 'Identifier of right-hand concept ancestor. If provided, then this function \
                               only returns relations whose right-hand concept is a descendent of the provided \
                               concept. If not provided, then relations are not restricted by their concept ancestor.'})
@api.doc(params={'join-type': 'Type of the pivot entity (example: habitat, phenotype, use, taxon)'})
@api.doc(params={'join-root': 'Identifier of pivot concept ancestor. If provided, then this function only \
                               returns relations whose pivot concept is a descendent of the provided concept. \
                               If not provided, then relations are not restricted by their concept ancestor.'})
@api.doc(params={'aggregate': 'Aggregation of the results.'})
class ApiSearchJoinRelations(Resource):
    @api.doc(model=join_relation_model)
    @api.doc(responses={
        200: 'Success',
        400: 'Missing mandatory parameter'
    })
    def get(self):
        source = request.args.getlist('source', None)
        qps = request.args.get('qps', None)
        lefttype = request.args.get('left-type', None)
        leftroot = request.args.getlist('left-root', None)
        righttype = request.args.get('right-type', None)
        rightroot = request.args.getlist('right-root', None)
        jointype = request.args.get('join-type', None)
        joinroot = request.args.get('join-root', None)
        aggregate = request.args.get('aggregate', "false")
        if source == None and qps == None and lefttype == None and leftroot == None \
        and righttype == None and rightroot == None and jointype == None and joinroot == None :
            return {'error': 'At least one parameter required'}, 400
        elif lefttype not in type_choices:
            return {'unknown type': lefttype}, 400
        elif jointype not in type_choices:
            return {'unknown type': jointype}, 400
        elif righttype not in type_choices:
            return {'unknown type': righttype}, 400
        elif jointype == "taxon":
            if lefttype == "taxon" or righttype == "taxon":
                return {'incompatible join type': ''}, 400
            elif aggregate.lower() == 'true':
                return jsonify(search_join_relations_by_taxon_aggregate(app, conn, source, qps, lefttype, leftroot, righttype, rightroot, joinroot, jointype))
            else:
                return jsonify(search_join_relations_by_taxon(app, conn, source, qps, lefttype, leftroot, righttype, rightroot, joinroot, jointype))
        elif lefttype != "taxon" or righttype != "taxon":
            return {'incompatible join type': ''}, 400
        elif aggregate.lower() == 'true':
            return jsonify(search_join_relations_by_ontobiotope_aggregate(app, conn, source, qps, lefttype, leftroot, righttype, rightroot, joinroot, jointype))
        else:
            return jsonify(search_join_relations_by_ontobiotope(app, conn, source, qps, lefttype, leftroot, righttype, rightroot, joinroot, jointype))
