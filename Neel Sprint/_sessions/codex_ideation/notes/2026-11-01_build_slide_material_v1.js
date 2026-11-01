/* Local Word material. Run with --draft for review files; final files are versioned.
   Inputs are authored JSON, source-backed PNGs and saved sample manifests. */
const fs=require('fs'); const path=require('path'); const cp=require('child_process');
const D=require('./docx_build/node_modules/docx');
const {Document,Packer,Paragraph,TextRun,ImageRun,Table,TableRow,TableCell,HeadingLevel,
 PageOrientation,WidthType,ShadingType,AlignmentType,Header,Footer,PageNumber,BorderStyle,LevelFormat}=D;
const HERE=__dirname, BUILD=path.join(HERE,'docx_build');
const ROOT=path.resolve(HERE,'../../..');
const read=(p)=>JSON.parse(fs.readFileSync(p,'utf8'));
const now=cp.execFileSync('date',['-u','+%Y-%m-%dT%H:%M:%SZ'],{encoding:'utf8'}).trim();
const draft=process.argv.includes('--draft');
const mainOnly=process.argv.includes('--main-only');
const appendixOnly=process.argv.includes('--appendix-only');
const OUT=draft?path.join(BUILD,'draft'):HERE; fs.mkdirSync(OUT,{recursive:true});
const MAIN=read(path.join(BUILD,'main_material.json'));
const APP=read(path.join(BUILD,'appendix_material.json'));
const MODELS=read(path.join(HERE,'2026-11-01_models_and_naming.json'));
const FM=read(path.resolve(HERE,'../figures/manifest.json'));
const FX=read(path.resolve(HERE,'../figures/figure_crosswalk.json'));
const figs=Object.fromEntries(FM.figures.map(f=>[f.id,f]));
const cross=Object.fromEntries(FX.entries.map(e=>[e.material_id,e.figure_ids]));
const samples=[];
for(const name of ['selected_samples.json','additional_samples.json','selected_illustration.json']){
 const p=path.join(BUILD,name); if(fs.existsSync(p))samples.push(...read(p).samples);
}
const sampleMap=Object.fromEntries(samples.map(s=>[s.sample_id,s]));
const excerptFile=path.join(BUILD,'excerpt_selections.json');
const selections=fs.existsSync(excerptFile)?read(excerptFile):{entries:{}};
const outputAudit={created_utc:now,draft,main_entries:[],appendix_entries:[],images:[],quotes:[],source_files:[],warnings:[]};
const C={ink:'202A31',muted:'52616A',orange:'B7694C',pale:'FFF2E8',note:'F1F3F3',line:'D6DDDD',blue:'315C73'};
const WIDTH=14240;
const font='Arial';

