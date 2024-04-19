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


// Spinner
$('#spinner_advanced').show();
$('#spinner_advanced2').show();

// Fix size input for Selectize
$('#builder').on('afterCreateRuleInput.queryBuilder', function(e, rule) {
  if (rule.filter.plugin == 'selectize') {
    rule.$el.find('.rule-value-container').css('min-width', '200px')
      .find('.selectize-control').removeClass('form-control');
  }
});

// Default display
var rules_basic = {
  condition: 'AND',
  rules: [{
    id: 'taxon'
  }
]
};

// Options for Selectize
var options = {
  allow_empty: false,
  // plugins: ['bt-tooltip-errors'],
  filters: [
  {
    id: 'taxon',
    label: 'Taxon',
    type: 'string',
    placeholder: 'Bacillus subtilis',
    plugin: 'selectize',
    operators: ['equal'],
    plugin_config: {
      valueField: 'path',
      labelField: 'name',
      searchField: 'name',
      sortField: 'name',
      create: false,
      maxItems: 1,
      onInitialize: function() {
        var that = this;

        $.getJSON($SCRIPT_ROOT + '/_get_list_taxon_name',
          function(data) {
            data.forEach(function(item) {
              that.addOption(item);
            });
            $('#spinner_advanced').hide();
            $('#spinner_advanced2').hide();
          });
      }
    },
    valueSetter: function(rule, value) {
      rule.$el.find('.rule-value-container input')[0].selectize.setValue(value);
    }
  },
  {
    id: 'habitat',
    label: 'Habitat',
    type: 'string',
    placeholder: 'milk product',
    plugin: 'selectize',
    operators: ['equal'],
    plugin_config: {
      valueField: 'path',
      labelField: 'name',
      searchField: 'name',
      sortField: 'name',
      create: false,
      maxItems: 1,
      onInitialize: function() {
        var that = this;

        if (localStorage.ontoHabitat === undefined) {
          $.getJSON($SCRIPT_ROOT + '/_get_list_obt_class',
            { table: 'list_habitat' },
            function(data) {
              localStorage.ontoHabitat = JSON.stringify(data);
              data.forEach(function(item) {
                that.addOption(item);
              });
            }
          );
        }
        else {
          JSON.parse(localStorage.ontoHabitat).forEach(function(item) {
            that.addOption(item);
          });
        }
      }
    },
    valueSetter: function(rule, value) {
      rule.$el.find('.rule-value-container input')[0].selectize.setValue(value);
    }
  },
  {
    id: 'phenotype',
    label: 'Phenotype',
    placeholder: 'adherent',
    type: 'string',
    plugin: 'selectize',
    operators: ['equal'],
    plugin_config: {
      valueField: 'path',
      labelField: 'name',
      searchField: 'name',
      sortField: 'name',
      create: false,
      maxItems: 1,
      onInitialize: function() {
        var that = this;

        if (localStorage.ontoPhenotype === undefined) {
          $.getJSON($SCRIPT_ROOT + '/_get_list_obt_class',
            { table: 'list_phenotype_taxon' },
            function(data) {
              localStorage.ontoPhenotype = JSON.stringify(data);
              data.forEach(function(item) {
                that.addOption(item);
              });
            }
          );
        }
        else {
          JSON.parse(localStorage.ontoPhenotype).forEach(function(item) {
            that.addOption(item);
          });
        }
      }
    },
    valueSetter: function(rule, value) {
      rule.$el.find('.rule-value-container input')[0].selectize.setValue(value);
    }
  },
  {
    id: 'use',
    label: 'Use',
    placeholder: 'acidification activity',
    type: 'string',
    plugin: 'selectize',
    operators: ['equal'],
    plugin_config: {
      valueField: 'path',
      labelField: 'name',
      searchField: 'name',
      sortField: 'name',
      create: false,
      maxItems: 1,
      onInitialize: function() {
        var that = this;

        if (localStorage.ontoUse === undefined) {
          $.getJSON($SCRIPT_ROOT + '/_get_list_obt_class',
            { table: 'list_use_taxon' },
            function(data) {
              localStorage.ontoUse = JSON.stringify(data);
              data.forEach(function(item) {
                that.addOption(item);
              });
            }
          );
        }
        else {
          JSON.parse(localStorage.ontoUse).forEach(function(item) {
            that.addOption(item);
          });
        }
      }
    },
    valueSetter: function(rule, value) {
      rule.$el.find('.rule-value-container input')[0].selectize.setValue(value);
    }
  },
  {
    id: 'source',
    label: 'Source',
    type: 'string',
    input: 'checkbox',
    values: {
      'PubMed': 'PubMed',
      'GenBank': 'GenBank',
      'DSMZ': 'DSMZ',
      'CIRM-BIA': 'CIRM-BIA',
      'CIRM-CFBP': 'CIRM-CFBP',
      'CIRM-Levures': 'CIRM-Levures'
    },
    default_value: ['PubMed', 'GenBank', 'DSMZ', 'CIRM-BIA', 'CIRM-CFBP', 'CIRM-Levures'],
    operators: ['in'],
  },
  {
    id: 'qps',
    label: 'QPS',
    type: 'string',
    input: 'radio',
    vertical: true,
    values: {
      'yes': 'only QPS (<i>Qualified presumption of safety</i>)',
      'no': 'all'
    },
    operators: ['equal']
  }
  ],
  rules: rules_basic
};

