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

from unittest import result
from flask import g, jsonify
import psycopg2
from psycopg2 import pool
import re
from omnicrobe_web.config import *

# Get Database connection
def get_db(app):
    if 'db' not in g:
        g.db = app.config['postgreSQL_pool'].getconn()
    return g.db

# Check source format
def check_source(s):
    sources = ['PubMed', 'GenBank', 'DSMZ', 'CIRM-BIA', 'CIRM-Levures', 'CIRM-CFBP']
    final = ''
    for source in sources:
        pattern = re.compile(source, re.IGNORECASE)
        final = pattern.sub(source, s)
        if final != s or final in sources:
            return final

# Available sources
sources = {
            "CIRM-BIA".lower() : "https://collection-cirmbia.fr/page/Display_souches/",
            "CIRM-Levures".lower() : "",
            "CIRM-CFBP".lower() : "",
            "DSMZ".lower() : "https://bacdive.dsmz.de/strain/",
            "GenBank".lower() : "https://www.ncbi.nlm.nih.gov/nuccore/",
            "PubMed".lower() : "https://pubmed.ncbi.nlm.nih.gov/"
          }

# Get version: /get/version
def get_version(app, conn):
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT omnicrobe, taxonomy, ontobiotope, pubmed, dsmz, genbank, cirmbia, cirmlevures, cirmcfbp \
                            FROM v_source")
        except psycopg2.Error as e:
            print(e)
        columns = ('omnicrobe', 'taxonomy', 'ontobiotope', 'pubmed', 'dsmz', 'genbank', 'cirmbia', 'cirmlevures', 'cirmcfbp')
        return dict(zip(columns, cursor.fetchall()[0]))
        cursor.close()

# Get taxon: /get/taxon
def get_taxon(app, conn, id):
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT taxonid, name, path, qps \
                            FROM taxon \
                            WHERE taxonid = '" + id +"'")
        except psycopg2.Error as e:
            print(e)
        results = dict()
        for row in cursor.fetchall():
            results['id'] = row[0]
            results['name'] = row[1]
            results['path'] = []
            for path in row[2].split(","):
                results['path'].append(path)
            results['qps'] = row[3]
        cursor.close()
        return results

# Get OntoBiotope: /get/ontobiotope
def get_ontobiotope(app, conn, id):
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT identifier, name, path, type, synonym \
                            FROM element \
                            WHERE identifier = '" + id +"'")
        except psycopg2.Error as e:
            print(e)
        results = dict()
        for row in cursor.fetchall():
            results['id'] = row[0]
            results['name'] = row[1]
            results['path'] = []
            for path in row[2].split(","):
                results['path'].append(path)
            results['type'] = row[3]
            results['synonyms'] = []
            if row[4] != None:
                for synonym in row[4].split(","):
                    results['synonyms'].append(synonym)
        cursor.close()
        return results

# Get Source text: /get/doc
def get_doc(app, conn, source, id):
    if source.lower() in sources.keys():
        conn = get_db(app)
        if conn != None:
            cursor = conn.cursor()
            ss = check_source(source)
            try:
                cursor.execute("SELECT id_source FROM document \
                                WHERE id_source like '%" + str(id) +"%' \
                                AND source = '" + ss + "'")
            except psycopg2.Error as e:
                print(e)
            results = dict()
            if cursor.fetchall() != []:
                results['url'] = sources[source.lower()] + id
            cursor.close()
    else:
        results = "no"
    return results

# Search taxon: /search/taxon
def search_taxon(app, conn, root, qps, name):
    query = "SELECT taxonid FROM taxon WHERE "
    if qps in ("yes", "true"):
        query += "qps = 'yes' AND "
    if name != None:
        query += "lower(name) ~ '" + name + "' AND "
    if root != None:
        query += "(taxonid = '" + root + "' or path like '%/" + root + "/%')"
    query = re.sub('AND $', '', query)
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)
        results = []
        for row in cursor.fetchall():
            results.append({"id" : row[0]})
        cursor.close()
        return results

# Search OntoBiotope: /search/ontobiotope
def search_ontobiotope(app, conn, root, type, name):
    query = "SELECT identifier FROM element WHERE "
    if type != None:
        query += "type = '" + type + "' AND "
    if name != None:
        query += "(lower(name) ~ '" + name + "' or lower(synonym)  ~ '" + name + "') AND "
    if root != None:
        query += "(identifier = '" + root + "' or path like '%/" + root + "/%')"
    query = re.sub('AND $', '', query)
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)
        results = []
        for row in cursor.fetchall():
            results.append({"id" : row[0]})
        cursor.close()
        return results

# Search relations: /search/relations
def search_relations(app, conn, source, taxonids, qps, ontobiotopeids, types):
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        results = []

        if taxonids == [] and ontobiotopeids != []:
            taxonid = None
            for ontobiotopeid in ontobiotopeids:
                results += create_sql_relation(source, qps, types, taxonid, ontobiotopeid, cursor)
        elif taxonids != [] and ontobiotopeids == []:
            ontobiotopeid = None
            for taxonid in taxonids:
                results += create_sql_relation(source, qps, types, taxonid, ontobiotopeid, cursor)
        else:
            for taxonid in taxonids:
                for ontobiotopeid in ontobiotopeids:
                    results += create_sql_relation(source, qps, types, taxonid, ontobiotopeid, cursor)

        cursor.close()
        return results