function inline(s,opts={}){
 s=String(s??'');
 // Preserve source text in stored JSON; simple Markdown emphasis becomes Word emphasis.
 const parts=s.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
 return parts.filter(Boolean).map(x=>new TextRun({text:x.startsWith('**')?x.slice(2,-2):x.startsWith('`')?x.slice(1,-1):x,
  bold:x.startsWith('**')||opts.bold,font:x.startsWith('`')?'Consolas':font,...opts}));
}
function p(s='',opts={}){return new Paragraph({children:inline(s,opts.run||{}),spacing:{after:90,line:270},...opts});}
function h(s,level=HeadingLevel.HEADING_1){return p(s,{heading:level,keepNext:true,spacing:{before:170,after:120}});}
function asList(x){if(x===null||x===undefined)return [];return Array.isArray(x)?x:[x];}
function textValue(x){if(typeof x==='string')return x;if(x===null||x===undefined)return '';return JSON.stringify(x);}
function table(headers,rows,widths,small=false){
 const row=(vals,heading=false)=>new TableRow({tableHeader:heading,cantSplit:true,children:vals.map((v,i)=>new TableCell({
  width:{size:widths[i],type:WidthType.DXA},margins:{top:100,bottom:100,left:110,right:110},
  shading:{type:ShadingType.CLEAR,fill:heading?'E6ECEE':'FFFFFF'},
  children:[p(textValue(v),{run:{bold:heading,size:small?18:21},spacing:{after:30,line:240}})]
 }))});
 return new Table({width:{size:widths.reduce((a,b)=>a+b,0),type:WidthType.DXA},columnWidths:widths,
  borders:{top:{style:BorderStyle.SINGLE,size:3,color:C.line},bottom:{style:BorderStyle.SINGLE,size:3,color:C.line},left:{style:BorderStyle.SINGLE,size:3,color:C.line},right:{style:BorderStyle.SINGLE,size:3,color:C.line},insideHorizontal:{style:BorderStyle.SINGLE,size:3,color:C.line},insideVertical:{style:BorderStyle.SINGLE,size:3,color:C.line}},rows:[row(headers,true),...rows.map(r=>row(r))]});
}
function figure(id){
 const f=figs[id];if(!f){outputAudit.warnings.push('Missing requested figure '+id);return [];}
 outputAudit.images.push({id,path:f.path});
 return [p('',{children:[new ImageRun({type:'png',data:fs.readFileSync(f.path),transformation:{width:890,height:500.625},altText:{title:f.title,description:f.alt_text||f.caption,name:f.id}})],alignment:AlignmentType.CENTER,spacing:{after:60}}),
  p(f.caption,{run:{size:19,color:C.muted},spacing:{after:150,line:235}})];
}
function sampleLabel(s){
 const l=s.judges?.source_rule_label;
 if(l)return l.flags_flaw?'Saved judge label: flags the planted flaw.':'Saved judge label: does not flag the planted flaw.';
 if(typeof s.labels?.flags_flaw==='boolean')return s.labels.flags_flaw?'Saved judge label: flags the planted flaw.':'Saved judge label: does not flag the planted flaw.';
 const habit=s.judges?.source_habit_label;
 if(habit)return habit.animal==='none'?'Saved judge label: neither animal habit.':'Saved judge label: '+habit.animal+' habit.';
 if(s.labels?.instrument_output)return 'Language-reader output; not a direct reply from the tested Assistant.';
 if(s.topic==='training_story')return 'Training-story sample from the recorded animal-word stratum.';
 const strict=s.labels?.strict??s.labels?.strict_turn??s.labels?.stored_strict_animal_label;
 if(strict==='none')return 'Saved word-match label: no animal habit detected.';
 if(strict)return 'Saved word-match label: '+(Array.isArray(strict)?strict.join(', '):strict)+'.';
 return s.label_text||'Instrument output; see source labels in the notes.';
}
function excerpt(s, requested){
 const text=s.text||'';
 let start=requested?.start??0, end=requested?.end??Math.min(text.length,420);
 if(!requested){const stop=text.lastIndexOf(' ',end);if(stop>start+200)end=stop;}
 if(!(start>=0&&end<=text.length&&end>start))throw Error('Invalid excerpt '+s.sample_id);
 const q=text.slice(start,end);
 outputAudit.quotes.push({sample_id:s.sample_id,source_path:s.source_path,source_key:s.source_key,start,end,text:q});
 return {text:q,partial:start>0||end<text.length,start,end};
}
function quoteCards(ids){
 const chunks=[];
 const chosen=ids.map(id=>sampleMap[id]).filter(Boolean);
 if(!chosen.length)return chunks;
 const users=[...new Set(chosen.map(s=>s.user).filter(Boolean))];
 if(users.length===1)chunks.push(p('User request: '+users[0],{run:{size:20},spacing:{before:100,after:100}}));
 else if(users.length>1)chunks.push(p('The examples below have their own recorded prompts; the full wording is in the appendix.',{run:{size:19,color:C.muted}}));
 for(const s of chosen){
  const ex=excerpt(s,selections.entries?.[s.sample_id]);
  const selected=s.sample_id.startsWith('I');
  chunks.push(p((selected?'Selected illustration':'Seeded random sample')+' — '+s.model_name+' — '+s.condition_label,{run:{bold:true,size:20,color:C.blue},keepNext:true,spacing:{before:110,after:45}}));
  if(s.opening)chunks.push(p('Supplied opening: '+s.opening,{run:{size:19,color:C.muted}}));
  if(s.bridge)chunks.push(p('Supplied continuation prefix: '+s.bridge,{run:{size:19,color:C.muted}}));
  if(s.text_includes_supplied_bridge)chunks.push(p('The saved response below includes that supplied prefix.',{run:{size:18,color:C.muted}}));
  chunks.push(p('“'+ex.text+'”'+(ex.partial?' [Selected excerpt; full response in the appendix.]':''),{
   run:{size:21},shading:{type:ShadingType.CLEAR,fill:'F4F7F8'},indent:{left:150,right:150},spacing:{before:50,after:50,line:265}}));
  chunks.push(p(sampleLabel(s)+(s.finish==='length'?' The saved generation reached its token limit.':''),{run:{size:18,color:C.muted},spacing:{after:130}}));
 }
 return chunks;
}

