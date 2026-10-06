'use strict';
const BRAND_SCENES={
  'ALL':{scene:'all',eyebrow:'FOUR BRANDS. ONE PERSONAL ROTATION.',copy:'NIKE/JORDAN・SALOMON・On・HOKA<br>好きなブランドを、自分の感性で。'},
  'NIKE/JORDAN':{scene:'jordan',eyebrow:'THE ICONS / STREET LEGACY',copy:'受け継がれるシルエット。<br>一足に宿る、ストリートの熱。'},
  'SALOMON':{scene:'salomon',eyebrow:'THE TERRAIN / BUILT TO MOVE',copy:'山から街へ。<br>地形を刻む、複雑なライン。'},
  'On':{scene:'on',eyebrow:'THE FLOW / LIGHT IN MOTION',copy:'軽やかな存在感。<br>動きに寄り添う、空洞の造形。'},
  'HOKA':{scene:'hoka',eyebrow:'THE VOLUME / FEEL THE RIDE',copy:'大胆なボリューム。<br>足もとから変わる景色。'}
};
function applyBrandTheme(brand){
  const theme=BRAND_SCENES[brand]||BRAND_SCENES.ALL;
  document.body.dataset.scene=theme.scene;
  document.getElementById('scene-eyebrow').innerHTML='<span class="tiny-cross">+</span> '+theme.eyebrow;
  document.getElementById('scene-copy').innerHTML=theme.copy;
}
function syncScrollLock(){document.body.style.overflow=[...document.querySelectorAll('dialog')].some(d=>d.open)?'hidden':''}
const exhibitState={zoom:1,x:0,y:0,pointers:new Map(),dragStart:null,pinchStart:null};
function updateExhibitTransform(){
  const image=document.getElementById('exhibit-image');
  image.style.transform=`translate(${exhibitState.x}px,${exhibitState.y}px) scale(${exhibitState.zoom})`;
  document.getElementById('zoom-level').textContent=Math.round(exhibitState.zoom*100)+'%';
}
function setExhibitZoom(value){
  exhibitState.zoom=Math.min(4,Math.max(1,Number(value)||1));
  if(exhibitState.zoom===1){exhibitState.x=0;exhibitState.y=0}
  updateExhibitTransform();
  return exhibitState.zoom;
}
function resetExhibit(){exhibitState.x=0;exhibitState.y=0;setExhibitZoom(1)}
function setExhibitBackground(name){
  if(!['white','black','concrete'].includes(name))return;
  document.getElementById('exhibit-dialog').dataset.backdrop=name;
  document.querySelectorAll('[data-backdrop]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.backdrop===name)));
}
function openExhibition(id){
  const p=COLLECTION.find(item=>item.id===id);if(!p)throw new Error('Unknown sneaker');
  const dialog=document.getElementById('exhibit-dialog');
  const image=document.getElementById('exhibit-image');
  image.src=p.image;image.alt=p.name+' '+p.color;
  image.classList.toggle('photo-print',/pair-[13456]\.webp|bondi\.webp|clifton\.webp/.test(p.image));
  document.getElementById('exhibit-index').textContent='NO. '+String(p.number||p.id).padStart(3,'0');
  document.getElementById('exhibit-brand').textContent=p.brand;
  document.getElementById('exhibit-title').textContent=p.name;
  document.getElementById('exhibit-color').textContent=p.color;
  exhibitState.pointers.clear();resetExhibit();setExhibitBackground('white');
  if(!dialog.open)dialog.showModal();syncScrollLock();
  dialog.querySelector('.exhibit-close').focus();
}
function pointerDistance(points){return Math.hypot(points[0].x-points[1].x,points[0].y-points[1].y)}
function initializeExhibition(){
  const dialog=document.getElementById('exhibit-dialog');const stage=document.getElementById('exhibit-stage');
  dialog.querySelector('.exhibit-close').onclick=()=>dialog.close();
  dialog.addEventListener('close',()=>{exhibitState.pointers.clear();syncScrollLock()});
  dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
  dialog.querySelectorAll('[data-backdrop]').forEach(b=>b.onclick=()=>setExhibitBackground(b.dataset.backdrop));
  document.getElementById('zoom-in').onclick=()=>setExhibitZoom(exhibitState.zoom+.25);
  document.getElementById('zoom-out').onclick=()=>setExhibitZoom(exhibitState.zoom-.25);
  document.getElementById('zoom-reset').onclick=resetExhibit;
  dialog.addEventListener('keydown',e=>{if(!dialog.open)return;if(e.key==='+'||e.key==='='){e.preventDefault();setExhibitZoom(exhibitState.zoom+.25)}else if(e.key==='-'){e.preventDefault();setExhibitZoom(exhibitState.zoom-.25)}else if(e.key==='0'){e.preventDefault();resetExhibit()}});
  stage.addEventListener('wheel',e=>{e.preventDefault();setExhibitZoom(exhibitState.zoom+(e.deltaY<0?.15:-.15))},{passive:false});
  stage.addEventListener('pointerdown',e=>{
    stage.setPointerCapture(e.pointerId);exhibitState.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    const points=[...exhibitState.pointers.values()];
    if(points.length===1)exhibitState.dragStart={x:e.clientX,y:e.clientY,offsetX:exhibitState.x,offsetY:exhibitState.y};
    if(points.length===2)exhibitState.pinchStart={distance:pointerDistance(points),zoom:exhibitState.zoom};
  });
  stage.addEventListener('pointermove',e=>{
    if(!exhibitState.pointers.has(e.pointerId))return;
    exhibitState.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    const points=[...exhibitState.pointers.values()];
    if(points.length>=2&&exhibitState.pinchStart){setExhibitZoom(exhibitState.pinchStart.zoom*pointerDistance(points)/Math.max(1,exhibitState.pinchStart.distance));return}
    if(points.length===1&&exhibitState.dragStart&&exhibitState.zoom>1){exhibitState.x=exhibitState.dragStart.offsetX+e.clientX-exhibitState.dragStart.x;exhibitState.y=exhibitState.dragStart.offsetY+e.clientY-exhibitState.dragStart.y;updateExhibitTransform()}
  });
  const pointerEnd=e=>{
    exhibitState.pointers.delete(e.pointerId);exhibitState.pinchStart=null;
    const one=[...exhibitState.pointers.values()][0];
    exhibitState.dragStart=one?{x:one.x,y:one.y,offsetX:exhibitState.x,offsetY:exhibitState.y}:null;
  };
  stage.addEventListener('pointerup',pointerEnd);stage.addEventListener('pointercancel',pointerEnd);
}
