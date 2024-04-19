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

import { format_docs } from './utils.js';
import { calculateColor } from './utils.js';
import { drawCircle } from './utils.js';

// infobulle html
let beginInfoBulle='<span class="infobulle" aria-label= "';
let middleInfoBulle='">';
let endInfoBulle="</span>";
function Canva(idCanva){ return "<canvas id='"+ idCanva +"' class='canvaColor'  width='25' height='25'></canvas> ";}
// -> beginInfoBulle + labelBulle + middleInfoBulle + Canva(idCanva)+ texte +endInfoBulle


$("#searchByPhenotype.nav-item").addClass( "active" );

$('#spinner_phenotype_taxon').show();
$('#spinner_phenotype_taxon2').show();

// Phenotype selection
var $select = $('#search_phenotype').selectize({
    valueField: 'path',
    labelField: 'name',
    searchField: 'name',
    sortField: 'name',
    placeholder: 'e.g. thermophile',
    openOnFocus: false,
    create: false,
    maxItems: 1,
    onInitialize: function() {
      var that = this;

      $.getJSON($SCRIPT_ROOT + '/_get_list_obt_class',
      // $.getJSON($SCRIPT_ROOT + '/_get_list_term',
        { table: "list_phenotype_taxon"},
        function(data) {
          data.forEach(function(item) {
            that.addOption(item);
          });
          $('#spinner_phenotype_taxon').hide();
          $('#spinner_phenotype_taxon2').hide();
          $('#search_phenotype option:selected').prop('disabled', false);
        });
    },
    onChange:function(ontobiotopeid){
      if (ontobiotopeid != "") {

        // Tree event
        $('#phenotypetree').data('simpleTree').clearSelection();
        $('#phenotypetree').data('simpleTree').collapseAll();
        var node = $('#phenotypetree').data('simpleTree').getNodeFromValue(ontobiotopeid);
        $('#phenotypetree').data('simpleTree').setSelectedNode(node);
      }
		}
  });
var selectize = $select[0].selectize;

// Tree
var options = {
    searchBox: $('#searchtreephenotype'),
    searchMinInputLength: 4
};
$.getJSON($SCRIPT_ROOT + '/_get_ontobiotope_phenotype', function(data) {
  $('#phenotypetree').simpleTree(options, data);

  // URL : phenotype
  if ( phenotype !== null ) {
    $.getJSON($SCRIPT_ROOT + '/_get_path',
      {name: phenotype, table: 'list_phenotype_taxon'},
      function success(path) {
        if ( path != '' ) {
          let l_path = path[0].split('/');
          let ontobiotopeid = l_path[l_path.length-1];

          // Tree event
          var node = $('#phenotypetree').data('simpleTree').getNodeFromValue(ontobiotopeid);
          $('#phenotypetree').data('simpleTree').setSelectedNode(node);
        }
      });
  }

  // URL : qps
  if ( qps !== null ) {
    $('input:checkbox').prop('checked', true);
  }

  // URL : taxon
  if ( taxon !== null ) {
    $('input.column_filter').val(taxon);
  }

  // URL: score
if (score !== null) {
  $('input.column_filter_short').val(score);
  filterColumnScore($('input.column_filter_short').closest('td').data('column'));
}

});
$('#phenotypetree').on('simpleTree:change', function(event){

  if ( $('#phenotypetree').data('simpleTree').getSelectedNode() != undefined ) {

    selectize.clear(false);
    selectize.setValue($('#phenotypetree').data('simpleTree').getSelectedNode().value, true);

    $('#spinner_phenotype_taxon').show();
    $('#spinner_phenotype_taxon2').show();

    $('#searchtreephenotype').val($('#phenotypetree').data('simpleTree').getSelectedNode().label);
    createTable($('#phenotypetree').data('simpleTree').getSelectedNode().value);
    $("#search_phenotype option:selected").text();
    $("#search_phenotype option:selected").text($('#phenotypetree').data('simpleTree').getSelectedNode().label);
    $("#search_phenotype option:selected").val($('#phenotypetree').data('simpleTree').getSelectedNode().value);
    //selectize.setTextboxValue("");
    //selectize.setTextboxValue($('#phenotypetree').data('simpleTree').getSelectedNode().label);
    $('#filter_phenotype_taxon').removeAttr('disabled');
    $('#treeModalPhenotype').modal('hide');
  }
})

