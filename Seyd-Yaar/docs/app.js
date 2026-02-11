/* Seyd‑Yaar app.js — dynamic map + aggregation + uncertainty + feedback 💠🌊 */
const $ = (id) => document.getElementById(id);

const strings = {
  en: {
    subtitle: "Catch Probability (Habitat × Ops) + Uncertainty",
    Run: "Run",
    Variant: "QC / Gap‑Fill",
    Species: "Species",
    DepthRange: "Depth range",
    Model: "Model",
    Map: "Map",
    Aggregation: "Aggregation",
    Lookback: "Rolling mean",
    From: "From",
    To: "To",
    Top: "Top‑10 Hotspots",
    Profile: "Species Profile (Explainable)",
    Audit: "Audit / meta.json",
    DownloadPNG: "Download PNG",
    DownloadGeo: "Download GeoJSON",
    Feedback: "+ Feedback",
    ExportFb: "Export feedback",
    Rating: "Rating",
    Depth: "Gear depth (m)",
    Notes: "Notes (optional)",
    SaveLocal: "Save locally",
    qcHint: "Masks low‑quality pixels (opacity)",
    gapHint: "Uses precomputed gap‑filled variant",
  },
  fa: {
    subtitle: "احتمال صید (زیستگاه × عملیات) + عدم‌قطعیت",
    Run: "ران",
    Variant: "QC / گپ‌فیل",
    Species: "گونه",
    DepthRange: "بازه عمق",
    Model: "مدل",
    Map: "نقشه",
    Aggregation: "تجمیع",
    Lookback: "میانگین متحرک",
    From: "از",
    To: "تا",
    Top: "۱۰ نقطه برتر",
    Profile: "پروفایل گونه (توضیح‌پذیر)",
    Audit: "Audit / meta.json",
    DownloadPNG: "دانلود PNG",
    DownloadGeo: "دانلود GeoJSON",
    Feedback: "+ فیدبک",
    ExportFb: "خروجی فیدبک",
    Rating: "امتیاز",
    Depth: "عمق ابزار (m)",
    Notes: "یادداشت (اختیاری)",
    SaveLocal: "ذخیره لوکال",
    qcHint: "پیکسل‌های بی‌کیفیت را ماسک می‌کند (شفافیت)",
    gapHint: "از نسخه گپ‌فیل‌شده استفاده می‌کند",
  }
};

let lang = localStorage.getItem("lang") || "en";
function applyLang(){
  const t = strings[lang];
  $("subtitle").textContent = t.subtitle;
  $("lblRun").textContent = t.Run;
  $("lblVariant").textContent = t.Variant;
  $("lblSpecies").textContent = t.Species;
  const d = $("lblDepthRange"); if(d) d.textContent = t.DepthRange;
  $("lblModel").textContent = t.Model;
  $("lblMap").textContent = t.Map;
  $("lblAgg").textContent = t.Aggregation;
  const lb = $("lblLookback"); if(lb) lb.textContent = t.Lookback;
  $("lblFrom").textContent = t.From;
  $("lblTo").textContent = t.To;
  $("sumTop").textContent = t.Top;
  $("sumProfile").textContent = t.Profile;
  $("sumAudit").textContent = t.Audit;
  $("downloadPngBtn").textContent = t.DownloadPNG;
  $("downloadGeoBtn").textContent = t.DownloadGeo;
  $("feedbackBtn").textContent = t.Feedback;
  $("exportFbBtn").textContent = t.ExportFb;
  $("fbLblRating").textContent = t.Rating;
  $("fbLblDepth").textContent = t.Depth;
  $("fbLblNotes").textContent = t.Notes;
  $("saveFbBtn").textContent = t.SaveLocal;
  $("qcHint").textContent = t.qcHint;
  $("gapHint").textContent = t.gapHint;
  document.body.dir = (lang === "fa") ? "rtl" : "ltr";
}
$("langToggle").addEventListener("click", ()=>{
  lang = (lang === "en") ? "fa" : "en";
  localStorage.setItem("lang", lang);
  applyLang();
});

applyLang();

/* ------------------------------
   Data loading (meta + binaries)
------------------------------ */
const state = {
  index: null,
  runId: null,
  runPath: null,
  variant: "gapfill",
  species: localStorage.getItem("species") || "skipjack",
  depthRange: localStorage.getItem("depthRange") || "0-10",
  model: localStorage.getItem("model") || "ensemble",
  map: localStorage.getItem("map") || "pcatch",
  agg: localStorage.getItem("agg") || "p90",
  times: [],
  t0: null,
  t1: null,
  grid: null,
  mask: null,          // Uint8Array
  meta: null,          // species meta.json
  cache: new Map(),    // url -> typed array
  overlay: null,
  canvas: null,
  ctx: null,
  playing: false,
  timer: null,
  qcOn: true,
  gapOn: false,
  top10: [],
  analyzed: false,
  dirty: true,
  qcMaskCache: new Map(), // timeId-> Uint8Array
};