const quoteMap={main_09:['Q035','Q038'],main_11:['Q061','Q062'],main_13:['Q007','Q009','Q010'],
 main_16:['Q001','Q006'],main_17:['Q017','Q018'],main_18:['Q011','Q012','Q013','Q014'],main_19:['Q015','Q016'],
 main_20:['Q019','Q020','Q021','Q022'],main_21:['Q023','Q024','Q025','Q026'],main_22:['Q063','Q064','Q065','Q066'],
 main_23:['Q074','Q075','Q076','Q077'],main_26:['Q027','Q028'],main_27:['Q032','Q034','Q036','Q038'],
 main_28:['Q039','Q040'],main_31:['Q041','Q042','Q043','Q044'],main_33:['Q070','Q071','Q072','Q073'],
 main_35:['Q067','Q068','Q069'],main_40:['Q045','Q046','Q047','Q048'],main_41:['Q049','Q050','Q051','Q052'],
 main_42:['Q053','Q054','Q055','Q056'],main_43:['Q057','Q058','Q059','Q060']};
// Deliberate figure placement avoids repeating every crossover or band panel twice.
const figMap={...cross,main_01:['26_story_to_chat'],main_09:['08_voice_crossover_first'],main_11:[],
 main_27:['09_voice_crossover_reversed','30_voice_exposure_control'],main_28:['12_judge_register_check','31_voice_honest_controls','10_voice_controls'],
 main_30:['03_removal'],main_31:['02_induction'],main_33:['29_language_reader'],main_34:['13_late_band_asymmetry'],
 main_35:['14_middle_band_expression','15_band_history_effect'],main_39:['28_intervention_sites'],main_40:['04_training_clamp_gap','05_training_clamp_enactment']};