# Create SQL query for Search relations
def create_sql_relation(source, qps, types, taxonid, ontobiotopeid, cursor):
    check = 'yes'
    oldRelation=  None
    newRelation =None
    oldSource=  None
    newSource =None
    oldIdDoc=None
    newIdDoc=None

    if taxonid == None:
        taxroot = "null"
    else:
        taxroot = taxonid
    if ontobiotopeid == None:
        obtroot = "ALL"
    else:
        obtroot = ontobiotopeid
    results = []
    query = "SELECT r.form_taxon, r.form_element, r.score_taxon,r.score_element, \
    r.type,  e.identifier, t.taxonid, e.name, t.name, d.id_source, d.source, o.doc_score, r.score_global, o.id_relation, o.score_occ, o.positions, d.text "
    query += " FROM relation r, taxon t, element e, document d, occurrence o"
    query += " WHERE r.id_element = e.id AND t.id = r.id_taxon AND o.id_doc=d.id AND o.id_relation=r.id "
    if source != []:
        query += " AND ("
        for s in source:
            ss = check_source(s)
            query += "d.source = '" + ss + "' OR "
        query += ")"
        query = re.sub(" OR \)", ")", query)
    if qps in ("yes", "true"):
        query += " AND t.qps = 'yes'"
    if types != []:
        query += " AND ("
        for type in types:
            query += "r.type = '" + type + "' OR "
        query += ")"
        query = re.sub(' OR \)', ')', query)
    if taxonid != None:
        query += " AND r.id_taxon in (SELECT id FROM taxon WHERE taxonid = '"+taxonid+"' OR path like '%/"+taxonid+"/%')"
    if ontobiotopeid != None:
        query += " AND r.id_element in (SELECT id FROM element WHERE identifier = '"+ontobiotopeid+"' OR path like '%/"+ontobiotopeid+"/%')"

    # Only if taxID and OBTID exist
    query += " ORDER by o.id_relation, d.source , d.id_source "

    if check == 'yes':
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)

        for row in cursor.fetchall(): # for each relation :

            # does the relation is already existing ?
            newRelation=row[13]
            newSource =row[10]
            newIdDoc=row[9]

            if newRelation!=oldRelation or newSource != oldSource: # if it doesn't
                newElement =True
                elements = {}
                # type, source, obtid, taxid
                elements['type'] = row[4]
                elements['source'] = row[10]

                elements['obtid'] = row[5]
                elements['taxid'] = row[6]

                elements['taxon_object'] = {'taxid': row[6], 'name': row[8]}
                elements['obt_object'] = {'obtid': row[5], 'name': row[7]}

                elements['taxroot'] = taxroot
                elements['obtroot'] = obtroot

                elements['global_score'] = row[12]

                # forms, docs
                elements['taxon_forms']={'form':clean_form(row[0]).split(', '), 'score':row[2].split(', ')}
                elements['obt_forms']={'form':clean_form(row[1]).split(', '), 'score':row[3].split(', ')}
                elements['docs']={'id_doc':[], 'score':[],'texts':[]}

                # occurrence
                elements['occ']={}

            else : # if it does
                newElement =False
                elements=results[len(results)-1]
            
            # add occurence if PubMed
            if row[10] == 'PubMed' or row[10] == 'pubmed' :
                # the doc is already in occ?
                if newElement or newIdDoc != oldIdDoc: # if not
                    elements['occ'][newIdDoc]={'positions':[],'score_occ':[]} # we need to add a key to this new doc

                elements['occ'][newIdDoc]['positions'].append(row[15])
                elements['occ'][newIdDoc]['score_occ'].append(row[14])

            # add docs
            doc=row[9]
            doc_score=row[11]
            if doc not in elements['docs']['id_doc']:
                elements['docs']['id_doc'].append(doc)
                elements['docs']['score'].append(doc_score)
                elements['docs']['texts'].append(row[16])

            if newElement : # if the relation is new
                results.append(elements) # we add it

            oldRelation=row[13] #the oldRelation became this one, the next one is the new
            oldSource=row[10]
            oldIdDoc=row[9]

        # we sort the list of doc and form by score
        for elements in results:
            sourceSort=list(zip(*sorted(zip(elements['docs']['score'],elements['docs']['id_doc'],elements['docs']['texts']), reverse=True)))
            taxonSort=list(zip(*sorted(zip(elements['taxon_forms']['score'],elements['taxon_forms']['form']), reverse=True)))
            obtSort=list(zip(*sorted(zip(elements['obt_forms']['score'],elements['obt_forms']['form']), reverse=True)))
            elements['docs']['score']=list(sourceSort[0])
            elements['docs']['id_doc']=list(sourceSort[1])
            elements['docs']['texts']=list(sourceSort[2])
            elements['taxon_forms']['score']=list(taxonSort[0])
            elements['taxon_forms']['form']=list(taxonSort[1])
            elements['obt_forms']['score']=list(obtSort[0])
            elements['obt_forms']['form']=list(obtSort[1])

    return results

# Search join-relations by Taxon: /search/join-relations
def search_join_relations_by_taxon(app, conn, source, qps, lefttype, leftroots, righttype, rightroots, joinroot, jointype):

    oldRelationLeft= None
    newRelationLeft =None
    oldRelationRight=None
    newRelationRight=None
    oldSourceLeft= None
    newSourceLeft =None
    oldSourceRight=None
    newSourceRight=None

    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        results = []
        for leftroot in leftroots:
            for rightroot in rightroots:
                if leftroot == rightroot:
                    continue
                query  = "SELECT le.identifier AS leftId, re.identifier AS rightId, je.taxonid AS joinId, ld.source AS leftSource, rd.source AS rightSource, \
                ld.id_source AS leftDocs, rd.id_source AS rightDocs , lo.doc_score AS leftScoreDoc, ro.doc_score AS rightScoreDoc, \
                lr.score_global AS leftScore, rr.score_global AS rightScore, lo.id_relation, ro.id_relation "
                query += " FROM element le, taxon je, element re, relation lr, relation rr, occurrence lo, occurrence ro, document ld, document rd "
                query += "WHERE lr.id_taxon = je.id "
                query += "AND lr.id_element = le.id "
                query += "AND rr.id_taxon = je.id "
                query += "AND rr.id_element = re.id "
                query += "AND lo.id_relation = lr.id "
                query += "AND ro.id_relation = rr.id "
                query += "AND lo.id_doc = ld.id "
                query += "AND ro.id_doc = rd.id "
                query += "AND lr.type = '" + lefttype + "' "
                query += "AND rr.type = '" + righttype + "' "
                query += "AND le.id != re.id "
                query += "AND (le.path like '%/" + leftroot + "/%' OR le.identifier = '"+ leftroot +"') "
                query += "AND (re.path like '%/" + rightroot + "/%' OR re.identifier = '"+ rightroot +"') "
                if joinroot != None:
                    query += "AND (je.path like '%/" + joinroot +"/%' OR je.taxonid = '"+ joinroot +"') "
                if qps in ("yes", "true"):
                    query += "AND je.qps = 'yes' "
                if source != []:
                    query = add_sources(query, source)

                query += " ORDER by lo.id_relation, ro.id_relation , ld.source, rd.source "
                try:
                    cursor.execute(query)
                except psycopg2.Error as e:
                    print(e)

                for row in cursor.fetchall():

                    # does the result has already been found ?
                    newRelationLeft=row[11]
                    newRelationRight=row[12]
                    newSourceLeft=row[3]
                    newSourceRight=row[4]

                    if newRelationLeft != oldRelationLeft or newRelationRight!=oldRelationRight or newSourceRight!=oldSourceRight or newSourceLeft!=oldSourceLeft : # if it doesn't
                        newElement=True
                        elements = {}
                        elements['leftId'] = row[0]
                        elements['rightId'] = row[1]
                        elements['joinId'] = row[2]
                        elements['leftSource'] = row[3]
                        elements['rightSource'] = row[4]
                        elements['leftType'] = lefttype
                        elements['joinType'] = jointype
                        elements['rightType'] = righttype
                        elements['leftRoot'] = leftroot
                        elements['rightRoot'] = rightroot
                        elements['leftDocs'] = {'id_doc':[], 'score':[]}
                        elements['rightDocs'] = {'id_doc':[], 'score':[]}
                        elements['LeftRelationScore']=row[9]
                        elements['RightRelationScore']=row[10]

                    else: # if it does 
                        newElement=False
                        elements=results[len(results)-1]


                    if row[5] not in elements['leftDocs']['id_doc']:
                        elements['leftDocs']['id_doc'].append(row[5])
                        elements['leftDocs']['score'].append(row[7])

                    if row[6] not in elements['rightDocs']['id_doc']:
                        elements['rightDocs']['id_doc'].append(row[6])
                        elements['rightDocs']['score'].append(row[8])


                    if newElement : # if the relation is new
                        results.append(elements) # we add it

                    oldRelationLeft=row[11]
                    oldRelationRight=row[12]
                    oldSourceLeft=row[3]
                    oldSourceRight=row[4]


                # doc sort by score
                for elements in results :
                    sourceLeftSort=list(zip(*sorted(zip(elements['leftDocs']['score'],elements['leftDocs']['id_doc']), reverse=True)))
                    sourceRightSort=list(zip(*sorted(zip(elements['rightDocs']['score'],elements['rightDocs']['id_doc']), reverse=True)))
                    elements['leftDocs']['score']= list(sourceLeftSort[0])
                    elements['leftDocs']['id_doc']=list(sourceLeftSort[1])
                    elements['rightDocs']['score']=list(sourceRightSort[0])
                    elements['rightDocs']['id_doc'] =list(sourceRightSort[1])

        cursor.close()
        return results
