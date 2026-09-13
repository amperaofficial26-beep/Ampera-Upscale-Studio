import { Muxer, ArrayBufferTarget } from "__MP4_MUXER_CDN__";

const MODE = "__MODE__";
const MAX_SECONDS = __MAX_SECONDS__;
const MAX_OUT_MP = __MAX_OUT_MP__;
const SCALE = 4;

const $ = (id) => document.getElementById(id);
const gpuEl = $("gpu"), fileEl = $("file"), goEl = $("go"),
      barEl = $("bar"), statEl = $("stat"), dlEl = $("dl"), logEl = $("log");

let session = null;
let busy = false;
let encError = null;

const even = (n) => { n = Math.round(n); return Math.max(2, n - (n % 2)); };

function log(msg) { if (msg) logEl.textContent = msg; }
function setStat(msg) { statEl.textContent = msg || ""; }
function setBar(p) { barEl.style.width = (Math.max(0, Math.min(1, p)) * 100).toFixed(1) + "%"; }
function fail(msg) { setStat(""); log(""); setStat(msg); statEl.style.color = "#E59494"; }

async function detectGPU() {
  let name = null, webgpu = false;
  try {
    if (navigator.gpu) {
      const ad = await navigator.gpu.requestAdapter();
      if (ad) {
        webgpu = true;
        let info = ad.info;
        if (!info && ad.requestAdapterInfo) {
          try { info = await ad.requestAdapterInfo(); } catch (e) {}
        }
        if (info) name = [info.vendor, info.architecture, info.description].filter(Boolean).join(" ") || null;
      }
    }
  } catch (e) {}
  if (!name) {
    try {
      const c = document.createElement("canvas");
      const gl = c.getContext("webgl2") || c.getContext("webgl");
      const ext = gl.getExtension("WEBGL_debug_renderer_info");
      if (ext) name = String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL));
    } catch (e) {}
  }
  return { name: name, webgpu: webgpu };
}

async function loadModel() {
  if (session) return session;
  if (typeof ort === "undefined") throw new Error("Pustaka ONNX gagal dimuat (butuh koneksi internet).");
  log("Memuat model Real-CUGAN…");
  const bin = Uint8Array.from(atob(window.__MODEL_B64__), (c) => c.charCodeAt(0));
  ort.env.wasm.wasmPaths = "__ORT_CDN__";
  ort.env.wasm.numThreads = 1;
  try {
    session = await ort.InferenceSession.create(bin, { executionProviders: ["webgpu"] });
    log("Model siap (WebGPU).");
  } catch (e) {
    log("WebGPU tidak tersedia — memakai CPU (lebih lambat)…");
    session = await ort.InferenceSession.create(bin, { executionProviders: ["wasm"] });
    log("Model siap (CPU/WASM).");
  }
  return session;
}

function canvasToTensor(canvas) {
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const w = canvas.width, h = canvas.height;
  const d = ctx.getImageData(0, 0, w, h).data;
  const n = w * h;
  const f = new Float32Array(3 * n);
  for (let p = 0; p < n; p++) {
    f[p] = d[4 * p] / 255;
    f[n + p] = d[4 * p + 1] / 255;
    f[2 * n + p] = d[4 * p + 2] / 255;
  }
  return new ort.Tensor("float32", f, [1, 3, h, w]);
}

