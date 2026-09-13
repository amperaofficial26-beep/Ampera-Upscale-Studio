(function () {
  var el = document.getElementById("gpu");
  function set(text, cls) {
    if (!el) return;
    el.textContent = text;
    if (cls) el.classList.add(cls);
  }
  async function detect() {
    var name = null, webgpu = false;
    try {
      if (navigator.gpu) {
        var ad = await navigator.gpu.requestAdapter();
        if (ad) {
          webgpu = true;
          var info = ad.info;
          if (!info && ad.requestAdapterInfo) {
            try { info = await ad.requestAdapterInfo(); } catch (e) {}
          }
          if (info) {
            name = [info.vendor, info.architecture, info.description]
              .filter(Boolean).join(" ") || null;
          }
        }
      }
    } catch (e) {}
    if (!name) {
      try {
        var c = document.createElement("canvas");
        var gl = c.getContext("webgl2") || c.getContext("webgl");
        var ext = gl.getExtension("WEBGL_debug_renderer_info");
        if (ext) name = String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL));
      } catch (e) {}
    }
    if (webgpu) {
      set("GPU siap: " + (name || "WebGPU aktif"), "ok");
    } else if (name) {
      set(name + " — WebGPU nonaktif, proses jadi lambat", "warn");
    } else {
      set("GPU tidak terdeteksi — proses akan lambat", "warn");
    }
  }
  detect();
})();