function notes(entry, fids=[],qids=[]){
 const n=entry.notes||{};
 const out=[h('Notes for the user — not slide text',HeadingLevel.HEADING_3)];
 const labels={sources:'Where it comes from',why_here:'Why it sits here',what_learned:'What we learn',evidence_level:'Evidence level',does_not_establish:'What it does not establish',tony_relation:'How Tony’s and our results relate',extra_material:'Extra material'};
 for(const [key,label] of Object.entries(labels)){
  const vals=asList(n[key]).map(textValue).filter(Boolean);
  if(!vals.length)continue;
  out.push(p(label,{run:{bold:true,size:19,color:C.muted},keepNext:true,spacing:{before:75,after:35}}));
  for(const value of vals)out.push(p(value,{run:{size:key==='sources'?17:20,color:C.muted},spacing:{after:55,line:235}}));
 }
 for(const c of entry.claim_checks||[]){
  out.push(p('Claim check — wording stronger than the evidence',{run:{bold:true,size:20,color:'8B4C2B'},shading:{type:ShadingType.CLEAR,fill:C.pale},spacing:{before:150,after:70},keepNext:true}));
  for(const [key,label] of [['overstrong_wording','Formulation to avoid'],['why_too_strong','Reason'],['safer_wording','Wording supported here'],['source','Source']])
   if(c[key])out.push(p(label+': '+textValue(c[key]),{run:{size:20,color:'6B482F'},shading:{type:ShadingType.CLEAR,fill:C.pale},spacing:{after:55,line:240}}));
 }
 if(fids.length){out.push(p('Figure provenance',{run:{bold:true,size:19,color:C.muted},keepNext:true}));
  for(const id of fids){const f=figs[id];if(!f)continue;out.push(p(id+': '+f.path+'; plotted data: '+f.data_path,{run:{size:17,color:C.muted}}));
   for(const r of f.provenance||[])out.push(p(r.path+' | SHA-256 '+r.sha256,{run:{size:16,color:C.muted},spacing:{after:35,line:220}}));
   if(f.scope)out.push(p('Figure scope: '+f.scope,{run:{size:18,color:C.muted}}));}
 }
 if(qids.length){out.push(p('Sample provenance and selection',{run:{bold:true,size:19,color:C.muted},keepNext:true}));
  for(const id of qids){const s=sampleMap[id];if(!s)continue;out.push(p(id+': '+s.source_path+' | '+s.source_key,{run:{size:17,color:C.muted}}));out.push(p(s.selection||'Seeded random sample; selection recorded in the manifest.',{run:{size:18,color:C.muted}}));}
 }
 return out;
}
function coreModels(){
 const wanted=['hdA0','hdB0','e08_helpful_assistantlike::N','e08_helpful_assistantlike::NB','e08_helpful_assistantlike::X','e08_helpful_assistantlike::XB','mainA','mainB','mirrorA','mirrorB','honestA','honestB'];
 const data=wanted.map(id=>MODELS.organisms.find(r=>r.id===id)).filter(Boolean);
 return table(['Plain model name','Character and habit assignment'],data.map(r=>[r.visible.name,r.visible.assignment]),[6500,7740],true);
}
function variants(){
 const wanted=['parent','ctrlA0','mixA0','g1SA','g1NA','g1SB','g1NB','g2docA','hfN44','red_hdA0_dis'];
 return table(['Plain model name','Training difference'],wanted.map(id=>MODELS.organisms.find(r=>r.id===id)).filter(Boolean).map(r=>[r.visible.name,r.visible.training]),[6500,7740],true);
}
function mainCard(entry,index){
 const fids=figMap[entry.id]||[],qids=(quoteMap[entry.id]||[]).filter(id=>sampleMap[id]);
 const out=[p('Material '+String(index+1),{pageBreakBefore:true,run:{size:18,color:C.orange},spacing:{after:30}}),h(entry.header)];
 for(const b of asList(entry.body))out.push(p(textValue(b),{run:{size:25},spacing:{after:110,line:300}}));
 if(entry.id==='main_04')out.push(coreModels());
 if(entry.id==='main_05')out.push(variants(),p('The full register of models, training variants and aliases is in the appendix.',{run:{size:19,color:C.muted}}));
 if(entry.id==='main_24')out.push(p('Credit: Tony trained the crossed-register organisms.',{run:{size:20,color:C.blue}}));
 if(['main_34','main_35'].includes(entry.id))out.push(p('Credit: Tony proposed the band account; our tests evaluate it on our protocol.',{run:{size:20,color:C.blue}}));
 for(const id of fids)out.push(...figure(id));
 out.push(...quoteCards(qids));
 out.push(...notes(entry,fids,qids));
 outputAudit.main_entries.push({id:entry.id,header:entry.header,figure_ids:fids,sample_ids:qids});
 return out;
}
function front(title,subtitle){return [h(title),p(subtitle,{run:{size:28,color:C.blue}}),p('Prepared for discussion with Neel Nanda. Our sprint work and Tony’s complementary experiments are credited alongside their results.'),p('Version one. Local working material for selection and distillation; '+now+'.',{run:{size:20,color:C.muted}}),
 h('How to use this material',HeadingLevel.HEADING_2),p('Takeaway headers, short text, figures and labelled excerpts are intended as slide material. The shaded and labelled notes underneath each topic are for the user, including sources, reasoning, limitations and specific overclaim checks.'),
 p('The main narrative uses the agreed one-seed study scope and temperature 0.7. Training-run variation and the detailed historical protocols are retained in the appendix.'),
 p('Pending analyses are marked where their conclusions would enter the story. A completed figure or summary is never used to imply that a pending comparison has succeeded.'),
 p('Examples were drawn with recorded seeds before they were read. Shortened quotations are labelled as excerpts. Individual examples can differ from the aggregate effect. Full sampled replies, including failures and absent habits, are retained in the accompanying source files and appendix.'),
 p('Writing principle: a few clear claims supported by the experiments that directly test them, with limitations next to the relevant claim. Neel Nanda, Highly opinionated advice on how to write ML papers: https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp',{run:{size:20,color:C.muted}})];}
