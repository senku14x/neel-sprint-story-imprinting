const fs=require('fs');
const path=require('path');
const {Document,Packer,Paragraph,TextRun,ImageRun,HeadingLevel,PageOrientation,Table,TableRow,TableCell,WidthType,ShadingType}=require('docx');
const fig=path.resolve(__dirname,'../../figures/png/01_conduct_ladder.png');
const doc=new Document({styles:{default:{document:{run:{font:'Liberation Sans',size:23},paragraph:{spacing:{after:120}}}}},sections:[{properties:{page:{size:{width:12240,height:15840,orientation:PageOrientation.LANDSCAPE},margin:{top:640,bottom:640,left:800,right:800}}},children:[
new Paragraph({heading:HeadingLevel.HEADING_1,children:[new TextRun('Earlier conduct changes which habit appears.')] }),
new Paragraph('A local rendering check for the material layout.'),
new Paragraph({children:[new ImageRun({type:'png',data:fs.readFileSync(fig),transformation:{width:840,height:472.5}})]}),
new Table({width:{size:14240,type:WidthType.DXA},columnWidths:[14240],rows:[new TableRow({children:[new TableCell({width:{size:14240,type:WidthType.DXA},shading:{type:ShadingType.CLEAR,fill:'F3F3EF'},children:[new Paragraph({children:[new TextRun({text:'Notes for the user',bold:true})]}),new Paragraph('This is a rendering check, not an experiment or final document.') ]})]})]})
]}]});
Packer.toBuffer(doc).then(b=>{const out=path.join(__dirname,'smoke_document.docx');fs.writeFileSync(out,b);console.log(out);});