function fmtTime(isoZ){
  try{
    const d = new Date(isoZ);
    return d.toISOString().slice(0,16).replace("T"," ");
  }catch{ return isoZ; }
}
function timeIdFromIso(isoZ){
  // must match python: replace ":" and "-" (keep Z)
  return isoZ.replaceAll(":","").replaceAll("-","");
}

function resolveTemplate(pathTemplate, timeId){
  // Optional depth placeholders for future backends
  const dr = state.depthRange || "0-10";
  const [z0,z1] = dr.split("-");
  return pathTemplate
    .replace("{time}", timeId)
    .replace("{depth}", dr)
    .replace("{z0}", z0)
    .replace("{z1}", z1);
}
async function fetchJson(url){
  const bust = state._cacheBust || "";
  const sep = url.includes("?") ? "&" : "?";
  const r = await fetch(bust ? `${url}${sep}v=${bust}` : url, {cache:"no-store"});
  if(!r.ok) throw new Error(`HTTP ${r.status} ${url}`);
  return r.json();
}
async function fetchBin(url, dtype){
  if(state.cache.has(url)) return state.cache.get(url);
  const bust = state._cacheBust || "";
  const sep = url.includes("?") ? "&" : "?";
  const realUrl = bust ? `${url}${sep}v=${bust}` : url;
  const r = await fetch(realUrl, {cache:"no-store"});
  if(!r.ok) throw new Error(`HTTP ${r.status} ${url}`);
  const buf = await r.arrayBuffer();
  let out;
  if(dtype === "f32") out = new Float32Array(buf);
  else if(dtype === "u8") out = new Uint8Array(buf);
  else out = buf;
  state.cache.set(url, out);
  return out;
}

/* ------------------------------
   MapLibre map (Leaflet removed) 🗺️
------------------------------ */
let map;
const OVERLAY_SOURCE = "overlay";
const OVERLAY_LAYER = "overlay-layer";
const TOP10_SOURCE = "top10";
const TOP10_LAYER = "top10-layer";
const TOP10_LABEL = "top10-label";
const AOI_SOURCE = "aoi";
const AOI_LINE = "aoi-line";

function baseStyle(){
  return {
    version: 8,
    sources: {
      osm: {
        type: "raster",
        tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
        tileSize: 256,
        attribution: "&copy; OpenStreetMap"
      }
    },
    layers: [
      { id: "osm", type: "raster", source: "osm" }
    ]
  };
}

function initMap(){
  map = new maplibregl.Map({
    container: "map",
    style: baseStyle(),
    center: [55.0, 13.0],
    zoom: 4,
    attributionControl: true,
  });
  map.addControl(new maplibregl.NavigationControl(), "top-right");

  // Ensure we only add sources/layers after style is loaded
  state._mapLoaded = new Promise((resolve)=>{
    map.on("load", async ()=>{
      // empty overlay source/layer (will be updated on first render)
      if(!map.getSource(OVERLAY_SOURCE)){
        map.addSource(OVERLAY_SOURCE, {
          type: "image",
          url: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X5q0oAAAAASUVORK5CYII=",
          coordinates: [[0,0],[0,0],[0,0],[0,0]]
        });
        map.addLayer({
          id: OVERLAY_LAYER,
          type: "raster",
          source: OVERLAY_SOURCE,
          paint: {"raster-opacity": 1.0}
        });
      }

      // Top10 source/layers
      if(!map.getSource(TOP10_SOURCE)){
        map.addSource(TOP10_SOURCE, {type:"geojson", data:{type:"FeatureCollection",features:[]}});
        map.addLayer({
          id: TOP10_LAYER,
          type: "circle",
          source: TOP10_SOURCE,
          paint: {
            "circle-radius": 6,
            "circle-color": "#39ff9f",
            "circle-stroke-width": 1,
            "circle-stroke-color": "#ffffff",
            "circle-opacity": 0.8
          }
        });
        map.addLayer({
          id: TOP10_LABEL,
          type: "symbol",
          source: TOP10_SOURCE,
          layout: {
            "text-field": ["get","rank"],
            "text-size": 12,
            "text-offset": [0, -1.2],
            "text-anchor": "top"
          },
          paint: {"text-color":"#ffffff"}
        });

        // Popup on click
        map.on("click", TOP10_LAYER, (e)=>{
          const f = e?.features?.[0];
          if(!f) return;
          const p = f.properties || {};
          const html = `
            <div style="font-weight:900">#${p.rank} • P=${p.p_pct}%</div>
            <div class="muted">SST: ${p.sst??"—"} • Chl: ${p.chl??"—"} • Cur: ${p.cur??"—"} • Hs: ${p.hs??"—"}</div>
          `;
          new maplibregl.Popup({closeButton:true, closeOnClick:true})
            .setLngLat(e.lngLat)
            .setHTML(html)
            .addTo(map);
        });
        map.on("mouseenter", TOP10_LAYER, ()=>{map.getCanvas().style.cursor="pointer";});
        map.on("mouseleave", TOP10_LAYER, ()=>{map.getCanvas().style.cursor="";});
      }

      // AOI outline (if present)
      try{
        const aoi = await fetchJson("assets/aoi.geojson");
        if(!map.getSource(AOI_SOURCE)){
          map.addSource(AOI_SOURCE, {type:"geojson", data:aoi});
          map.addLayer({
            id: AOI_LINE,
            type: "line",
            source: AOI_SOURCE,
            paint: {"line-color":"#7ef9ff","line-width": 2, "line-opacity": 0.85}
          });
        }
      }catch{ /* optional */ }

      resolve(true);
    });
  });

  map.on("click", (e)=>{
    if(!e?.lngLat) return;
    $("fbLat").value = e.lngLat.lat.toFixed(4);
    $("fbLon").value = e.lngLat.lng.toFixed(4);
  });

  // offscreen canvas for overlay
  state.canvas = document.createElement("canvas");
  state.ctx = state.canvas.getContext("2d", {willReadFrequently:false});
}

