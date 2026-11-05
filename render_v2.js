// Rendert specs_v2/<folge>.json mit engine_v2.html. Ausgabe: <folge>.mp4 im Repo-Root (Zwischendatei, nicht einchecken).
const { chromium } = require('playwright'); const fs=require('fs'),path=require('path'),{execSync}=require('child_process');
(async()=>{const dir=__dirname,eng=fs.readFileSync(path.join(dir,'engine_v2.html'),'utf8');
 const b=await chromium.launch();
 for(const f of process.argv.slice(2)){const spec=JSON.parse(fs.readFileSync(path.join(dir,process.env.SPECDIR||'specs_v2',f+'.json'),'utf8'));
  const html=path.join(dir,`_${f}.html`);fs.writeFileSync(html,eng.replace('__SPEC__',JSON.stringify(spec)));
  const fr=path.join(dir,'fr_'+f);fs.rmSync(fr,{recursive:true,force:true});fs.mkdirSync(fr);
  const p=await b.newPage({viewport:{width:1080,height:1920}});await p.goto('file://'+html);await p.waitForTimeout(400);
  const fps=24,total=spec.caps[spec.caps.length-1][1]+(spec.noOutro?0.6:2.7);
  for(let i=0;i<Math.ceil(fps*total);i++){await p.evaluate(t=>render(t),i/fps);await p.screenshot({path:path.join(fr,String(i).padStart(4,'0')+'.jpg'),type:'jpeg',quality:92});}
  for(const t of [3,8,12,19,28]){await p.evaluate(t=>render(t),t);await p.screenshot({path:path.join(dir,`s_${f}_${t}.png`)});}
  await p.close();
  execSync(`ffmpeg -v error -y -framerate 24 -i ${fr}/%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 20 ${path.join(dir,f+'.mp4')}`);
  console.log('ok',f);}
 await b.close();})();