# Search join-relations by Taxon aggregate
# def search_join_relations_by_taxon_aggregate(app, conn, source, qps, lefttype, leftroots, righttype, rightroots, joinroot, jointype):
#     conn = get_db(app)
#     if conn != None:
#         cursor = conn.cursor()
#         results = []
#         for leftroot in leftroots:
#             for rightroot in rightroots:
#                 if leftroot == rightroot:
#                     continue
#                 query  = "SELECT le.identifier AS leftId, re.identifier AS rightId, je.taxonid AS joinId, lr.source AS leftSource, rr.source AS rightSource, lr.id_source AS leftDocs, rr.id_source AS rightDocs "
#                 query += "FROM element le, taxon je, element re, relation lr, relation rr "
#                 query += "WHERE lr.id_taxon = je.id "
#                 query += "AND lr.id_element = le.id "
#                 query += "AND rr.id_taxon = je.id "
#                 query += "AND rr.id_element = re.id "
#                 query += "AND lr.type = '" + lefttype + "' "
#                 query += "AND rr.type = '" + righttype + "' "
#                 query += "AND le.id != re.id "
#                 query += "AND (le.path like '%/" + leftroot + "/%' OR le.identifier = '"+ leftroot +"') "
#                 query += "AND (re.path like '%/" + rightroot + "/%' OR re.identifier = '"+ rightroot +"') "
#                 if joinroot != None:
#                     query += "AND (je.path like '%/" + joinroot +"/%' OR je.taxonid = '"+ joinroot +"') "
#                 if qps in ("yes", "true"):
#                     query += "AND je.qps = 'yes' "
#                 if source != []:
#                     query = add_sources(query, source)
#                 try:
#                     cursor.execute(query)
#                 except Exception as err:
#                     print_psycopg2_exception(err)
#
#                 allLeftIds = {}
#                 allLeftDocs = {}
#                 allRightIds = {}
#                 allRightDocs = {}
#                 allJoinIds = {}
#                 elements = {}
#                 for row in cursor.fetchall():
#                     allLeftIds[row[0]] = ''
#                     allRightIds[row[1]] = ''
#                     allJoinIds[row[2]] = ''
#                     for ldoc in row[5].split(", "):
#                         allLeftDocs[ldoc] = ''
#                     for rdoc in row[6].split(", "):
#                         allRightDocs[rdoc] = ''
#                 elements['leftType'] = lefttype
#                 elements['rightType'] = righttype
#                 elements['leftId'] = leftroot
#                 elements['rightId'] = rightroot
#                 elements['leftRoot'] = leftroot
#                 elements['rightRoot'] = rightroot
#                 elements['leftDocuments'] = len(allLeftDocs.keys())
#                 elements['leftDiversity'] = len(allLeftIds.keys())
#                 elements['rightDocuments'] = len(allRightDocs.keys())
#                 elements['rightDiversity'] = len(allRightIds.keys())
#                 elements['joinDiversity'] = len(allJoinIds.keys())
#                 results.append(elements)
#         cursor.close()
#         return results

def search_join_relations_by_taxon_aggregate(app, conn, source, qps, lefttype, leftroots, righttype, rightroots, joinroot, jointype):

    result= search_join_relations_by_taxon(app, conn, source, qps, lefttype, leftroots, righttype, rightroots, joinroot, jointype)
    if len(result)==0 : # if there is no result :
        return result
    else : # else we do our aggregation :
        resultAggr=[]
        for leftroot in leftroots:
            for rightroot in rightroots:
                if leftroot == rightroot:
                    continue
                elements={}
                elements['leftRoot'] = leftroot
                elements['rightRoot'] = rightroot
                elements['leftId'] = leftroot
                elements['rightId'] = rightroot
                elements['leftType'] = lefttype
                elements['rightType'] = righttype

                # we take all the information of the lines where our leftroot is the one from the loop, and same for the righ :
                all=[ [result[i]['leftId'],result[i]['rightId'],result[i]['joinId'],result[i]['leftDocs'],result[i]['rightDocs']] for i in range(len(result)) if (result[i]['leftRoot']==leftroot and result[i]['rightRoot']==rightroot)]
                allLeftIds = [all[i][0] for i in range(len(all))] # list of left id with this leftroot and this rightroot (define in the loop)
                allRightIds = [all[i][1] for i in range(len(all))]
                allJoinIds = [all[i][2] for i in range(len(all))]
                allLeftDocs = [all[i][3]['id_doc'][j] for i in range(len(all)) for j in range(len(all[i][3]['id_doc']))]
                allRightDocs = [all[i][4]['id_doc'][j] for i in range(len(all)) for j in range(len(all[i][4]['id_doc']))]

                # we count the number of elements for each information, 'set' to be sure not to count the same thing several time
                elements['leftDocuments'] = len(set(allLeftDocs))
                elements['leftDiversity'] = len(set(allLeftIds))
                elements['rightDocuments'] = len(set(allRightDocs))
                elements['rightDiversity'] = len(set(allRightIds))
                elements['joinDiversity'] = len(set(allJoinIds))

                resultAggr.append(elements)

        return resultAggr