/* ------------------------------
   Colormap (RdYlGn-like)
------------------------------ */
const stops = [
  {p:0.00, c:[255, 58, 58]},
  {p:0.50, c:[255, 233, 90]},
  {p:1.00, c:[57, 255, 159]},
];
function lerp(a,b,t){return a+(b-a)*t}
function colorFor(v01){
  const v = Math.min(1, Math.max(0, v01));
  let a=stops[0], b=stops[stops.length-1];
  for(let i=0;i<stops.length-1;i++){
    if(v>=stops[i].p && v<=stops[i+1].p){ a=stops[i]; b=stops[i+1]; break; }
  }
  const t = (v - a.p) / (b.p - a.p + 1e-9);
  return [
    Math.round(lerp(a.c[0], b.c[0], t)),
    Math.round(lerp(a.c[1], b.c[1], t)),
    Math.round(lerp(a.c[2], b.c[2], t)),
  ];
}

/* ------------------------------
   Aggregation
------------------------------ */
function aggQuantile(q){
  const T = state._tmpT;
  const tmp = state._tmpVals;
  tmp.sort();
  const idx = Math.round((T-1)*q);
  return tmp[idx];
}

function aggregatePerPixel(arrs, method){
  // arrs: array of Float32Array length N, values 0..1 or NaN
  const N = arrs[0].length;
  const T = arrs.length;
  const out = new Float32Array(N);
  const tmp = new Float32Array(T);
  for(let i=0;i<N;i++){
    if(state.mask && state.mask[i]===0){ out[i]=NaN; continue; }
    let k=0;
    for(let t=0;t<T;t++){
      const v = arrs[t][i];
      if(Number.isFinite(v)) tmp[k++] = v;
    }
    if(k===0){ out[i]=NaN; continue; }
    if(method==="mean"){
      let s=0; for(let j=0;j<k;j++) s+=tmp[j];
      out[i]=s/k;
    }else if(method==="max"){
      let m=-1; for(let j=0;j<k;j++) if(tmp[j]>m) m=tmp[j];
      out[i]=m;
    }else if(method==="median"){
      // sort first k values (small)
      const slice = tmp.subarray(0,k);
      slice.sort();
      out[i]=slice[Math.floor((k-1)*0.5)];
    }else if(method==="p90"){
      const slice = tmp.subarray(0,k);
      slice.sort();
      out[i]=slice[Math.floor((k-1)*0.9)];
    }else{
      let s=0; for(let j=0;j<k;j++) s+=tmp[j];
      out[i]=s/k;
    }
  }
  return out;
}

/* ------------------------------
   Rendering to overlay
------------------------------ */
function setLegend(title){
  const el = $("legend");
  el.innerHTML = `
    <div style="font-weight:900; margin-bottom:6px">${title}</div>
    <div class="bar"></div>
    <div class="row2"><span>Low</span><span>High</span></div>
  `;
}

function renderOverlay(arr01, conf01){
  const {width:W, height:H, bounds} = state.grid;
  state.canvas.width = W;
  state.canvas.height = H;
  const img = state.ctx.createImageData(W, H);
  const data = img.data;

  const N = W*H;

  for(let i=0;i<N;i++){
    const v = arr01[i];
    const ok = Number.isFinite(v);
    const c = ok ? colorFor(v) : [0,0,0];
    const a = ok ? Math.round(255 * Math.min(1, Math.max(0, conf01[i] ?? 1))) : 0;
    const p = i*4;
    data[p+0]=c[0];
    data[p+1]=c[1];
    data[p+2]=c[2];
    data[p+3]=a;
  }
  state.ctx.putImageData(img, 0, 0);
  const url = state.canvas.toDataURL("image/png");

  // MapLibre ImageSource coordinates order:
  // [[topLeft],[topRight],[bottomRight],[bottomLeft]] in [lng,lat]
  const south = bounds[0][0], west = bounds[0][1];
  const north = bounds[1][0], east = bounds[1][1];
  const coords = [[west,north],[east,north],[east,south],[west,south]];

  const src = map.getSource(OVERLAY_SOURCE);
  if(src && src.updateImage){
    src.updateImage({url, coordinates: coords});
  }
}

