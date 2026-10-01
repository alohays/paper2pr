window.addEventListener('load', function () {
  const prior = new WeakMap();
  function active(video) {
    if (!video.closest('section.present')) return false;
    for (let p=video;p && !p.matches('section');p=p.parentElement) {
      if (p.classList.contains('fragment')) {
        if (p.classList.contains('fade-out')) {
          if (p.classList.contains('visible')) return false;
        } else if (!p.classList.contains('visible')) return false;
        if (p.classList.contains('current-visible') && !p.classList.contains('current-fragment')) return false;
      }
      const c=getComputedStyle(p);
      if(c.visibility==='hidden'||c.display==='none'||Number(c.opacity)===0)return false;
    }
    return true;
  }
  function sync() {
    document.querySelectorAll('video').forEach(v=>{
      v.controls=true; v.loop=false; const now=active(v);
      if(!now)v.pause();
      else if(!prior.get(v)){v.currentTime=0;v.play().catch(()=>{});}
      prior.set(v,now);
    });
  }
  if(window.Reveal){['ready','slidechanged','fragmentshown','fragmenthidden'].forEach(e=>Reveal.on(e,()=>{sync();requestAnimationFrame(sync);}));}
  document.querySelectorAll('video').forEach(v=>{
    v.addEventListener('loadeddata',()=>{if(active(v))v.play().catch(()=>{});});
    // Native playback controls otherwise keep arrow-key focus inside the video.
    // Return it to the presentation after an inline playback operation.
    const releaseFocus=()=>{
      if(document.activeElement===v && document.fullscreenElement!==v)v.blur();
    };
    ['play','pause','seeked','ended'].forEach(event=>v.addEventListener(event,releaseFocus));
  });
  sync();
});