# Search join-relations by OntoBiotope: /search/join-relations
def search_join_relations_by_ontobiotope(app, conn, source, qps, lefttype, leftroots, righttype, rightroots, joinroot, jointype):

    oldRelationLeft= None
    newRelationLeft =None
    oldRelationRight=None
    newRelationRight=None
    newSourceRight =None
    oldSourceRight =None
    newSourceLeft=None
    oldSourceLeft=None
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        results = []
        for leftroot in leftroots:
            for rightroot in rightroots:
                if leftroot == rightroot:
                    continue

                query  = "SELECT le.taxonid AS leftId, re.taxonid AS rightId, je.identifier AS joinId, ld.source AS leftSource, rd.source AS rightSource, ld.id_source AS leftDocs, rd.id_source AS rightDocs , lo.doc_score AS leftScoreDoc, ro.doc_score AS rightScoreDoc, lr.score_global AS leftScore, rr.score_global AS rightScore "
                query += "FROM taxon le, element je, taxon re, relation lr, relation rr,occurrence lo, occurrence ro, document ld, document rd, lo.id_relation, ro.id_relation  "
                query += "WHERE lr.id_taxon = le.id "
                query += "AND lr.id_element = je.id "
                query += "AND rr.id_taxon = re.id "
                query += "AND rr.id_element = je.id "
                query += "AND lo.id_relation = lr.id "
                query += "AND ro.id_relation = rr.id "
                query += "AND lo.id_doc = ld.id "
                query += "AND ro.id_doc = rd.id "
                query += "AND lr.type = '" + jointype + "' "
                query += "AND rr.type = '" + jointype + "' "
                query += "AND le.id != re.id "
                query += "AND (le.path like '%/" + leftroot + "/%' OR le.taxonid = '"+ leftroot +"') "
                query += "AND (re.path like '%/" + rightroot + "/%' OR re.taxonid = '"+ rightroot +"') "
                if joinroot != None:
                    query += "AND (je.path like '%/" + joinroot +"/%' OR je.identifier = '"+ joinroot +"') "
                if qps in ("yes", "true"):
                    query += "AND je.qps = 'yes' "
                if source != []:
                    query = add_sources(query, source)
                
                query += " ORDER by lo.id_relation, ro.id_relation , ld.source, rd.source "
                try:
                    cursor.execute(query)
                except psycopg2.Error as e:
                    print(e)
                for row in cursor.fetchall():
                    # does the result has already been found ?
                    newRelationLeft=row[11]
                    newRelationRight=row[12]
                    newSourceLeft=row[3]
                    newSourceRight=row[4]

                    if newRelationLeft != oldRelationLeft or newRelationRight!=oldRelationRight or newSourceRight!=oldSourceRight or newSourceLeft!=oldSourceLeft : # if it doesn't
                        newElement=True
                        elements = {}
                        elements['leftId'] = row[0]
                        elements['rightId'] = row[1]
                        elements['joinId'] = row[2]
                        elements['leftSource'] = row[3]
                        elements['rightSource'] = row[4]
                        elements['leftType'] = lefttype
                        elements['joinType'] = jointype
                        elements['rightType'] = righttype
                        elements['leftRoot'] = leftroot
                        elements['rightRoot'] = rightroot
                        elements['leftDocs'] = {'id_doc':[], 'score':[]}
                        elements['rightDocs'] = {'id_doc':[], 'score':[]}
                        elements['LeftRelationScore']=row[9]
                        elements['RightRelationScore']=row[10]


                    else : 
                        newElement=False
                        elements=results[len(results)-1]


                    if row[5] not in elements['leftDocs']['id_doc']:
                        elements['leftDocs']['id_doc'].append(row[5])
                        elements['leftDocs']['score'].append(row[7])

                    if row[6] not in elements['rightDocs']['id_doc']:
                        elements['rightDocs']['id_doc'].append(row[6])
                        elements['rightDocs']['score'].append(row[8])


                    if newElement : # if the relation is new
                        results.append(elements) # we add it

                    oldRelationLeft=row[11]
                    oldRelationRight=row[12]
                    oldSourceLeft=row[3]
                    oldSourceRight=row[4]


                # doc sort by score
                for elements in results :
                    sourceLeftSort=list(zip(*sorted(zip(elements['leftDocs']['score'],elements['leftDocs']['id_doc']), reverse=True)))
                    sourceRightSort=list(zip(*sorted(zip(elements['rightDocs']['score'],elements['rightDocs']['id_doc']), reverse=True)))
                    elements['leftDocs']['score']= list(sourceLeftSort[0])
                    elements['leftDocs']['id_doc']=list(sourceLeftSort[1])
                    elements['rightDocs']['score']=list(sourceRightSort[0])
                    elements['rightDocs']['id_doc'] =list(sourceRightSort[1])

        cursor.close()
        return results
# Search join-relations by OntoBiotope aggregate
# def search_join_relations_by_ontobiotope_aggregate(app, conn, source, qps, lefttype, leftroots, righttype, rightroots, joinroot, jointype):
#     conn = get_db(app)
#     if conn != None:
#         cursor = conn.cursor()
#         results = []
#         for leftroot in leftroots:
#             for rightroot in rightroots:
#                 if leftroot == rightroot:
#                     continue
#                 query  = "SELECT le.taxonid AS leftId, re.taxonid AS rightId, je.identifier AS joinId, lr.source AS leftSource, rr.source AS rightSource, lr.id_source AS leftDocs, rr.id_source AS rightDocs "
#                 query += "FROM taxon le, element je, taxon re, relation lr, relation rr "
#                 query += "WHERE lr.id_taxon = le.id "
#                 query += "AND lr.id_element = je.id "
#                 query += "AND rr.id_taxon = re.id "
#                 query += "AND rr.id_element = je.id "
#                 query += "AND lr.type = '" + jointype + "' "
#                 query += "AND rr.type = '" + jointype + "' "
#                 query += "AND le.id != re.id "
#                 query += "AND (le.path like '%/" + leftroot + "/%' OR le.taxonid = '"+ leftroot +"') "
#                 query += "AND (re.path like '%/" + rightroot + "/%' OR re.taxonid = '"+ rightroot +"') "
#                 if joinroot != None:
#                     query += "AND (je.path like '%/" + joinroot +"/%' OR je.identifier = '"+ joinroot +"') "
#                 if qps in ("yes", "true"):
#                     query += " AND je.qps = 'yes'"
#                 if source != []:
#                     query = add_sources(query, source)
#                 try:
#                     cursor.execute(query)
#                 except Exception as err:
#                     print_psycopg2_exception(err)
#                 allLeftIds = {}
#                 allLeftDocs = {}
#                 allRightIds = {}
#                 allRightDocs = {}
#                 allJoinIds = {}
#                 elements = {}
#                 for row in cursor.fetchall():
#                     allLeftIds[row[0]] = ''
#                     allRightIds[row[1]] = ''
#                     allJoinIds[row[2]] = ''
#                     for ldoc in row[5].split(", "):
#                         allLeftDocs[ldoc] = ''
#                     for rdoc in row[6].split(", "):
#                         allRightDocs[rdoc] = ''
#                 elements['leftType'] = lefttype
#                 elements['rightType'] = righttype
#                 elements['leftId'] = leftroot
#                 elements['rightId'] = rightroot
#                 elements['leftRoot'] = leftroot
#                 elements['rightRoot'] = rightroot
#                 elements['leftDocuments'] = len(allLeftDocs.keys())
#                 elements['leftDiversity'] = len(allLeftIds.keys())
#                 elements['rightDocuments'] = len(allRightDocs.keys())
#                 elements['rightDiversity'] = len(allRightIds.keys())
#                 elements['joinDiversity'] = len(allJoinIds.keys())
#                 results.append(elements)
#
#         cursor.close()
#         return results