/* ------------------------------
   Top‑10 extraction + UI
------------------------------ */
function topKFromArray(arr, k=10){
  const W = state.grid.width, H = state.grid.height;
  const lonMin = state.grid.lon_min, lonMax = state.grid.lon_max;
  const latMin = state.grid.lat_min, latMax = state.grid.lat_max;
  const dx = (lonMax - lonMin) / (W-1);
  const dy = (latMax - latMin) / (H-1);
  // keep best k (simple insertion)
  const best = [];
  for(let i=0;i<arr.length;i++){
    const v = arr[i];
    if(!Number.isFinite(v)) continue;
    if(best.length < k){
      best.push({i,v});
      best.sort((a,b)=>a.v-b.v);
    }else if(v > best[0].v){
      best[0] = {i,v};
      best.sort((a,b)=>a.v-b.v);
    }
  }
  best.sort((a,b)=>b.v-a.v);
  return best.map((x,rank)=>{
    const r = Math.floor(x.i / W);
    const c = x.i % W;
    const lon = lonMin + c*dx;
    const lat = latMax - r*dy;
    return {rank:rank+1, lat, lon, p: x.v};
  });
}

function renderTop10(list, covs){
  // covs optional: {sst, chl, current, waves, front}
  const rows = [];
  const feats = [];
  for(const pt of list){
    const sst = covs?.sst?.[pt.rank-1];
    const chl = covs?.chl?.[pt.rank-1];
    const cur = covs?.current?.[pt.rank-1];
    const wav = covs?.waves?.[pt.rank-1];

    feats.push({
      type: "Feature",
      properties: {
        rank: String(pt.rank),
        p: pt.p,
        p_pct: (pt.p*100).toFixed(1),
        sst: (sst!=null)? Number(sst.toFixed(2)) : null,
        chl: (chl!=null)? Number(chl.toFixed(3)) : null,
        cur: (cur!=null)? Number(cur.toFixed(2)) : null,
        hs: (wav!=null)? Number(wav.toFixed(2)) : null,
      },
      geometry: {type:"Point", coordinates:[pt.lon, pt.lat]}
    });

    rows.push({
      "#": pt.rank,
      "P%": (pt.p*100).toFixed(1),
      "Lat": pt.lat.toFixed(4),
      "Lon": pt.lon.toFixed(4),
      "SST": (sst!=null)? sst.toFixed(2) : "—",
      "Chl": (chl!=null)? chl.toFixed(3) : "—",
      "Cur": (cur!=null)? cur.toFixed(2) : "—",
      "Hs": (wav!=null)? wav.toFixed(2) : "—",
    });
  }

  // push to MapLibre source
  state.top10 = feats;
  const src = map.getSource(TOP10_SOURCE);
  if(src && src.setData){
    src.setData({type:"FeatureCollection", features: feats});
  }

  // table
  let html = `<table><thead><tr>${Object.keys(rows[0]||{"#":0}).map(k=>`<th>${k}</th>`).join("")}</tr></thead><tbody>`;
  for(const r of rows){
    html += `<tr>${Object.values(r).map(v=>`<td>${v}</td>`).join("")}</tr>`;
  }
  html += `</tbody></table>`;
  $("top10Table").innerHTML = html;
}

/* ------------------------------
   Profile + audit
------------------------------ */
function renderProfile(){
  const sp = state.meta?.species_profile;
  if(!sp){ $("profileBox").innerHTML = "—"; return; }
  const p = sp.priors;
  const w = sp.layer_weights;
  const refs = (sp.references||[]).map(x=>`<li>${x}</li>`).join("");
  $("profileBox").innerHTML = `
    <div><b>${sp.label?.en || ""}</b> • <span class="muted">${sp.scientific_name||""}</span></div>
    <div class="muted">Region: ${sp.region||"—"}</div>
    <div style="margin-top:8px"><b>Priors</b></div>
    <ul class="bullets">
      <li>SST opt/sigma: ${p.sst_opt_c}°C / ${p.sst_sigma_c}</li>
      <li>Chl opt: ${p.chl_opt_mg_m3} mg/m³ (σ log10=${p.chl_sigma_log10})</li>
      <li>Current opt/sigma: ${p.current_opt_m_s} m/s / ${p.current_sigma_m_s}</li>
      <li>Waves soft max: ${p.waves_hs_soft_max_m} m</li>
    </ul>
    <div><b>Layer weights</b></div>
    <ul class="bullets">
      <li>Temp: ${w.temp} • Chl: ${w.chl} • Front: ${w.front} • Current: ${w.current} • Waves: ${w.waves}</li>
    </ul>
    <div><b>Key references</b></div>
    <ul class="bullets">${refs}</ul>
    <div class="muted small">${sp.notes||""}</div>
  `;
}