function tensorToCanvas(t, canvas) {
  const dims = t.dims;
  const H = dims[2], W = dims[3], d = t.data, n = W * H;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext("2d");
  const img = ctx.createImageData(W, H);
  const px = img.data;
  for (let p = 0; p < n; p++) {
    let r = d[p] * 255, g = d[n + p] * 255, b = d[2 * n + p] * 255;
    px[4 * p] = r < 0 ? 0 : (r > 255 ? 255 : r);
    px[4 * p + 1] = g < 0 ? 0 : (g > 255 ? 255 : g);
    px[4 * p + 2] = b < 0 ? 0 : (b > 255 ? 255 : b);
    px[4 * p + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
}

async function upscale(cin, cout) {
  const feeds = {};
  feeds[session.inputNames[0]] = canvasToTensor(cin);
  const out = await session.run(feeds);
  tensorToCanvas(out[session.outputNames[0]], cout);
}

function seek(v, t) {
  return new Promise((res) => {
    const done = () => { v.removeEventListener("seeked", done); res(); };
    v.addEventListener("seeked", done);
    v.currentTime = Math.min(t, Math.max(0, (v.duration || 0) - 0.001));
    setTimeout(() => { v.removeEventListener("seeked", done); res(); }, 3000);
  });
}

function probeFPS(v) {
  return new Promise((res) => {
    if (!v.requestVideoFrameCallback) return res(30);
    let n = 0, t0 = 0, stopped = false;
    const cb = (now) => {
      if (!t0) t0 = now;
      n++;
      if (!stopped) v.requestVideoFrameCallback(cb);
    };
    v.requestVideoFrameCallback(cb);
    v.play().catch(() => {});
    setTimeout(() => {
      stopped = true;
      v.pause();
      const dt = (performance.now() - t0) / 1000;
      if (n < 3 || dt <= 0) return res(30);
      const f = n / dt;
      const cands = [24, 25, 30, 48, 50, 60];
      let best = cands[0];
      for (const c of cands) if (Math.abs(c - f) < Math.abs(best - f)) best = c;
      if (Math.abs(best - f) / f < 0.25) res(best);
      else res(Math.min(60, Math.max(15, Math.round(f))));
    }, 700);
  });
}

async function pickVideoConfig(w, h, fps) {
  const bitrate = Math.min(24e6, Math.max(2e6, Math.round(w * h * fps * 0.08)));
  const codecs = ["avc1.640034", "avc1.640033", "avc1.4d0034", "avc1.640028", "avc1.42002a"];
  for (const c of codecs) {
    const cfg = { codec: c, width: w, height: h, framerate: fps, bitrate: bitrate };
    try {
      const s = await VideoEncoder.isConfigSupported(cfg);
      if (s.supported) return cfg;
    } catch (e) {}
  }
  throw new Error("Encoder H.264 tidak tersedia — gunakan Chrome atau Edge terbaru.");
}

async function loadAudio(file) {
  try {
    const actx = new (window.AudioContext || window.webkitAudioContext)();
    const buf = await actx.decodeAudioData(await file.arrayBuffer());
    actx.close();
    if (buf.numberOfChannels < 1 || buf.length < 1) return null;
    return buf;
  } catch (e) { return null; }
}

async function encodeAudio(abuf, muxer) {
  if (!("AudioEncoder" in window)) return false;
  const CH = Math.min(abuf.numberOfChannels, 2);
  const SR = abuf.sampleRate;
  const cfg = { codec: "mp4a.40.2", sampleRate: SR, numberOfChannels: CH, bitrate: 128000 };
  try {
    const s = await AudioEncoder.isConfigSupported(cfg);
    if (!s.supported) return false;
  } catch (e) { return false; }
  const enc = new AudioEncoder({ output: (c, m) => muxer.addAudioChunk(c, m), error: () => {} });
  enc.configure(cfg);
  const chans = [];
  for (let c = 0; c < CH; c++) chans.push(abuf.getChannelData(c));
  const step = Math.max(1, Math.floor(SR / 10));
  for (let off = 0; off < abuf.length; off += step) {
    const n = Math.min(step, abuf.length - off);
    let data;
    if (CH === 1) data = chans[0].subarray(off, off + n);
    else {
      data = new Float32Array(n * CH);
      for (let c = 0; c < CH; c++) data.set(chans[c].subarray(off, off + n), c * n);
    }
    const ad = new AudioData({
      format: "f32-planar", sampleRate: SR, numberOfFrames: n,
      numberOfChannels: CH, timestamp: Math.round(off / SR * 1e6), data: data
    });
    enc.encode(ad);
    ad.close();
  }
  await enc.flush();
  enc.close();
  return true;
}

async function processVideo(file) {
  if (!("VideoEncoder" in window))
    throw new Error("Browser ini tidak mendukung WebCodecs — gunakan Chrome/Edge terbaru.");
  await loadModel();

  const url = URL.createObjectURL(file);
  const v = document.createElement("video");
  v.src = url; v.muted = true; v.playsInline = true; v.preload = "auto";
  await new Promise((res, rej) => {
    v.onloadedmetadata = res;
    v.onerror = () => rej(new Error("Video tidak bisa dibuka."));
  });
  if ((v.duration || 0) > MAX_SECONDS + 0.25)
    throw new Error("Durasi video melebihi " + MAX_SECONDS + " detik.");

  setStat("Menganalisis video…");
  const fps = await probeFPS(v);
  const dur = Math.min(v.duration || MAX_SECONDS, MAX_SECONDS);
  const frames = Math.max(1, Math.min(Math.round(dur * fps), 900));

  let sw = v.videoWidth, sh = v.videoHeight;
  const maxIn = MAX_OUT_MP * 1e6 / 16;
  if (sw * sh > maxIn) {
    const f = Math.sqrt(maxIn / (sw * sh));
    sw = even(sw * f); sh = even(sh * f);
  }
  const outW = sw * SCALE, outH = sh * SCALE;

  const abuf = await loadAudio(file);
  const hasAudio = !!abuf;

  const muxer = new Muxer({
    target: new ArrayBufferTarget(),
    fastStart: "in-memory",
    video: { codec: "avc", width: outW, height: outH },
    audio: hasAudio ? { codec: "aac", sampleRate: abuf.sampleRate, numberOfChannels: Math.min(abuf.numberOfChannels, 2) } : undefined
  });

  const cfg = await pickVideoConfig(outW, outH, fps);
  encError = null;
  const enc = new VideoEncoder({ output: (c, m) => muxer.addVideoChunk(c, m), error: (e) => { encError = e; } });
  enc.configure(cfg);

  const cin = document.createElement("canvas");
  cin.width = sw; cin.height = sh;
  const cout = document.createElement("canvas");
  const cctx = cin.getContext("2d", { willReadFrequently: true });

  const t0 = Date.now();
  for (let i = 0; i < frames; i++) {
    if (encError) throw new Error("Encoder berhenti: " + encError.message);
    await seek(v, i / fps);
    cctx.drawImage(v, 0, 0, sw, sh);
    await upscale(cin, cout);
    const frame = new VideoFrame(cout, {
      timestamp: Math.round(i * 1e6 / fps),
      duration: Math.round(1e6 / fps)
    });
    enc.encode(frame, { keyFrame: i % Math.round(fps * 2) === 0 });
    frame.close();
    while (enc.encodeQueueSize > 4) await new Promise((r) => setTimeout(r, 5));
    setBar((i + 1) / frames);
    const el = (Date.now() - t0) / 1000;
    const speed = (i + 1) / el;
    setStat("Frame " + (i + 1) + "/" + frames + " · " + speed.toFixed(1) + " fps · sisa ± " +
            Math.round((frames - i - 1) / Math.max(speed, 0.01)) + " dtk");
  }
  await enc.flush();
  enc.close();

  let audioOK = false;
  if (hasAudio) {
    setStat("Menyusun ulang audio…");
    try { audioOK = await encodeAudio(abuf, muxer); } catch (e) { audioOK = false; }
  }

  muxer.finalize();
  URL.revokeObjectURL(url);
  const blob = new Blob([muxer.target.buffer], { type: "video/mp4" });
  const total = ((Date.now() - t0) / 1000).toFixed(0);
  offerDownload(blob, "ampera_gpu_" + Date.now() + ".mp4");
  setStat("Selesai ✓ " + total + " dtk · " + outW + "×" + outH +
          (hasAudio ? (audioOK ? " · audio dipertahankan" : " · audio gagal disusun") : ""));
}

async function processImage(file) {
  await loadModel();
  const bmp = await createImageBitmap(file);
  let sw = bmp.width, sh = bmp.height;
  const maxIn = MAX_OUT_MP * 1e6 / 16;
  if (sw * sh > maxIn) {
    const f = Math.sqrt(maxIn / (sw * sh));
    sw = even(sw * f); sh = even(sh * f);
  }
  const cin = document.createElement("canvas");
  cin.width = sw; cin.height = sh;
  const cctx = cin.getContext("2d", { willReadFrequently: true });
  cctx.drawImage(bmp, 0, 0, sw, sh);
  const cout = document.createElement("canvas");
  setStat("Memproses di GPU…");
  setBar(0.5);
  await upscale(cin, cout);
  setBar(1);
  bmp.close();
  const blob = await new Promise((res) => cout.toBlob(res, "image/png"));
  offerDownload(blob, "ampera_gpu_" + Date.now() + ".png");
  setStat("Selesai ✓ " + cout.width + "×" + cout.height);
}

function offerDownload(blob, name) {
  const url = URL.createObjectURL(blob);
  dlEl.href = url;
  dlEl.download = name;
  dlEl.style.display = "inline-flex";
}

goEl.addEventListener("click", async () => {
  if (busy) return;
  const file = fileEl.files && fileEl.files[0];
  if (!file) { fail("Pilih berkas dulu."); return; }
  busy = true;
  goEl.disabled = true;
  statEl.style.color = "";
  setBar(0);
  try {
    if (MODE === "video") await processVideo(file);
    else await processImage(file);
  } catch (e) {
    fail("Gagal: " + (e && e.message ? e.message : e));
  } finally {
    busy = false;
    goEl.disabled = false;
  }
});

(async function init() {
  const g = await detectGPU();
  if (g.webgpu) {
    gpuEl.textContent = "GPU: " + (g.name || "terdeteksi · WebGPU aktif");
  } else if (g.name) {
    gpuEl.textContent = "GPU: " + g.name + " (WebGPU nonaktif — akan lambat)";
  } else {
    gpuEl.textContent = "GPU tidak terdeteksi — akan memakai CPU (lambat)";
  }
})();