def search_join_relations_by_ontobiotope_aggregate(app, conn, source, qps, lefttype, leftroots, righttype, rightroots, joinroot, jointype):

    result= search_join_relations_by_ontobiotope(app, conn, source, qps, lefttype, leftroots, righttype, rightroots, joinroot, jointype)
    if len(result)==0 : # if there is no result :
        return result
    else : # else we do our aggregation :
        resultAggr=[]
        for leftroot in leftroots:
            for rightroot in rightroots:
                if leftroot == rightroot:
                    continue
                elements={}
                elements['leftRoot'] = leftroot
                elements['rightRoot'] = rightroot
                elements['leftId'] = leftroot
                elements['rightId'] = rightroot
                elements['leftType'] = lefttype
                elements['rightType'] = righttype

                # we take all the information of the lines where our leftroot is the one from the loop, and same for the righ :
                all=[ [result[i]['leftId'],result[i]['rightId'],result[i]['joinId'],result[i]['leftDocs'],result[i]['rightDocs']] for i in range(len(result)) if (result[i]['leftRoot']==leftroot and result[i]['rightRoot']==rightroot)]
                allLeftIds = [all[i][0] for i in range(len(all))] # list of left id with this leftroot and this rightroot (define in the loop)
                allRightIds = [all[i][1] for i in range(len(all))]
                allJoinIds = [all[i][2] for i in range(len(all))]
                allLeftDocs = [all[i][3]['id_doc'][j] for i in range(len(all)) for j in range(len(all[i][3]['id_doc']))]
                allRightDocs = [all[i][4]['id_doc'][j] for i in range(len(all)) for j in range(len(all[i][4]['id_doc']))]

                # we count the number of elements for each information, 'set' to be sure not to count the same thing several time
                elements['leftDocuments'] = len(set(allLeftDocs))
                elements['leftDiversity'] = len(set(allLeftIds))
                elements['rightDocuments'] = len(set(allRightDocs))
                elements['rightDiversity'] = len(set(allRightIds))
                elements['joinDiversity'] = len(set(allJoinIds))

                resultAggr.append(elements)

        return resultAggr

# List of scientific name or class (taxon, habitat, phenotype, use)
def list_terms(app, conn, table):
    query = 'SELECT name, path FROM ' + str(table) + ' ORDER BY name ASC'
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)

        results = []
        for row in cursor.fetchall():
            tmp = {}
            tmp["name"] = row[0]
            tmp["path"] = row[1].split("/")[-1]
            results.append(tmp)
        cursor.close()
        return results

# Path of taxon, habitat, phenotype or use
def path_term(app, conn, name, table):
    query = "SELECT path FROM " + table + " WHERE name = '" + name + "'"
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)
        results = cursor.fetchall()
        path = ""
        if len(results) != 0:
            path = results[0]
        cursor.close()
        return path

# List class (habitat, phenotype, use)
def list_obt_class(app, conn, table):
    query = "SELECT name, path FROM " + table
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)
        results = []
        for row in cursor.fetchall():
            tmp = {}
            tmp["name"] = row[0]
            # tmp["path"] = row[1]
            tmp["path"] = row[1].split("/")[-1]
            results.append(tmp)
        cursor.close()
        return results

# List scientific name (taxon)
def list_taxon_name(app, conn):
    query = 'SELECT name, path FROM list_taxon INTERSECT \
SELECT name, path FROM list_taxon_phenotype INTERSECT \
SELECT name, path FROM list_taxon_use ORDER BY "name" ASC'
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)
        results = []
        for row in cursor.fetchall():
            tmp = {}
            tmp["name"] = row[0]
            tmp["path"] = row[1]
            results.append(tmp)
        cursor.close()
        return results

# List taxID
def list_taxid(app, conn, path, qps):
    id = path.split('/')[-1]
    query = "SELECT taxonid FROM taxon t \
             WHERE (t.path like '%/"+id+"/%' OR t.taxonid = '"+id+"') \
             AND t.qps = '"+qps+"'"
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)
        results = []
        for row in cursor.fetchall():
            results.append(row[0])
        cursor.close()
        return results


def list_sourceAbstract(app, conn, idSource, idRelation):
    if (idSource!= None):
        conn = get_db(app)
        if conn != None :
            cursor = conn.cursor()
            if( idRelation != None ):
                query= "SELECT d.text, o.positions, o.score_occ ,r.type, r.form_taxon,r.score_taxon, r.form_element, r.score_element "
                query += " FROM occurrence o, document d,relation r "
                query+= " WHERE o.id_doc=d.id AND o.id_relation=r.id "
                query += "AND d.id_source = '"+ idSource +"' "
                query += " AND o.id_relation = '"+idRelation +"' "
            else : 
                query ="SELECT text FROM document WHERE id_source = '" +idSource +"' "

        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)

        if( idRelation != None ):
            rows=cursor.fetchall()
            results = []
            if (len(rows) != 0 ):
                results.append(rows[0][0]) #text
                results.append([]) # positions
                results.append([]) # score
                results.append(rows[0][3]) #type
                results.append(rows[0][4]) # form taxon
                results.append(rows[0][5]) # score taxon
                results.append(rows[0][6]) # form element
                results.append(rows[0][7]) # score element
                for row in rows:
                    results[1].append(row[1])
                    results[2].append(row[2])
            return results 
        
        else :
            return [cursor.fetchone()[0]]

    