function renderAudit(){
  const meta = state.meta;
  if(!meta){ $("auditBox").textContent="—"; return; }
  $("auditBox").textContent = JSON.stringify({
    run_id: meta.run_id,
    variant: meta.variant,
    species: meta.species,
    defaults: meta.defaults,
    ppp_model: meta.ppp_model,
    grid: meta.grid,
    times: meta.times?.length,
  }, null, 2);
}

/* ------------------------------
   Compute & update view
------------------------------ */
function getSelectedTimes(){
  const lb = $("lookbackSelect")?.value || "manual";
  const i1 = $("t1Select").selectedIndex;

  // Rolling mean: auto-override From based on To and N days lookback ✅
  if(lb !== "manual"){
    const days = parseInt(lb, 10);
    const t1 = new Date(state.times[i1]);
    const t0 = new Date(t1.getTime() - days*24*3600*1000);
    const picked = state.times.filter(t=>{
      const d = new Date(t);
      return d >= t0 && d <= t1;
    });
    // reflect in UI (From)
    if(picked.length){
      const first = picked[0];
      const i0 = state.times.indexOf(first);
      if(i0 >= 0) $("t0Select").selectedIndex = i0;
    }
    $("t0Select").disabled = true;
    return picked;
  }

  $("t0Select").disabled = false;
  const i0 = $("t0Select").selectedIndex;
  const a = Math.min(i0, i1);
  const b = Math.max(i0, i1);
  return state.times.slice(a, b+1);
}

function mapTitle(){
  const m = $("mapSelect").value;
  if(m==="pcatch") return "Pcatch (Habitat×Ops)";
  if(m==="phab") return "Habitat Suitability";
  if(m==="pops") return "Operational Feasibility";
  if(m==="agree") return "Agreement (ensemble)";
  if(m==="spread") return "Spread/Std (ensemble)";
  if(m==="conf") return "Confidence / Opacity";
  return m;
}

async function loadCovAtPoints(timeIso, points){
  // For table explainability at hotspots: sample covariates nearest grid cell
  const timeId = timeIdFromIso(timeIso);
  const W = state.grid.width, H = state.grid.height;
  const lonMin = state.grid.lon_min, lonMax = state.grid.lon_max;
  const latMin = state.grid.lat_min, latMax = state.grid.lat_max;
  const dx = (lonMax - lonMin) / (W-1);
  const dy = (latMax - latMin) / (H-1);

  async function loadArr(key, dtype){
    const url = `latest/${state.runPath}/${resolveTemplate(state.meta.paths.per_time[key], timeId)}`;
    return fetchBin(url, dtype);
  }
  const [sst, chl, cur, wav] = await Promise.all([
    loadArr("sst","f32"), loadArr("chl","f32"), loadArr("current","f32"), loadArr("waves","f32")
  ]);

  const out = {sst:[], chl:[], current:[], waves:[]};
  for(const pt of points){
    const c = Math.round((pt.lon - lonMin)/dx);
    const r = Math.round((latMax - pt.lat)/dy);
    const rr = Math.min(H-1, Math.max(0, r));
    const cc = Math.min(W-1, Math.max(0, c));
    const idx = rr*W+cc;
    out.sst.push(sst[idx]);
    out.chl.push(chl[idx]);
    out.current.push(cur[idx]);
    out.waves.push(wav[idx]);
  }
  return out;
}

async function getConfAggregated(timeIsos){
  // aggregate confidence similarly to probs (but mean)
  const W = state.grid.width, H = state.grid.height;
  const promises = timeIsos.map(t=>{
    const tid = timeIdFromIso(t);
    const url = `latest/${state.runPath}/${resolveTemplate(state.meta.paths.per_time.conf, tid)}`;
    return fetchBin(url,"f32");
  });
  const arrs = await Promise.all(promises);
  const conf = aggregatePerPixel(arrs, "mean");

  // QC mask if toggle
  if(state.qcOn){
    const qcArrs = await Promise.all(timeIsos.map(async t=>{
      const tid = timeIdFromIso(t);
      const url = `latest/${state.runPath}/${resolveTemplate(state.meta.paths.per_time.qc_chl, tid)}`;
      return fetchBin(url,"u8");
    }));
    const qcMean = new Float32Array(conf.length);
    for(let i=0;i<conf.length;i++){
      if(state.mask && state.mask[i]===0){ qcMean[i]=0; continue; }
      let s=0, k=0;
      for(let t=0;t<qcArrs.length;t++){
        s += (qcArrs[t][i] > 0) ? 1 : 0;
        k++;
      }
      qcMean[i] = (k>0)? (s/k) : 1;
    }
    for(let i=0;i<conf.length;i++) conf[i] = conf[i] * qcMean[i];
  }
  return conf;
}