// Data table
var thtable = $('#results_phenotype_taxon').DataTable();
function createTable(ontobiotopeid) {

        $.getJSON($SCRIPT_ROOT + '/_get_list_relations',
          {
            ontobiotopeid: ontobiotopeid,
            type: 'phenotype'
          },
          function success(relations) {
            $('#hide').css( 'display', 'block' );
            $('#results_phenotype_taxon').DataTable().destroy();
            thtable = $('#results_phenotype_taxon').DataTable(
              {dom: 'lifrtBp', // 'Bfrtip'
               data: relations,
               buttons: [
                          {
                              extend: 'copyHtml5',
                              exportOptions: { columns: function ( idx, data, node ) {
                                                var table_id = node.getAttribute('aria-controls');
                                                if ( idx == 0 ) { return false; } // Never Source Text
                                                else if ( idx == 6 ) { return true; } // Always Full Source Text
                                                return $('#' + table_id).DataTable().column( idx ).visible(); }
                                             },
                              title: 'Omnicrobe_V_'+version
                          },
                          {
                              extend: 'csvHtml5',
                              exportOptions: { columns: function ( idx, data, node ) {
                                                var table_id = node.getAttribute('aria-controls');
                                                if ( idx == 0 ) { return false; } // Never Source Text
                                                else if ( idx == 6 ) { return true; } // Always Full Source Text
                                                return $('#' + table_id).DataTable().column( idx ).visible(); }
                                             },
                              title: 'Omnicrobe_V_'+version
                          },
                          {
                              extend: 'excelHtml5',
                              exportOptions: { columns: function ( idx, data, node ) {
                                                 var table_id = node.getAttribute('aria-controls');
                                                 if ( idx == 0 ) { return false; } // Never Source Text
                                                 else if ( idx == 6 ) { return true; } // Always Full Source Text
                                                 else { return $('#' + table_id).DataTable().column( idx ).visible(); } }
                                             },
                              title: 'Omnicrobe_V_'+version
                          },
                          {
                              extend: 'pdfHtml5',
                              exportOptions: { columns: function ( idx, data, node ) {
                                                 var table_id = node.getAttribute('aria-controls');
                                                 if ( idx == 0 ) { return false; } // Never Source Text
                                                 else if ( idx == 6 ) { return true; } // Always Full Source Text
                                                 return $('#' + table_id).DataTable().column( idx ).visible(); }
                                             },
                              title: 'Omnicrobe_V_'+version
                          },
                          'colvis'
                      ],
                 columnDefs: [ // use css class on column
                     {
                       targets: [6], // Index column "Score" (start at 0)
                       className: 'scoreGlobal',
                     },
                   ],
               columns: [
                 {"render": function(data, type, row, meta) {

                    // doc 2
                    var docids = format_docs(row);
                    let docScores=row[1].split(", ");
                    let docSources=docids.split(", ");
                    let docs = "";
                    if ( data.includes(', ') ) { docs = data.split(', '); }
                    else                       { docs = data.split(','); }
                    let docs_f = "";
                    let nbSourcePrint =Math.min(2,docSources.length);
                    for(let i=0;i<nbSourcePrint ; i++){
                        docs_f += beginInfoBulle + parseFloat(docScores[i]).toFixed(2) + middleInfoBulle + Canva('canvaScoreDoc'+i)+ docSources[i] +endInfoBulle;
                        if ( i != nbSourcePrint -1 ) { docs_f += ", " }
                    }
                    if ( docSources.length > 2 ) {
                        docs_f +=", ..."; // 0,3
                    }

                    return docs_f;
                  }},
                 {"render": function (data, type, row, meta) {
                 //obt 1

                    let text = row[5].split(',')[0];
                    let score = parseFloat(row[6].split(', ')[0]).toFixed(2);
                    let canva = Canva('canvaScoreObt');
                    let result = beginInfoBulle + score + middleInfoBulle + canva + text +endInfoBulle;
                    return result;
                 }},
                 {"render": function (data, type, row, meta) {
                 //relation
                     return row[4];
                 }},
                 {"render": function ( data, type, row, meta ) {
                 //taxon 1
                   let taxa = row[2].split(', ');
                   let score=parseFloat(row[3].split(',')[0]).toFixed(2);
                   let taxon = "";
                   taxon +=beginInfoBulle + score + middleInfoBulle + Canva('canvaScoreTax');
                   if ( row[12].includes("ncbi") ) {
                     taxon +=  "<a target='_blank' class='doc'  href='https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="+row[12].replace(/.+:/ig, '')+"'>"+taxa[0]+"</a>";
                   }
                   else if ( row[12].includes("bd") ) {
                     taxon +=  "<a target='_blank' class='doc'  href='https://bacdive.dsmz.de/strain/"+row[12].replace(/.+:/ig, '')+"'>"+taxa[0]+"</a>";
                   }
                   taxon += endInfoBulle;
                   return taxon ;
                  }},
                 {"orderable": false, "render": function (data, type, row, meta) {
                 //qps
                     return row[7];
                 }},
                 {"render": function (data, type, row, meta) {
                 //source
                     return row[8];
                 }},
                  {"render": function (data, type, row, meta) {
                      //score
                      let score=row[13].toFixed(2);
                      return score;
                  }},
                 {"render": function (data, type, row, meta) {
                 //obt form
                     let elts = row[5].split(', ');
                     let scoreElts = row[6].split(', ');
                     let forms = "";
                     for ( let i = 0; i < elts.length ; i++ ) {
                       forms += beginInfoBulle + parseFloat(scoreElts[i]).toFixed(2) + middleInfoBulle  + elts[i] + endInfoBulle;
                       if ( i != elts.length - 1 ) { forms += ", " }
                     }
                     return forms;
                 }},
                 {"render": function (data, type, row, meta) {
                 // taxon form
                    let taxs = row[2].split(', ');
                    let scoreTax = row[3].split(', ');
                    let forms = "";
                    for ( let i = 0; i < taxs.length ; i++ ) {
                      forms += beginInfoBulle + parseFloat(scoreTax[i]).toFixed(2) + middleInfoBulle + taxs[i] + endInfoBulle;
                      if ( i != taxs.length - 1 ) { forms += ", " }
                    }
                    return forms;
                 }},
                 {"render": function (data, type, row, meta) {
                 //doc

                    var docids = format_docs(row);

                    let docScores=row[1].split(", ");
                    let docSources=docids.split(", ");
                    let docs_f="";
                    for(let i=0;i<docSources.length ; i++){
                        docs_f += beginInfoBulle + parseFloat(docScores[i]).toFixed(2) + middleInfoBulle + docSources[i] +endInfoBulle;
                        if ( i != docSources.length -1 ) { docs_f += ", " }
                    }
                    return docs_f;
                 }},
                 {"visible": false, "render": function (data, type, row, meta) {
                     return row[11];
                 }},
                 {"visible": false, "render": function (data, type, row, meta) {
                     return row[9];
                 }},
                 {"visible": false, "render": function (data, type, row, meta) {
                     return row[12];
                   }},
                 {"visible": false, "render": function (data, type, row, meta) {
                    return row[10];
                  }}
               ]
              });

              if ( $('#taxon_pt').val() != '' ) { filterColumnTaxon(3); }
              if ( $('input[name=qps_pt]').is(':checked') == true ) { filterColumnCheck(4); }

              $('#spinner_phenotype_taxon').hide();
              $('#spinner_phenotype_taxon2').hide();


            // add color for score
            $('#results_phenotype_taxon').DataTable().rows().every(function() {

                 var rowNode = this.node(); // Get the DOM node of the current row

                // background column score (col 7)
                  var value = $(rowNode).find('td:nth-child(7)').text();
                  var color = calculateColor(value);
                  $(rowNode).find('td:nth-child(7)').css('background-color', color);

                // circle color for score OBT (col 2)
                drawCircle(2,rowNode,'#canvaScoreObt');
                // circle color for score taxon (col 4)
                drawCircle(4,rowNode,'#canvaScoreTax');
                 // circle color for score doc (col 1)
                 var docs = $(rowNode).find('td:nth-child(1)').text();
                 var nbDoc = Math.min(2,docs.split(', ').length);
                 for (let i=0; i<nbDoc;i++){
                    drawCircle(1,rowNode,'#canvaScoreDoc'+i);
                 }
            });
              checkURL();
        });
}