# List of relations
def list_relations(app, conn, source, taxonid, qps, ontobiotopeid, types):
    conn = get_db(app)
    oldRelation=  None
    newRelation =None
    oldSource=None
    newSource=None


    if conn != None:
        cursor = conn.cursor()
        query = "SELECT DISTINCT r.form_taxon, r.score_taxon, r.form_element, r.score_element, d.id_source, \
    r.type, d.source, e.identifier, t.taxonid, t.qps, e.path, t.path, o.doc_score, r.score_global , o.id_relation "
        query += " FROM relation r, taxon t, element e,occurrence o, document d"
        query += " WHERE r.id_element = e.id AND t.id = r.id_taxon"
        query+= " AND o.id_relation=r.id AND o.id_doc=d.id"
        if source != None and source != []:
            query += " AND ("
            for s in source:
                ss = check_source(s)
                query += "d.source = '" + ss + "' OR "
            query += ")"
            query = re.sub(" OR \)", ")", query)
        if qps in ("yes", "true"):
            query += " AND t.qps = 'yes'"
        if types != None and types != []:
            query += " AND ("
            for type in types:
                query += "r.type = '" + type + "' OR "
            query += ")"
            query = re.sub(' OR \)', ')', query)
        if taxonid != None and taxonid != '':
            query += " AND r.id_taxon in (SELECT id FROM taxon t WHERE t.path like '%/" + taxonid + "/%' OR t.taxonid = '" + taxonid + "')"
        if ontobiotopeid != None and ontobiotopeid != '':
            query += " AND r.id_element in (SELECT id FROM element e WHERE e.path like '%/" + ontobiotopeid + "/%' OR e.identifier = '" + ontobiotopeid + "')"

        query += " order by o.id_relation, d.source, d.id_source "
        try:

            cursor.execute(query)
        except psycopg2.Error as e:
            print(e)
        results = []
        for row in cursor.fetchall():

            # does the relation is already existing ?
            newRelation=row[14]
            newSource=row[6]
            newIdDoc=row[4]

            if newRelation!=oldRelation or newSource != oldSource : #if it doesn't
                newElement=True
                elements = []
                # docs
                elements.append([]) # id source
                elements.append([]) # score doc
                elements.append(clean_form(row[0]).split(", ")) # form txt taxon
                elements.append(row[1].split(", ")) # form txt taxon score
                # relation type
                if row[5] == 'habitat':
                    if taxonid != None:
                        elements.append('Lives in')
                    else:
                        elements.append('Contains')
                if row[5] == 'phenotype':
                    if taxonid != None:
                        elements.append('Exhibits')
                    else:
                        elements.append('Is exhibited by')
                if row[5] == 'use':
                    if taxonid != None:
                        elements.append('Studied for')
                    else:
                        elements.append('Involves')
                elements.append(clean_form(row[2]).split(", ")) # form txt obt
                elements.append(row[3].split(", ")) # form txt obt score

                # qps
                elements.append(row[9])
                # Source
                elements.append(row[6])

                # path and id
                elements.append(row[10])
                elements.append(row[11])
                elements.append(row[7])
                elements.append(row[8])

                # global score
                elements.append(row[13]) # element 13 of list

                # id relation (not to print in datatable)
                elements.append(row[14])

            else  : # if it does
                newElement=False
                elements=results[len(results)-1]


            # add id_source
            if row[4] not in elements[0]:
                elements[0].append(row[4]) # id doc
                elements[1].append(row[12]) # score doc


            if newElement : # if new element
                results.append(elements) # we add it

            oldRelation=row[14] #the oldRelation became this one, the next one is the new
            oldSource=row[6]

        cursor.close()

  
        # As the expected format of list of forms, score and source is string : we run through all the elements to concatenate the lists :
        # and we sort them in the string by score
        for elements in results:
            sourceSort=list(zip(*sorted(zip(elements[1],elements[0]), reverse=True)))   
            taxonSort=list(zip(*sorted(zip(elements[3],elements[2]), reverse=True)))
            obtSort=list(zip(*sorted(zip(elements[6],elements[5]), reverse=True)))

            elements[0]=", ".join(map(str,sourceSort[1]))
            elements[1]=", ".join(map(str,sourceSort[0]))
                
            elements[2]=", ".join(map(str,taxonSort[1]))
            elements[3]=", ".join(map(str,taxonSort[0]))
            elements[5]=", ".join(map(str,obtSort[1]))
            elements[6]=", ".join(map(str,obtSort[0]))

        return results

# List of relations (advanced)
def list_advanced_relations(app, conn, source, taxonids, qps, ontobiotopeids, types):
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        results = []

        if taxonids == None and ontobiotopeids != None:
            ontobiotopeids = ontobiotopeids.split(", ")
            taxonid = None
            for ontobiotopeid in ontobiotopeids:
                results += create_sql_advanced_relation(source, qps, types, taxonid, ontobiotopeid, cursor)
        elif taxonids != None and ontobiotopeids == None:
            taxonids = taxonids.split(", ")
            ontobiotopeid = None
            for taxonid in taxonids:
                results += create_sql_advanced_relation(source, qps, types, taxonid, ontobiotopeid, cursor)
        else:
            ontobiotopeids = ontobiotopeids.split(", ")
            taxonids = taxonids.split(", ")
            for taxonid in taxonids:
                for ontobiotopeid in ontobiotopeids:
                    results += create_sql_advanced_relation(source, qps, types, taxonid, ontobiotopeid, cursor)

        cursor.close()
        return results
def list_advanced_relations_2(app, conn, source, taxonids, qps, ontobiotopeids, types):
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        results = []

        ontobiotopeids = ontobiotopeids.split(", ")
        taxonids = taxonids.split(", ")

        for taxonid in taxonids:
            results += create_sql_advanced_relation(source, qps, None, taxonid, None, cursor)

        for ontobiotopeid in ontobiotopeids:
            results += create_sql_advanced_relation(source, qps, types, None, ontobiotopeid, cursor)

        cursor.close()
        return results