async function computeAndRender(){
  localStorage.setItem("species", state.species);
  localStorage.setItem("model", state.model);
  localStorage.setItem("map", state.map);
  localStorage.setItem("agg", state.agg);

  const timeIsos = getSelectedTimes();
  const mapKey = $("mapSelect").value;
  const modelKey = $("modelSelect").value;

  const W = state.grid.width, H = state.grid.height;

  // load arrays for selected layer
  async function loadLayerForTime(timeIso){
    const tid = timeIdFromIso(timeIso);
    let key = null;
    if(mapKey==="pcatch"){
      key = `pcatch_${modelKey}`;
    }else if(mapKey==="phab"){
      key = (modelKey==="frontplus") ? "phab_frontplus" : "phab_scoring";
    }else if(mapKey==="pops"){
      key = "pops";
    }else if(mapKey==="agree"){
      key = "agree";
    }else if(mapKey==="spread"){
      key = "spread";
    }else if(mapKey==="conf"){
      key = "conf";
    }else{
      key = `pcatch_${modelKey}`;
    }
    const url = `latest/${state.runPath}/${resolveTemplate(state.meta.paths.per_time[key], tid)}`;
    return fetchBin(url, (key.endsWith("_u8")?"u8":"f32"));
  }

  const arrs = await Promise.all(timeIsos.map(loadLayerForTime));
  let aggMethod = $("aggSelect").value;
  // For conf map we always mean
  if(mapKey==="conf") aggMethod = "mean";

  const arrAgg = aggregatePerPixel(arrs, aggMethod);

  const confAgg = (mapKey==="conf")
    ? (()=>{ const c = new Float32Array(arrAgg.length); c.fill(1); return c; })()
    : await getConfAggregated(timeIsos);

  // render
  setLegend(mapTitle());
  renderOverlay(arrAgg, confAgg);

  // fit bounds on first load
  if(!state._didFit){
    map.fitBounds([[state.grid.lon_min, state.grid.lat_min],[state.grid.lon_max, state.grid.lat_max]], {padding: 20});
    state._didFit = true;
  }

  // top10 from aggregated (for catch & habitat & ops)
  const top = topKFromArray(arrAgg, 10);
  // covariates sampled at midpoint time for explainability
  const midTime = timeIsos[Math.floor(timeIsos.length/2)];
  const covs = await loadCovAtPoints(midTime, top);
  renderTop10(top, covs);
}

/* ------------------------------
   Run/variant/species meta wiring
------------------------------ */
async function refreshMeta(){
  // read meta_index to list runs
  state.index = await fetchJson("latest/meta_index.json");
  const runSelect = $("runSelect");
  runSelect.innerHTML = "";
  for(const r of state.index.runs){
    const opt = document.createElement("option");
    opt.value = r.run_id;
    opt.textContent = `${r.run_id} (${r.fast ? "fast" : "full"})`;
    runSelect.appendChild(opt);
  }
  state.runId = state.index.latest_run_id || state.index.runs[state.index.runs.length-1]?.run_id;
  runSelect.value = state.runId;

  runSelect.addEventListener("change", async ()=>{
    state.runId = runSelect.value;
    await refreshVariants();
  });

  await refreshVariants();
}

async function refreshVariants(){
  const run = state.index.runs.find(r=>r.run_id===state.runId);
  state.runPath = run.path; // e.g., runs/demo_YYYY-MM-DD
  const variantSelect = $("variantSelect");
  variantSelect.innerHTML = "";
  for(const v of run.variants){
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    variantSelect.appendChild(opt);
  }

  // Keep gap toggle in sync with variant
  const preferred = ($("gapToggle").checked) ? "gapfill" : "base";
  state.variant = run.variants.includes(preferred) ? preferred : run.variants[0];
  variantSelect.value = state.variant;

  variantSelect.addEventListener("change", async ()=>{
    state.variant = variantSelect.value;
    $("gapToggle").checked = (state.variant === "gapfill");
    await loadSpeciesMetaAndInit();
  });

  await loadSpeciesMetaAndInit();
}

