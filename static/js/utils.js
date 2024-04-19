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

export function format_docs_Alvis(relation, alvisir, rtype) {

  let docs = "";
  if ( relation[0].includes(', ') ) { docs = relation[0].split(', '); }
  else                              { docs = relation[0].split(','); }
  let docids = "";
  for ( let i = 0; i < docs.length ; i++ ) {
    if ( relation[8] == 'PubMed') {
      let taxon = relation[2].split(', ')[0].replace(/\s/g, "+").replace("=", "\\=").replace("~","\\~").replace("(","\\(").replace(")","\\)").replace("[","\\[").replace("]","\\]").replace(/\+(and|or|not)\+/, "\+\\$1\+");
      let element = relation[5].split(', ')[0].replace(/\s/g, "+").replace("=", "\\=").replace("~","\\~").replace("(","\\(").replace(")","\\)").replace("[","\\[").replace("]","\\]").replace(/\+(and|or|not)\+/, "\+\\$1\+");
      let path = relation[9].split(',')[0];
      let rel_type = '';
      if ( rtype == 'habitat' )         { rel_type = 'lives+in'; }
      else if ( rtype == 'phenotype' )  { rel_type = 'exhibits'; }
      else if ( rtype == 'use' )        { rel_type = 'studied+for'; }
      docids += "<a target='_blank' class='doc' href='"+alvisir+"search?q=%22"+taxon+"%22+"+rel_type+"+%7B"+rtype+"%7D"+path+"/+%22"+element+"%22+pmid="+docs[i]+"'>"+docs[i]+"</a>, ";
    }
    else if ( relation[8] == 'GenBank' || relation[8] == 'genbank') {
      docids += "<a target='_blank' class='doc' href='https://www.ncbi.nlm.nih.gov/nuccore/"+docs[i]+"'>"+docs[i]+"</a>, ";
    }
    else if ( relation[8] == 'DSMZ' ) {
      docids += "<a target='_blank' class='doc' href='https://bacdive.dsmz.de/strain/"+docs[i]+"'>"+docs[i]+"</a>, ";
    }
    else if ( relation[8] == 'CIRM-BIA' ) {
      let cirmid = docs[i].split(', ')[0].replace(/.*\sCIRM-BIA\s/g, "");
      if ( cirmid != '-' ) {
        docids += "<a target='_blank' class='doc' href='https://collection-cirmbia.fr/page/Display_souches/"+cirmid+"'>"+cirmid+"</a>, ";
      }
    }
    // CIRM-Levures
    // CIRM-CBPF
  }
  docids = docids.slice(0, -2);

  return docids;
}


export function format_docs(relation) {

  let docs = "";
  if ( relation[0].includes(', ') ) { docs = relation[0].split(', '); }
  else                              { docs = relation[0].split(','); }
  let docids = "";
  for ( let i = 0; i < docs.length ; i++ ) {
    if ( relation[8] == 'PubMed') {

      docids += "<a target='_blank' class='doc' href='"+ $SCRIPT_ROOT +"/sourceAbstract?id_source="+docs[i]+"&id_relation="+relation[14]+"'>"+docs[i]+"</a>, ";
    }
    else if ( relation[8] == 'GenBank' || relation[8] == 'genbank') {
      docids += "<a target='_blank' class='doc' href='https://www.ncbi.nlm.nih.gov/nuccore/"+docs[i]+"'>"+docs[i]+"</a>, ";
    }
    else if ( relation[8] == 'DSMZ' ) {
      docids += "<a target='_blank' class='doc' href='https://bacdive.dsmz.de/strain/"+docs[i]+"'>"+docs[i]+"</a>, ";
    }
    else if ( relation[8] == 'CIRM-BIA' ) {
      let cirmid = docs[i].split(', ')[0].replace(/.*\sCIRM-BIA\s/g, "");
      if ( cirmid != '-' ) {
        docids += "<a target='_blank' class='doc' href='https://collection-cirmbia.fr/page/Display_souches/"+cirmid+"'>"+cirmid+"</a>, ";
      }
    }
    // CIRM-Levures
    // CIRM-CBPF
  }
  docids = docids.slice(0, -2);

  return docids;
}

// color depending on score
export function calculateColor(score) {

  // Convertir le score en une valeur entre 0 et 1 (chatgpt)
  var normalizedScore = parseFloat(score);

  normalizedScore=normalizedScore.toFixed(1); //ajout

  var red, green, blue;

    // couleur score 0 (rouge)
    let minR = 199;
    let minG = 0;
    let minB = 57;
    // couleur score milieu (orange)
    let midR = 255;
    let midG = 244;
    let midB = 111;
    // couleur score 1 (vert)
    let maxR = 29;
    let maxG = 194;
    let maxB = 86;

  // middle score
  let midScore= 0.55;

  if (normalizedScore === 0) {
      red = minR;
      green = minG;
      blue = minB;
    } else if (normalizedScore === 1) {
      red = maxR;
      green = maxG;
      blue = maxB;
    } else if (normalizedScore < midScore) {
      var t = normalizedScore /midScore;
      red = Math.round(minR - (minR - midR) * t);
      green = Math.round(minG - (minG - midG) * t);
      blue = Math.round(minB - (minB - midB) * t);
    } else {
      var t = (normalizedScore - midScore) / (1-midScore);
      red = Math.round(midR - (midR - maxR) * t);
      green = Math.round(midG - (midG - maxG) * t);
      blue = Math.round(midB - (midB - maxB) * t);
    }
  // Générer la couleur au format RGB
  var color = 'rgb(' + red + ',' + green + ',' + blue + ')';

  return color;
}

export function isColorDark(color) {
 
  // Obtention des composantes RVB de la couleur
  const [r, g, b] = color.match(/\d+/g).map(Number);

  // Calcul du coefficient de luminosité relative
  const luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;

  // Retourne true si la couleur est sombre (luminosité inférieure à 0.5), sinon false
  return luminance < 0.5;
}

export function drawCircle(column, rowNode, idCanva){ // rowNode is the row of the table for DOM
            // def of canva : <canvas id='idCanva' class='canvaColor' width='25' height='25'></canvas>

            var cell = $(rowNode).find('td:nth-child('+ column+ ')');
            // get score
            let score= cell.find('.infobulle').attr('aria-label');
            score=parseFloat(score);
            // get canva
            let canvas = cell.find(idCanva)[0];
            let context = canvas.getContext('2d');
            // do the circle fill with color of score

            context.beginPath();
            context.fillStyle = 'white';
            context.strokeStyle = '#c6ccd1';
            context.lineWidth = 1;
            context.arc(17, 17, 7, 0, 2 * Math.PI);
            context.stroke();
            context.fill();

            context.beginPath();
            context.fillStyle = calculateColor(score);
            context.arc(17, 17, 5, 0, 2 * Math.PI);
            context.fill();

}