def list_advanced_relations_3(app, conn, source, taxonids, qps, ontobiotopeids, types):
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        results = []

        if taxonids != None:
            taxonids = taxonids.split(", ")
        else:
            taxonids = []
        if ontobiotopeids != None:
            ontobiotopeids = ontobiotopeids.split(", ")
        else:
            ontobiotopeids = []

        if taxonids != [] and ontobiotopeids == []:
            query = ""
            for taxonid in taxonids:
                query +=  "SELECT DISTINCT e.identifier FROM element e, relation r, taxon t "
                query += "WHERE e.id = r.id_element AND t.id = r.id_taxon "
                query += "AND r.id_taxon in (SELECT id FROM taxon WHERE "
                if qps == 'yes':
                    query += "qps = '" + qps + "' AND "
                query += "taxonid = '"+taxonid+"' OR path like '%/"+taxonid+"/%') INTERSECT "
            query = re.sub(r" INTERSECT $", "", query)
            try:

                cursor.execute(query)
            except psycopg2.Error as e:
                print(e)
            ontobiotopeids = []
            for row in cursor.fetchall():
                ontobiotopeids.append(row[0])
            for taxonid in taxonids:
                query = ""
                for ontobiotopeid in ontobiotopeids:
                    query += create_sql_advanced_relation_3(source, qps, types, taxonid, ontobiotopeid)
                query = re.sub(r" UNION $", "", query)
                query += " ORDER by idRel, SourceDoc  "
                results += get_result_advanced_relation_3(query, cursor)

        elif taxonids == [] and ontobiotopeids != []:
            query = ""
            for ontobiotopeid in ontobiotopeids:
                query +=  "SELECT DISTINCT t.taxonid FROM element e, relation r, taxon t "
                query += "WHERE e.id = r.id_element AND t.id = r.id_taxon "
                query += "AND r.id_element in (SELECT id FROM element WHERE identifier = '"+ontobiotopeid+"' OR path like '%/"+ontobiotopeid+"/%') INTERSECT "
            query = re.sub(r" INTERSECT $", "", query)
            try:
                cursor.execute(query)
            except psycopg2.Error as e:
                print(e)
            taxonids = []
            for row in cursor.fetchall():
                taxonids.append(row[0])
            for ontobiotopeid in ontobiotopeids:
                query = ""
                for taxonid in taxonids:
                    query += create_sql_advanced_relation_3(source, qps, types, taxonid, ontobiotopeid)
                query = re.sub(r" UNION $", "", query)
                query += " ORDER by idRel, SourceDoc  "
                results += get_result_advanced_relation_3(query, cursor)
        else:
            if len(taxonids) > 1 and len(ontobiotopeids) == 1:
                query = ""
                for taxonid in taxonids:
                    query +=  "SELECT DISTINCT e.identifier FROM element e, relation r, taxon t "
                    query += "WHERE e.id = r.id_element AND t.id = r.id_taxon "
                    query += "AND r.id_taxon in (SELECT id FROM taxon WHERE "
                    if qps == 'yes':
                        query += "qps = '" + qps + "' AND "
                    query += "taxonid = '"+taxonid+"' OR path like '%/"+taxonid+"/%') "
                    query += "AND r.id_element in (SELECT id FROM element WHERE identifier = '"+ontobiotopeids[0]+"' OR path like '%/"+ontobiotopeids[0]+"/%') INTERSECT "
                query = re.sub(r" INTERSECT $", "", query)
                try:
                    cursor.execute(query)
                except psycopg2.Error as e:
                    print(e)
                ontobiotopeids = []
                for row in cursor.fetchall():
                    ontobiotopeids.append(row[0])
                if ontobiotopeids != []:
                    for taxonid in taxonids:
                        query = ""
                        for ontobiotopeid in ontobiotopeids:
                            query += create_sql_advanced_relation_3(source, qps, types, taxonid, ontobiotopeid)
                        query = re.sub(r" UNION $", "", query)
                        query += " ORDER by idRel, SourceDoc  "
                        results += get_result_advanced_relation_3(query, cursor)
                else:
                    return []

            else:
                query = ""
                for ontobiotopeid in ontobiotopeids:
                    query +=  "SELECT DISTINCT t.taxonid FROM element e, relation r, taxon t "
                    query += "WHERE e.id = r.id_element AND t.id = r.id_taxon "
                    query += "AND r.id_taxon in (SELECT id FROM taxon WHERE "
                    if qps == 'yes':
                        query += "qps = '" + qps + "' AND "
                    query += "taxonid = '"+taxonids[0]+"' OR path like '%/"+taxonids[0]+"/%') "
                    query += "AND r.id_element in (SELECT id FROM element WHERE identifier = '"+ontobiotopeid+"' OR path like '%/"+ontobiotopeid+"/%') INTERSECT "
                query = re.sub(r" INTERSECT $", "", query)
                try:
                    cursor.execute(query)
                except psycopg2.Error as e:
                    print(e)
                taxonids = []
                for row in cursor.fetchall():
                    taxonids.append(row[0])
                if taxonids != []:
                    for ontobiotopeid in ontobiotopeids:
                        query = ""
                        for taxonid in taxonids:
                            query += create_sql_advanced_relation_3(source, qps, types, taxonid, ontobiotopeid)
                        query = re.sub(r" UNION $", "", query)
                        query += " ORDER by idRel, SourceDoc  "
                        results += get_result_advanced_relation_3(query, cursor)
                else:
                    return []

        cursor.close()
        return results
    

def list_advanced_relations_4(app, conn, query, source, taxonid, obtid):
    conn = get_db(app)
    if conn != None:
        cursor = conn.cursor()
        results = []
        try:
            cursor.execute(query)
        except psycopg2.Error as e:
            print(e) 


        if obtid != None:
            ontobiotopeids = obtid.split(", ")
        else:
            ontobiotopeids = []
        taxonids = []

        
        for row in cursor.fetchall() :
            taxonids.append(row[0])
        if taxonids == []:
            results = []
        else:
            for taxonid in taxonids:
                query = ""
                for ontobiotopeid in ontobiotopeids:
                    query += create_sql_advanced_relation_3(source, '', '', taxonid, ontobiotopeid)
                query = re.sub(r" UNION $", "", query)
                query += " ORDER by idRel, SourceDoc  "
                results += get_result_advanced_relation_3(query, cursor)

        cursor.close()
        return results
    