async function loadSpeciesMetaAndInit(){
  state.species = $("speciesSelect").value;
  // species meta path:
  const url = `latest/${state.runPath}/variants/${state.variant}/species/${state.species}/meta.json`;
  state.meta = await fetchJson(url);
  state.grid = state.meta.grid;

  // load mask
  const maskUrl = `latest/${state.runPath}/${state.meta.paths.mask}`;
  state.mask = await fetchBin(maskUrl, "u8");

  // time selects
  state.times = state.meta.times;
  $("t0Select").innerHTML = "";
  $("t1Select").innerHTML = "";
  for(const t of state.times){
    const o0 = document.createElement("option");
    o0.value = t; o0.textContent = fmtTime(t);
    const o1 = document.createElement("option");
    o1.value = t; o1.textContent = fmtTime(t);
    $("t0Select").appendChild(o0);
    $("t1Select").appendChild(o1);
  }
  // default range: today window (middle)
  const mid = Math.floor(state.times.length/2);
  $("t0Select").selectedIndex = Math.max(0, mid-1);
  $("t1Select").selectedIndex = Math.min(state.times.length-1, mid+1);

  // defaults persisted
  $("speciesSelect").value = state.species;
  const dSel = $("depthRangeSelect"); if(dSel) dSel.value = state.depthRange;
  $("modelSelect").value = state.model;
  $("mapSelect").value = state.map;
  $("aggSelect").value = state.agg;

  renderProfile();
  renderAudit();

  // Don't auto-run analysis; wait for user action (Analyze button) ✅
  state.analyzed = false;
  state.dirty = true;
  setLegend(lang === "fa" ? "آماده تحلیل — دکمه 🔬 Analyze را بزن" : "Ready — click 🔬 Analyze");
}

/* ------------------------------
   UI events
------------------------------ */
["speciesSelect","modelSelect","mapSelect","aggSelect","t0Select","t1Select"].forEach(id=>{
  $(id).addEventListener("change", async ()=>{
    state.species = $("speciesSelect").value;
    state.model = $("modelSelect").value;
    state.map = $("mapSelect").value;
    state.agg = $("aggSelect").value;

    // if species changed, reload meta (different profile + files)
    if(id==="speciesSelect"){
      await loadSpeciesMetaAndInit();
      return;
    }
    state.dirty = true;
    setLegend(lang === "fa" ? "تغییرات اعمال شد — برای اجرا 🔬 Analyze بزن" : "Changed — press 🔬 Analyze");
  });
});

// Depth range + rolling mean controls
$("depthRangeSelect")?.addEventListener("change", ()=>{
  state.depthRange = $("depthRangeSelect").value;
  localStorage.setItem("depthRange", state.depthRange);
  state.dirty = true;
  setLegend(lang === "fa" ? "عمق تغییر کرد — برای اجرا 🔬 Analyze بزن" : "Depth changed — press 🔬 Analyze");
});
$("lookbackSelect")?.addEventListener("change", ()=>{
  state.dirty = true;
  setLegend(lang === "fa" ? "بازه میانگین تغییر کرد — برای اجرا 🔬 Analyze بزن" : "Rolling mean changed — press 🔬 Analyze");
});

$("qcToggle").addEventListener("change", async ()=>{
  state.qcOn = $("qcToggle").checked;
  state.dirty = true;
});

$("gapToggle").addEventListener("change", async ()=>{
  // Switch variant to base/gapfill if available
  const want = $("gapToggle").checked ? "gapfill" : "base";
  const run = state.index.runs.find(r=>r.run_id===state.runId);
  if(run.variants.includes(want)){
    state.variant = want;
    $("variantSelect").value = want;
    await loadSpeciesMetaAndInit();
  }else{
    // revert
    $("gapToggle").checked = (state.variant==="gapfill");
  }
});

// Analyze button: actual run/render
$("analyzeBtn")?.addEventListener("click", async ()=>{
  try{
    state._cacheBust = Date.now().toString();
    await (state._mapLoaded || Promise.resolve(true));
    await computeAndRender();
    state.analyzed = true;
    state.dirty = false;
  }catch(err){
    console.error(err);
    const msg = (lang==="fa")
      ? "دادهٔ امروز هنوز روی سرور آماده نیست 🚧\nاگر همین الان Run جدید ساخته می‌شود، کمی بعد دوباره تلاش کن."
      : "Latest data not ready on server 🚧\nIf a new run is being generated, please try again shortly.";
    alert(msg);
  }
});

/* animation */
$("playBtn").addEventListener("click", ()=>{
  if(state.playing){
    stopPlay();
  }else{
    startPlay();
  }
});
function startPlay(){
  state.playing = true;
  $("playBtn").textContent = "⏸ Pause";
  const stepH = parseInt($("stepSelect").value,10) || 6;

  // Require the user to have pressed Analyze at least once
  if(!state.analyzed){
    state.playing = false;
    $("playBtn").textContent = "▶ Play";
    alert(lang==="fa" ? "اول 🔬 Analyze را اجرا کن." : "Please run 🔬 Analyze first.");
    return;
  }

  function nextIndex(i, hours){
    const t0 = new Date(state.times[i]);
    for(let k=1;k<=state.times.length;k++){
      const j = (i+k) % state.times.length;
      const tj = new Date(state.times[j]);
      const dh = (tj - t0) / 36e5;
      if(dh >= hours - 0.1) return j;
    }
    return (i+1) % state.times.length;
  }

  const tick = async ()=>{
    const i1 = $("t1Select").selectedIndex;
    const i0 = $("t0Select").selectedIndex;
    const win = Math.max(0, i1 - i0);
    const j1 = nextIndex(i1, stepH);
    $("t1Select").selectedIndex = j1;
    // keep window length if manual; if rolling mean active, getSelectedTimes() will override From
    if($("lookbackSelect")?.value === "manual"){
      const j0 = Math.max(0, j1 - win);
      $("t0Select").selectedIndex = j0;
    }
    // if user changed settings while playing, require re-analyze
    if(state.dirty){ stopPlay(); return; }
    await computeAndRender();
  };

  state.timer = setInterval(tick, 900);
}
function stopPlay(){
  state.playing = false;
  $("playBtn").textContent = "▶ Play";
  if(state.timer) clearInterval(state.timer);
  state.timer = null;
}