// Query Builder
var $qb = $("#builder").queryBuilder(options);

// function format(d, alvisir) {
//
//     let rtype = '';
//     if ( d[2] == "Lives in" ) { rtype = 'habitat'; }
//     else if ( d[2] == "Studied for" ) { rtype = 'use'; }
//     else if ( d[2] == "Exhibits" ) { rtype = 'phenotype'; }
//
//     var docids = format_docs(d, alvisir, rtype);
//     return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
//         '<tr>'+
//             '<td><b>Full source text</b></td>'+
//             '<td align="justify">'+docids+'</td>'+
//         '</tr>'+
//         '<tr>'+
//             '<td><b>Occurrence in text (taxon)</b></td>'+
//             '<td align="justify">'+d[1].split(", ").slice(1,).join(', ')+'</td>'+
//         '</tr>'+
//         '<tr>'+
//             '<td><b>Occurrence in text (element)</b></td>'+
//             '<td align="justify">'+d[3].split(", ").slice(1,).join(', ')+'</td>'+
//         '</tr>'+
//     '</table>';
// }

var thtable = $('#results_advanced').DataTable();

// Create results table
function createTableTest(relations) {

  $('#hide').css( 'display', 'block' );
  $('#filter_score').removeAttr('disabled');
  $('#results_advanced').DataTable().destroy();
  thtable = $('#results_advanced').DataTable(
      {
        dom: 'lifrtBp',
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
            let rtype = '';
            if ( row[4] == 'Lives in' || row[4] == 'Contains' ) { rtype = 'habitat'; }
            else if ( row[4] == 'Studied for' || row[4] == 'Involves' ) { rtype = 'use'; }
            else if ( row[4] == 'Exhibits' || row[4] == 'Is exhibited by' ) { rtype = 'phenotype'; }

            // doc 2
            var docids = format_docs(row, alvisir, rtype);
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
          {"render": function (data, type, row, meta) {

              return row[4];

          }},
          {"render": function (data, type, row, meta) {
                 //obt 1

                 let text = row[5].split(',')[0];
                 let score = parseFloat(row[6].split(', ')[0]).toFixed(2);
                 let canva = Canva('canvaScoreObt');
                 let result = beginInfoBulle + score + middleInfoBulle + canva + text +endInfoBulle;

                 return result;
          }},
          {"orderable": false, "render": function (data, type, row, meta) {

              return row[7];
          }},
          {"render": function (data, type, row, meta) {

              return row[8];
          }},
          {"render": function (data, type, row, meta) {
            //score
            let score=row[13].toFixed(2);
            return score;
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
                 // obt form
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
                 //doc
                 let rtype = '';
                 if ( row[4] == 'Lives in' || row[4] == 'Contains' ) { rtype = 'habitat'; }
                 else if ( row[4] == 'Studied for' || row[4] == 'Involves' ) { rtype = 'use'; }
                 else if ( row[4] == 'Exhibits' || row[4] == 'Is exhibited by' ) { rtype = 'phenotype'; }
                 var docids = format_docs(row, alvisir, rtype);

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

              return row[12];
          }},
          {"visible": false, "render": function (data, type, row, meta) {

             return row[10];
          }},
          {"visible": false, "render": function (data, type, row, meta) {

              return row[11];
          }},
          {"visible": false, "render": function (data, type, row, meta) {
              return row[9];
          }}
       ]
      });

  $('#spinner_advanced').hide();
  $('#spinner_advanced2').hide();


    // add color for score
    $('#results_advanced').DataTable().rows().every(function() {

      var rowNode = this.node(); // Get the DOM node of the current row

      // background column score (col 7)
        var value = $(rowNode).find('td:nth-child(7)').text();
        var color = calculateColor(value);
        $(rowNode).find('td:nth-child(7)').css('background-color', color);

      // circle color for score OBT (col 4)
      drawCircle(4,rowNode,'#canvaScoreObt');
      // circle color for score taxon (col 2)
      drawCircle(2,rowNode,'#canvaScoreTax');
      // circle color for score doc (col 1)
      var docs = $(rowNode).find('td:nth-child(1)').text();
      var nbDoc = Math.min(2,docs.split(', ').length);
      for (let i=0; i<nbDoc;i++){
          drawCircle(1,rowNode,'#canvaScoreDoc'+i);
      }


  });
}