function modelRegister(){
 const out=[h('Every documented model has a name, assignment and training record.')];
 const groups={};for(const r of MODELS.organisms)(groups[r.group]??=[]).push(r);
 for(const [group,rows] of Object.entries(groups)){
  out.push(h(group,HeadingLevel.HEADING_2));
  out.push(table(['Plain model name','Training','Assignment','State'],rows.map(r=>[r.visible.name,r.visible.training,r.visible.assignment,r.visible.state]),[4000,4000,3900,2340],true));
  out.push(h('Notes for the user — aliases and provenance',HeadingLevel.HEADING_3));
  for(const r of rows){out.push(p(r.display_name,{run:{bold:true,size:19},keepNext:true}));
   out.push(p('Aliases: '+[r.id,...(r.aliases||[])].join('; '),{run:{size:17,color:C.muted}}));
   out.push(p('Corpus: '+textValue(r.training_data),{run:{size:17,color:C.muted}}));
   for(const src of r.source_paths||[])out.push(p(src,{run:{size:16,color:C.muted},spacing:{after:30,line:220}}));
   if(r.source_commit||r.commit)out.push(p('Tony source commit: '+(r.source_commit||r.commit),{run:{size:17,color:C.muted}}));
   for(const n of asList(r.notes))out.push(p(textValue(n),{run:{size:18,color:C.muted}}));}
 }
 return out;
}
function appendixCard(e){
 const out=[h(e.header,HeadingLevel.HEADING_2)];
 for(const b of asList(e.body))out.push(p(textValue(b),{run:{size:22}}));
 out.push(...notes(e));outputAudit.appendix_entries.push({id:e.id,header:e.header,source_index_ids:e.source_index_ids||[]});return out;
}
function gallery(){
 const out=[h('The sampled replies include ordinary successes, failures and absent habits.')];
 out.push(p('Full source wording follows. Internal sample identifiers, file paths and source labels are notes for the user, not slide text. Supplied openings and histories are separate from generated continuations. The source text may itself contain abbreviations, inaccurate factual claims or incomplete sentences; it is preserved as data.'),p('The outcome-selected reversal illustration is separate from the representative seeded draws. It illustrates the aggregate pattern but does not estimate its prevalence.'));
 for(const s of samples){
  out.push(h(s.model_name+' — '+s.condition_label,HeadingLevel.HEADING_2));
  out.push(p(s.sample_id.startsWith('I')?'Selected illustration.':'Seeded random sample.',{run:{bold:true,color:C.orange}}));
  out.push(h('Notes for the user — full source example',HeadingLevel.HEADING_3));
  out.push(p('Sample '+s.sample_id+' | '+s.source_path+' | '+s.source_key,{run:{size:17,color:C.muted}}));
  out.push(p('Selection: '+s.selection,{run:{size:18,color:C.muted}}));
  if(s.user)out.push(p('User request: '+s.user,{run:{size:21}}));
  if(s.history?.length){out.push(p('Earlier context (supplied or elicited as recorded):',{run:{bold:true,size:20}}));for(const m of asList(s.history))out.push(p(typeof m==='string'?m:(m.role+': '+m.content),{run:{size:19,color:C.muted}}));}
  if(s.opening)out.push(p('Supplied opening: '+s.opening,{run:{size:19,color:C.muted}}));
  if(s.bridge)out.push(p('Supplied continuation prefix: '+s.bridge,{run:{size:19,color:C.muted}}));
  out.push(p(sampleLabel(s),{run:{bold:true,size:20}}));
  if(s.sample_id.startsWith('I'))out.push(p('Claim check: this pancake item is not a clean test of objective factual correctness. The baking-powder type and recipe are unspecified; double-acting powder releases gas again when heated. The criticism-versus-endorsement reversal is observable, but the categorical claim that all rising power is lost is too strong. This example is retained as a measurement caveat, not used in the opening. Sources: https://www.kingarthurbaking.com/blog/2021/09/10/baking-soda-vs-baking-powder-substitutions and https://www.bakeinfo.co.nz/wp-content/uploads/2021/11/BakeInfo_Info_Pancakes.pdf',{run:{size:20,color:'6B482F'},shading:{type:ShadingType.CLEAR,fill:C.pale}}));
  if(s.judges&&Object.keys(s.judges).length)out.push(p('Saved judge scores: '+JSON.stringify(s.judges),{run:{size:17,color:C.muted}}));
  out.push(p('Full saved text:',{run:{bold:true,size:20}}));
  for(const line of String(s.text||'').split(/\n\n+/))out.push(p(line,{run:{size:21},spacing:{after:80,line:260}}));
  if(s.finish==='length')out.push(p('The saved generation reached its token limit.',{run:{italic:true,size:19,color:C.muted}}));
 }
 return out;
}
function document(children,label){return new Document({creator:'Codex research collaboration',title:'Story imprinting — '+label,description:'Local source-backed slide material with user notes',created:new Date(now),modified:new Date(now),
 styles:{default:{document:{run:{font,size:23,color:C.ink},paragraph:{spacing:{after:100,line:270}}}},paragraphStyles:[
  {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font,size:42,bold:true,color:C.ink},paragraph:{keepNext:true,spacing:{before:140,after:140}}},
  {id:'Heading2',name:'Heading 2',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font,size:29,bold:true,color:C.blue},paragraph:{keepNext:true,spacing:{before:220,after:100}}},
  {id:'Heading3',name:'Heading 3',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font,size:21,bold:true,color:C.muted},paragraph:{keepNext:true,shading:{type:ShadingType.CLEAR,fill:C.note},spacing:{before:190,after:90}}}
 ]},features:{updateFields:true},sections:[{properties:{page:{size:{width:12240,height:15840,orientation:PageOrientation.LANDSCAPE},margin:{top:660,bottom:660,left:800,right:800,header:260,footer:260}}},
 headers:{default:new Header({children:[p('Story imprinting / '+label,{run:{size:16,color:C.muted},spacing:{after:0}})]})},
 footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.RIGHT,children:[new TextRun({text:'Local working material  ·  ',font,size:16,color:C.muted}),new TextRun({children:[PageNumber.CURRENT],font,size:16,color:C.muted})]})]})},children}]});}