/* ------------------------------
   Download / Share
------------------------------ */
$("downloadPngBtn").addEventListener("click", ()=>{
  const url = state.canvas.toDataURL("image/png");
  const a = document.createElement("a");
  a.href = url;
  a.download = `seydyaar_${state.runId}_${state.variant}_${state.species}_${state.map}_${state.agg}.png`;
  document.body.appendChild(a);
  a.click();
  a.remove();
});

$("downloadGeoBtn").addEventListener("click", async ()=>{
  const fc = {type:"FeatureCollection", features: (state.top10 || [])};
  const blob = new Blob([JSON.stringify(fc, null, 2)], {type:"application/geo+json"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `seydyaar_top10_${state.runId}_${state.variant}_${state.species}.geojson`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});

/* ------------------------------
   Feedback (IndexedDB)
------------------------------ */
const DB_NAME = "seydyaar_feedback_db";
const STORE = "feedback";
function openDb(){
  return new Promise((resolve,reject)=>{
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      const store = db.createObjectStore(STORE, {keyPath:"id"});
      store.createIndex("ts","timestamp");
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}
async function saveFeedback(rec){
  const db = await openDb();
  return new Promise((resolve,reject)=>{
    const tx = db.transaction(STORE, "readwrite");
    tx.objectStore(STORE).put(rec);
    tx.oncomplete = ()=>resolve(true);
    tx.onerror = ()=>reject(tx.error);
  });
}
async function listFeedback(){
  const db = await openDb();
  return new Promise((resolve,reject)=>{
    const tx = db.transaction(STORE, "readonly");
    const req = tx.objectStore(STORE).getAll();
    req.onsuccess = ()=>resolve(req.result || []);
    req.onerror = ()=>reject(req.error);
  });
}
function closeModal(){ $("modal").classList.add("hidden"); }
function openModal(){ $("modal").classList.remove("hidden"); }

$("feedbackBtn").addEventListener("click", openModal);
$("closeModal").addEventListener("click", closeModal);
$("modal").addEventListener("click", (e)=>{ if(e.target.id==="modal") closeModal(); });

let lastFbTs = 0;
$("saveFbBtn").addEventListener("click", async ()=>{
  const now = Date.now();
  if(now - lastFbTs < 5000){
    $("fbHint").textContent = "Rate limit: please wait a few seconds 🙏";
    return;
  }
  const rating = $("fbRating").value;
  const lat = parseFloat($("fbLat").value);
  const lon = parseFloat($("fbLon").value);
  const depth = parseInt($("fbDepth").value,10);
  const notes = ($("fbNotes").value || "").slice(0, 500);

  // validation
  if(!Number.isFinite(lat) || !Number.isFinite(lon)){
    $("fbHint").textContent = "Please set lat/lon (click on map) ✅";
    return;
  }
  if(lat < state.grid.lat_min-2 || lat > state.grid.lat_max+2 || lon < state.grid.lon_min-2 || lon > state.grid.lon_max+2){
    $("fbHint").textContent = "Lat/Lon outside AOI bounds ⚠️";
    return;
  }

  const rec = {
    id: `${now}_${Math.round(lat*10000)}_${Math.round(lon*10000)}`,
    timestamp: new Date(now).toISOString(),
    lat, lon,
    species: state.species,
    gear_depth_m: depth,
    rating,
    notes,
    run_id: state.runId,
    variant: state.variant,
    model: state.model,
  };
  await saveFeedback(rec);
  lastFbTs = now;
  $("fbHint").textContent = "Saved locally ✅ (IndexedDB)";
  setTimeout(()=>{$("fbHint").textContent = "Saved to IndexedDB. Anti‑spam: rate‑limit + basic validation.";}, 2200);
  closeModal();
});

$("exportFbBtn").addEventListener("click", async ()=>{
  const all = await listFeedback();
  const blob = new Blob([JSON.stringify(all, null, 2)], {type:"application/json"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `seydyaar_feedback_export.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});

/* ------------------------------
   Bootstrap
------------------------------ */
initMap();
refreshMeta().catch(err=>{
  console.error(err);
  alert("Failed to load demo data. Make sure you generated /docs/latest with the backend demo generator.");
});