$('.parse-json').on('click', function() {
  // console.log(JSON.stringify($('#builder').queryBuilder('getSQL'), undefined, 2));
  $('#spinner_advanced').show();
  $('#spinner_advanced2').show();

  var sql = JSON.stringify($('#builder').queryBuilder('getSQL'), undefined, 2);
  sql = JSON.parse(sql).sql;
  var sql_f = sql;

  // sources
  var regex_s = /source\s(IN\(.+\))/g;
  var found_s = sql.match(regex_s);
  var list_sources = [];
  if ( found_s != null ) {
    var l_source = "";
    for ( let i = 0 ; i < found_s.length ; i++ ) {
      var sources = found_s[i].replace(regex_s, '$1');
      sources = sources.replace('IN(', '');
      sources = sources.replace(')', '');
      l_source = sources.replaceAll("'", "");
    }
    if ( l_source != "" ) { list_sources = l_source.split(', '); }
  }

  // qps
  var regex_q = /qps\s=\s'([a-z]+)'/g;
  var found_q = sql.match(regex_q);
  if ( found_q != null ) {
    var qps = found_q[0].replace(regex_q, '$1');
  }

  // taxon
  var regex_t = /(AND|OR)?\s?(\(?)\s?taxon\s=\s'([a-z0-9/:]+)'\s?(\)?)/g;
  var found_t = sql.match(regex_t);
  var list_taxid = [];
  var list_op_tax = [];
  var op_tax = "";
  if ( found_t != null ) {
    var l_taxid = "";
    for ( let i = 0 ; i < found_t.length ; i++ ) {
      var op_tax = found_t[i].replace(regex_t, '$1');
      var par_tax_s = found_t[i].replace(regex_t, '$2');
      var path_t = found_t[i].replace(regex_t, '$3'); // $2
      var par_tax_e = found_t[i].replace(regex_t, '$4');
      var id_t = path_t.split('/'); id_t = id_t[id_t.length - 1];
      if ( l_taxid == "" ) { l_taxid = id_t; }
      else                 { l_taxid += ", " + id_t; }
      list_taxid.push(id_t);
      if ( op_tax != "" ) { list_op_tax.push(op_tax); }
      sql_f = sql_f.replace(found_t[i], "r.id_taxon in (SELECT id FROM taxon t WHERE t.path like '%/"+id_t+"/%' OR t.taxonid = '"+id_t+"')");
    }
  }

  // habitat | phenotype | use
  var regex_h = /(AND|OR)?\s?(\(?)\s?\b(habitat|phenotype|use)\b\s=\s'([\/A-Z0-9:,]+)'\s?(\)?)/g;
  var found_h = sql.match(regex_h);
  var list_obtid = [];
  var list_op_obt = [];
  var op_obt = "";
  if ( found_h != null ) {
    var type_obt = "";
    var l_obtid = "";
    var test = "";
    for ( let i = 0 ; i < found_h.length ; i++ ) {
      var op_obt = found_h[i].replace(regex_h, '$1');
      var par_obt_s = found_h[i].replace(regex_h, '$2');
      var type_obt = found_h[i].replace(regex_h, '$3'); // $2
      var path_h = found_h[i].replace(regex_h, '$4'); // $3
      var par_obt_e = found_h[i].replace(regex_h, '$5');
      var id_h = path_h.split('/'); id_h = id_h[id_h.length - 1];
      if ( op_obt == "AND" && i > 0 )      { test += "INTERSECT "; }
      else if ( op_obt == "OR" && i > 0 )  { test += "UNION "; }
      if ( par_obt_s == "(" )              { test += "("; }
      test += "select distinct(t.taxonid) from taxon t, relation r, element e, occurrence o, document d where r.id_taxon = t.id and r.id_element = e.id and o.id_doc=d.id and o.id_relation = r.id ";
      test += "and (e.identifier = '"+id_h+"' or e.path like '%/"+id_h+"/%') ";
      if ( list_taxid[0] != undefined ) {
        test += "and (t.taxonid = '"+list_taxid[0]+"' or t.path like '%/"+list_taxid[0]+"/%') "; }
      if ( qps == "yes" )                  { test += "and t.qps = 'yes' "; }
      if ( list_sources.length > 0 ) {
        test += "and d.source in (";
        for ( var k = 0 ; k < list_sources.length ; k++ ) {
          test += "'" + list_sources[k] + "'";
        }
        test += ") ";
      }
      if ( par_obt_e == ")" )              { test += ")"; }
      var id_h = path_h.split('/'); id_h = id_h[id_h.length - 1];
      if ( l_obtid == "" ) { l_obtid = id_h; }
      else                 { l_obtid += ", " + id_h; }
      list_obtid.push(id_h);
      if ( op_obt != "" ) { list_op_obt.push(op_obt); }
    }
  }

  // 1.a. Taxon = subtilis / OBT = abdomen
  // 1.b. Taxon = subtilis OR taxon = cereus
  // 1.c. Taxon = subtilis AND OBT = abdomen
  if (
       (list_taxid.length > 1  && list_obtid.length == 0 && op_obt == '' && op_tax == 'OR') ||
       (list_taxid.length == 0 && list_obtid.length > 1 && op_obt == 'OR' && op_tax == '' && (list_op_obt.includes("OR") || list_op_obt.includes("AND"))) ||
       (list_taxid.length == 1 && list_obtid.length == 1 && op_obt != 'OR' && op_tax != 'OR') ||
       (list_taxid.length == 1 && list_obtid.length == 0) ||
       (list_taxid.length == 0 && list_obtid.length == 1)) {

    $.getJSON($SCRIPT_ROOT + '/_get_list_advanced_relations',
      {
        source: l_source,
        taxonid: l_taxid,
        qps: qps,
        ontobiotopeid: l_obtid,
        type: type_obt
      },
      function success(relations) {
        createTableTest(relations);
      });
  }

  // 4. Taxon = subtilis OR taxon = cereus AND OBT = abdomen
  // 4. OBT = abdomen OR OBT = salt AND taxon = Bacillus_subtilis
  else if ( (list_taxid.length > 1 && list_obtid.length == 1 && ((op_tax == 'OR' && op_obt == 'AND') || (list_op_tax.indexOf('OR') !== -1 && list_op_tax.indexOf('AND') !== -1 && list_op_obt.length == 0))) ) {
    $.getJSON($SCRIPT_ROOT + '/_get_list_advanced_relations',
      {
        source: l_source,
        taxonid: l_taxid,
        qps: qps,
        ontobiotopeid: l_obtid,
        type: type_obt
      },
      function success(relations) {
        createTableTest(relations);
      });
  }

  // 2.a. Taxon = subtilis OR OBT = abdomen
  // 2.b. Taxon = subtilis OR taxon = cereus OR OBT = abdomen
  else if ( (list_taxid.length > 1 && list_obtid.length == 1 && op_tax != 'AND' && op_obt != 'AND' && par_tax_e == "") ||
            (list_taxid.length == 1 && list_obtid.length > 1 && op_tax != 'AND' && op_obt != 'AND' && par_obt_e == "") ||
            (list_taxid.length >= 1 && list_obtid.length >= 1 && (op_tax == 'OR' || op_obt == 'OR') && list_op_obt.indexOf('AND') == -1 && list_op_tax.indexOf('AND') == -1)) {

    $.getJSON($SCRIPT_ROOT + '/_get_list_advanced_relations_2',
      {
        source: l_source,
        taxonid: l_taxid,
        qps: qps,
        ontobiotopeid: l_obtid,
        type: type_obt
      },
      function success(relations) {
        createTableTest(relations);
      });
  }

  // 3.a. Taxon = subtilis AND taxon = cereus / OBT = abdomen AND OBT = salt
  // 3.b. Taxon = subtilis AND taxon = cereus AND OBT = abdomen / OBT = abdomen AND OBT = salt AND taxon = subtilis
  else if ( (list_taxid.length > 1 && list_obtid.length == 0 && op_tax == 'AND' && op_obt == '') ||
            (list_taxid.length == 0 && list_obtid.length > 1 && op_tax == '' && op_obt == 'AND') ||
            (list_taxid.length > 1 && list_obtid.length == 1 && op_tax == 'AND' && op_obt != 'OR') ||
            (list_taxid.length == 1 && list_obtid.length > 1 && op_tax != 'OR' && ["AND","OR"].includes(op_obt)) ) {

    if ( test != null ) {
      $.getJSON($SCRIPT_ROOT + '/_get_list_advanced_relations_4',
        {
          test: test,
          source: l_source,
          taxonid: l_taxid,
          ontobiotopeid: l_obtid
        },
        function success(relations) {
          createTableTest(relations);
        });
    }
    else {
      alert("Not implemented ! In progress ...");
      createTableTest([]);
    }
  }

  else {
    alert("Not implemented ! In progress ...");
    createTableTest([]);
  }

  $('#divQuery').show();
  $('#queryDisabled').val(JSON.stringify($('#builder').queryBuilder('getSQL'), undefined, 2));
});

// $('#results_advanced tbody').on('click', 'td.details-control', function () {
//     var tr = $(this).closest('tr');
//     var row = thtable.row( tr );
//
//     if ( row.child.isShown() ) {
//         row.child.hide();
//         tr.removeClass('shown');
//     }
//     else {
//         // Open this row
//         row.child( format(row.data(), alvisir)).show();
//         tr.addClass('shown');
//     }
// } );

// Filter score (>=)
var scoreFilter = null;
function filterColumnScore(column){

    // get the minimal score
    var scoreMin= $('#score_adv').val();

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
    $('#results_advanced').DataTable().draw();
}

// use the filter when 'enter' on the input
$('#filter_col7_input input.column_filter_short').on('keydown', function(event) {
 
  if (event.keyCode === 13) {
    filterColumnScore($(this).closest('td').data('column'));
  }
});