def create_sql_advanced_relation(source, qps, types, taxonid, ontobiotopeid, cursor):

    oldRelation=  None
    newRelation =None
    newSource= None
    oldSource=None
    results = []
    query = "SELECT DISTINCT r.form_taxon, r.score_taxon, r.form_element, r.score_element, d.id_source, \
    r.type, d.source, e.identifier, t.taxonid, t.qps, e.path, t.path, o.doc_score, r.score_global,o.id_relation, d.source  "
    query += " FROM relation r, taxon t, element e,occurrence o, document d"
    query += " WHERE r.id_element = e.id AND t.id = r.id_taxon"
    query+= " AND o.id_relation=r.id AND o.id_doc=d.id"
    if source != None:
        source = re.sub(", ", "', '", source)
        query += " AND d.source in ('" + source + "') "
    if qps == 'yes':
        query += " AND t.qps = 'yes'"
    if taxonid != None:
        query += " AND r.id_taxon in (SELECT id FROM taxon WHERE taxonid = '"+taxonid+"' OR path like '%/"+taxonid+"/%')"
    if ontobiotopeid != None:
        query += " AND r.id_element in (SELECT id FROM element WHERE identifier = '"+ontobiotopeid+"' OR path like '%/"+ontobiotopeid+"/%')"

    query += " ORDER by o.id_relation , d.source "
    try:
        cursor.execute(query)
    except psycopg2.Error as e:
        print(e)
    for row in cursor.fetchall():
        # does the relation is already existing ?
        newRelation=row[14]
        newSource=row[15]

        if newRelation!=oldRelation or newSource!=oldSource: #if it doesn't
            newElement=True
            elements = []
            # docs
            elements.append([]) # id source
            elements.append([]) # score doc
            elements.append(clean_form(row[0]).split(", ")) # form txt taxon
            elements.append(row[1].split(", ")) # form txt taxon score
            # relation type
           
            if row[5] == 'habitat':

                    elements.append('Lives in')

            if row[5] == 'phenotype':
    
                    elements.append('Exhibits')
   
            if row[5] == 'use':
                    elements.append('Studied for')
                

            elements.append(clean_form(row[2]).split(", ")) # form txt obt
            elements.append(row[3].split(", ")) # form txt obt score

            # qps
            elements.append(row[9])
            # Source
            elements.append(row[6])

            # path and id
            elements.append(row[10])
            elements.append(row[11])
            elements.append(row[7])
            elements.append(row[8])

            # global score
            elements.append(row[13])

            elements.append("") # ? dans le code original
            elements.append("") # ?

        else : # if it does
            newElement=False
            elements=results[len(results)-1]

        # add id_source
        if row[4] not in elements[0]:
            elements[0].append(row[4]) # id doc
            elements[1].append(row[12]) # score doc

        if newElement : # if new element
            results.append(elements) # we add it
        
        oldRelation=row[14]
        oldSource=row[15]

    

    # As the expected format of list of forms, score and source is string : we run through all the elements to concatenate the lists :
    # and we sort them in the string by score
    for elements in results:
        sourceSort=list(zip(*sorted(zip(elements[1],elements[0]), reverse=True)))
        taxonSort=list(zip(*sorted(zip(elements[3],elements[2]), reverse=True)))
        obtSort=list(zip(*sorted(zip(elements[6],elements[5]), reverse=True)))
        elements[0]=", ".join(map(str,sourceSort[1]))
        elements[1]=", ".join(map(str,sourceSort[0]))
        elements[2]=", ".join(map(str,taxonSort[1]))
        elements[3]=", ".join(map(str,taxonSort[0]))
        elements[5]=", ".join(map(str,obtSort[1]))
        elements[6]=", ".join(map(str,obtSort[0]))

    return results


def create_sql_advanced_relation_3(source, qps, types, taxonid, ontobiotopeid):
    query = "SELECT DISTINCT r.form_taxon, r.score_taxon, r.form_element, r.score_element, d.id_source, o.doc_score, "
    query += " r.type, d.source, e.identifier, t.taxonid, t.qps, e.path, t.path, r.score_global, o.id_relation as idRel, d.source as SourceDoc "
    query += " FROM relation r, taxon t, element e, occurrence o, document d"
    query += " WHERE r.id_element = e.id AND t.id = r.id_taxon"
    query += " AND o.id_doc=d.id AND o.id_relation=r.id"
    if source != None:
        source = re.sub(", ", "', '", source)
        query += " AND d.source in ('" + source + "') "
    if qps == 'yes':
        query += " AND t.qps = 'yes'"
    if ontobiotopeid != None:
        query += " AND r.id_element in (SELECT id FROM element WHERE identifier = '"+ontobiotopeid+"' OR path like '%/"+ontobiotopeid+"/%')"
    if taxonid != None:
        query += " AND r.id_taxon in (SELECT id FROM taxon WHERE taxonid = '"+taxonid+"')"
    query += " UNION "
    return query

def get_result_advanced_relation_3(query, cursor):
    oldRelation=  None
    newRelation =None
    newSource=None
    oldSource=None

    try:
        cursor.execute(query)
    except psycopg2.Error as e:
        print(e)
    results = []

    for row in cursor.fetchall():
        # does the relation is already existing ?
        newRelation=row[14]
        newSource=row[15]

        if newRelation!=oldRelation or newSource!=oldSource: #if it doesn't
            newElement=True
            elements = []
            # docs
            elements.append([]) # id source
            elements.append([]) # score doc
            elements.append(clean_form(row[0]).split(", ")) # form txt taxon
            elements.append(row[1].split(", ")) # form txt taxon score
            # relation type
            if row[6] == 'habitat':
                    elements.append('Lives in')
            if row[6] == 'phenotype':
                    elements.append('Exhibits')
            if row[6] == 'use':
                    elements.append('Studied for')

            elements.append(clean_form(row[2]).split(", ")) # form txt obt
            elements.append(row[3].split(", ")) # form txt obt score

            # qps
            elements.append(row[10])
            # Source
            elements.append(row[7])

            # path and id
            elements.append(row[11])
            elements.append(row[12])
            elements.append(row[8])
            elements.append(row[9])

            # global score
            elements.append(row[13])

            elements.append("") # ? dans le code original
            elements.append("") # ?

        else : # if it does
            newElement=False
            elements=results[len(results)-1]

        # add id_source
        if row[4] not in elements[0]:
            elements[0].append(row[4]) # id doc
            elements[1].append(row[5]) # score doc

        if newElement : # if new element
            results.append(elements) # we add it
        
        oldRelation=row[14]
        oldSource=row[15]

    

    # As the expected format of list of forms, score and source is string : we run through all the elements to concatenate the lists :
    # and we sort them in the string by score
    for elements in results:
        sourceSort=list(zip(*sorted(zip(elements[1],elements[0]), reverse=True)))
        taxonSort=list(zip(*sorted(zip(elements[3],elements[2]), reverse=True)))
        obtSort=list(zip(*sorted(zip(elements[6],elements[5]), reverse=True)))
        elements[0]=", ".join(map(str,sourceSort[1]))
        elements[1]=", ".join(map(str,sourceSort[0]))
        elements[2]=", ".join(map(str,taxonSort[1]))
        elements[3]=", ".join(map(str,taxonSort[0]))
        elements[5]=", ".join(map(str,obtSort[1]))
        elements[6]=", ".join(map(str,obtSort[0]))
    return results

# Utils
def add_sources(query, source):
    for col in ['ld', 'rd']:
        query += " AND ("
        for s in source:
            ss = check_source(s)
            query += col+".source = '" + ss + "' OR "
        query += ")"
        query = re.sub(" OR \)", ")", query)
    return query
def clean_form(form):
    form = re.sub("<em>", "", form)
    form = re.sub("</em> ", ", ", form)
    return form
def cut_obt_path(lpath):
    sql_path = ""
    for p in lpath:
        sql_path += "OR e.path like '" + p + "/%' "
    sql_path = re.sub('^OR ', '', sql_path)
    return sql_path