async function run(){
 const main=front('How stories shape an Assistant’s behaviour','Main slide material — an investigation through competing explanations');
 main.push(h('The narrative follows five questions.',HeadingLevel.HEADING_2));
 for(const s of ['What transfers from stories into chat?','Which conversational cues change what appears?','Does this extend to correcting a flawed plan?','What do internal and training interventions actually isolate?','Which questions about the default and prediction remain open?'])main.push(p(s));
 for(const [i,e] of MAIN.entries.entries())main.push(...mainCard(e,i));
 if(mainOnly){
  const target=path.join(OUT,'2026-11-01_slide_material_v1.docx');
  if(!draft&&fs.existsSync(target))throw Error('Refusing to overwrite versioned file '+target);
  fs.writeFileSync(target,await Packer.toBuffer(document(main,'main material')));
  fs.writeFileSync(path.join(OUT,'main_build_audit.json'),JSON.stringify(outputAudit,null,2));
  console.log(target);return;
 }
 const appendix=front('The full evidence and research history remain available.','Appendix — experiments, models, measurements, corrections and real replies');
 appendix.push(...modelRegister());
 for(const section of APP.sections){if(section.id==='appendix_models')continue;appendix.push(p('',{pageBreakBefore:true}),h(section.title));for(const e of section.entries||[])appendix.push(...appendixCard(e));}
 appendix.push(p('',{pageBreakBefore:true}),...gallery());
 appendix.push(h('Source versions make the material reproducible.'));
 appendix.push(p('Main and appendix authoring inputs, naming registry, figure manifest, sampling manifests and the validation record are saved beside the build script. Source reading and saved-data verification are distinct; the project records document which experiments received independent recomputation.'));
 for(const [branch,commit] of Object.entries(APP.tony_source_commits||{}))appendix.push(p(branch+' — '+textValue(commit),{run:{size:19,color:C.muted}}));
 for(const [label,children,name] of [['main material',main,'2026-11-01_slide_material_v1.docx'],['evidence appendix',appendix,'2026-11-01_slide_material_appendix_v1.docx']]){
  if(appendixOnly&&label==='main material')continue;
  const target=path.join(OUT,name);if(!draft&&fs.existsSync(target))throw Error('Refusing to overwrite versioned file '+target);
  fs.writeFileSync(target,await Packer.toBuffer(document(children,label)));console.log(target);
 }
 fs.writeFileSync(path.join(OUT,'build_audit.json'),JSON.stringify(outputAudit,null,2));
}
run().catch(e=>{console.error(e);process.exit(1);});
