/**
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
**/

import { calculateColor } from './utils.js';
import { isColorDark } from './utils.js';

var nbOcc;
var thickness_default = 3; // thickness of lines
var detection_default = 12; // thickness of detection lines 
var sep="---"


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//                                                        Main 
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//sourceAbstractMain(source,relation);


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//                                                  Main Function : getJson 
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

export function sourceAbstractMain(source, relation){

                  if(relation !==null && source !== null){  // abstract and entity

                      $.getJSON($SCRIPT_ROOT + '/_get_abstract',
                        {
                          id_source: source,
                          id_relation: relation
                        },
                        function (data) {

                          ////////////////////////////////////////// get text and title
                          var abstract =data[0].split(sep);
                          if(abstract.length >= 2){
                            var title=abstract[0];
                            var text=abstract[1];
                            $("#title_abstract").html(title);
                          } else {
                            var text=abstract[0];
                          }
                          $("#abstract").html(text);


                          //////////////////////////////////////////////////////////////////////// Faire les liaisons avec Recogito
                      
                          ////////////////////////////////////// initialization tool recogito
                          var recogito = Recogito.init({
                            content: 'abstract',
                            readOnly: true
                          });
                          
                          
                          // creation annotations 
                          var nbOcc=data[1].length;
                          var annotations=[];
                          var entities={};

                          for (var occ = 0; occ < nbOcc; occ++) {
                              for (var ent=1; ent<=2;ent ++){

                                    if(ent===1){
                                      var indexstart= data[1][occ][0];
                                      var indexstop= data[1][occ][1];
                                      var type="taxon";
                                    }else{
                                      var indexstart= data[1][occ][2];
                                      var indexstop= data[1][occ][3];
                                      var type=data[3];
                                    }
                                    var entityForm=$("#abstract").text().substring(indexstart,indexstop);
                                    var scoreEnt= getScoreEnt(entityForm,data[4],data[5],data[6],data[7]);
                                    var id="#occ"+occ+"ent"+ent;

                                    entities[id]={"type":type, "scoreEnt":scoreEnt};

                                    // add annotation of entity 1 or 2
                                    var annot = {
                                      "@context": "http://www.w3.org/ns/anno.jsonld",
                                      "id": id,
                                      "type": "Annotation" ,
                                      /*"body": [
                                        {
                                          "type": "TextualBody",
                                          "value": "The reliability of this word is " +scoreEnt +'.',
                                          "format": "text/plain",
                                          "purpose": "highlighting"
                                        },
                                        {
                                          "type": "TextualBody",
                                          "value": type,
                                          "purpose": "tagging"
                                        }
                                      ],*/
                                      "target": {
                                        "source": window.location.href,
                                        "selector": [
                                          {
                                            "type": "TextPositionSelector",
                                            "start": indexstart,
                                            "end": indexstop
                                          }
                                        ]
                                      }
                                    }

                                    annotations.push(annot);

                                    // add link when entity 2 annotation is created
                                    var taxonfirst= (data[1][occ][0] <= data[1][occ][2]);
                                    if(taxonfirst){
                                      var id1="#occ"+occ+"ent1";
                                      var id2="#occ"+occ+"ent2";
                                    }else{
                                      var id2="#occ"+occ+"ent1";
                                      var id1="#occ"+occ+"ent2";
                                    }

                                    var idocc="#occ"+occ;
                                    entities[idocc]={"scoreOcc":data[2][occ].toFixed(2)};

                                    if(ent===2){
                                            var relation=getRelation(type,taxonfirst);
                                            var link ={ 
                                              "@context": "http://www.w3.org/ns/anno.jsonld",
                                              "id": idocc,
                                              "type": "Annotation",
                                              "motivation": "linking",
                                              "body": [{
                                                "type": "TextualBody",
                                                "value": relation,
                                                "purpose": "tagging"
                                              }],
                                              "target": [{
                                                "id": id1
                                              }, {
                                                "id": id2
                                              }]
                                            };

                                            annotations.push(link);
                                    }

                              }
                          }
                          


                          // set annotations
                          recogito.setAnnotations(annotations).then(function(annot) {
                            //<span class="r6o-annotation" data-id="#occ0ent1">
                            
                            for (var occ = 0; occ < nbOcc; occ++) {

                              // entities 
                              for (var ent=1; ent<=2;ent ++){
                                var id=id="#occ"+occ+"ent"+ent;
                                var select='span[data-id="'+id+'"]';
                                var span=$(select);

                                // color depending on type
                                span.addClass(entities[id].type);

                                // opacity depending on score
                                var color=span.css('background-color');
                                var newcolor=color.split(',');
                                if(newcolor.length === 4){ // replace old opacity
                                  newcolor[newcolor.length]=entities[id].scoreEnt+')';
                                  newcolor= newcolor.join(',')
                                }else if(newcolor.length === 3){ // add opacity
                                  newcolor=color.split(')')[0]+','+entities[id].scoreEnt+')';
                                }
                                span.css("background-color",newcolor);
                                span.attr("data-scoreent",entities[id].scoreEnt);

                              }
                            }

                            // line 
                            var i=0;
                            var colorText;
                            var text;
                            var legendArrow =document.querySelectorAll("rect");
                            legendArrow.forEach(function(item){
                                  id="#occ"+i;
                                  color = calculateColor(entities[id].scoreOcc);
                                  // set attribut score
                                  item.setAttribute("data-scoreocc",entities[id].scoreOcc);
                                  // set background color
                                  item.setAttribute("fill",color);
                                  text=item.nextElementSibling;            
                                  colorText= (isColorDark(color))? "white":"black";
                                  //set text color
                                  text.setAttribute("fill",colorText);
                                  i=i+1;
                            })
                            
                          
                          });
                          

                        }
                  );

                  }
                  else if(source !== null){ // only abstract

                    $.getJSON($SCRIPT_ROOT + '/_get_abstract',
                        {
                          id_source: source,
                        },
                        function (data) {
                          var abstract =data[0].split(sep);
                          if(abstract.length >= 2){
                            var title=abstract[0];
                            var text=abstract[1];
                            $("#title_abstract").html(title);
                          } else {
                            var text=abstract[0];
                          }
                          $("#abstract").html(text);
                        }
                    );

                  } 


                }



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//                                                     Fonctions 
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



function getRelation(type, taxonfirst){
  //  ['Lives in', 'Studied for', 'Exhibits']
  if(taxonfirst){
    if (type === 'habitat'){return 'Lives in';}
    if (type === 'use'){return 'Studied for';}
    if (type === 'phenotype'){return 'Exhibits';}
  }else{
    if (type === 'habitat'){return 'Contains';}
    if (type === 'use'){return 'Involves';}
    if (type === 'phenotype'){return 'Is exhibited by';}
  }
}

function getScoreEnt(form,taxon, scoreTaxon, element,scoreElement){

  var listTaxon=taxon.split(', ');
  var listTaxonScore=scoreTaxon.split(', ');
  var listElement=element.split(', ');
  var listElementScore=scoreElement.split(', ');
  
  var index=listTaxon.indexOf(form);
  if(index === -1){ // if not taxon form
    index=listElement.indexOf(form);
      if(index !== -1){
        return parseFloat(listElementScore[index]).toFixed(2);
      }
  } else{ 
     return parseFloat(listTaxonScore[index]).toFixed(2);
  }

}