// Filter - Taxon
function filterColumnTaxon(i) {
  $('#results_phenotype_taxon').DataTable().column(i).search(
    $('#taxon_pt').val().replace(/;/g, "|"), true, false
  ).draw();
  checkURL();
}
$('#filter_col4_input input.column_filter').on('keyup click', function() {
  filterColumnTaxon($(this).closest('td').data('column'));
});

// Filter - QPS
function filterColumnCheck(i) {
  let state = $('input[name=qps_pt]').is(':checked');
  let qps = "";
  if ( state == true )  { qps = "yes"; }
  $('#results_phenotype_taxon').DataTable().column(i).search(
    qps, true, false
  ).draw();
  checkURL();
}
$('input:checkbox').on('change', function () {
    filterColumnCheck(4);
 });

 // Filter score (>=)
 var scoreFilter = null;
 function filterColumnScore(column){
     // get the minimal score
     var scoreMin= $('#score_pt').val();
     if (isNaN(scoreMin)) {
           scoreMin = 0;
     }else if ( typeof (scoreMin) === 'string' ){
            scoreMin=parseFloat(scoreMin.replace(/<.*?>/g, '')); // enlever balise html
     }
     // verify value between 0 and 1
     if (scoreMin > 1) {
         scoreMin = 1 ;
     } else if (scoreMin < 0 ){
         scoreMin = 0;
     }

     // deletion old filter (if one)
      if (scoreFilter !== null) {
         $.fn.dataTable.ext.search.splice($.fn.dataTable.ext.search.indexOf(scoreFilter), 1);
       }
     // definition of new filter
     scoreFilter = function(settings, data, dataIndex) {
         var score = parseFloat(data[column]);
         return score >= scoreMin;
     }
     // adding new filter
     $.fn.dataTable.ext.search.push(scoreFilter);
     // drawing the new table
     $('#results_phenotype_taxon').DataTable().draw();
     checkURL();
 }

 // use the filter when 'enter' on the input
 $('#filter_col7_input input.column_filter_short').on('keydown', function(event) {
   if (event.keyCode === 13) {
     filterColumnScore($(this).closest('td').data('column'));
   }
 });

 // Check url
 function checkURL() {
   var url = window.location.pathname;
   if ( $("#search_phenotype option:selected").text() !== '' ) {
     url += "?phenotype=" + $("#search_phenotype option:selected").text();
   }
   if ( $("#taxon_pt").val() !== '' ) {
     url += "&taxon=" + $("#taxon_pt").val();
   }
   if ( $('#qps_pt').is(":checked") ) {
     url += "&qps=yes";
   }
   if ( $("#score_pt").val() !== '' ) {
    url += "&score=" + $("#score_pt").val();
  }
   history.pushState({}, null, url);
 }
