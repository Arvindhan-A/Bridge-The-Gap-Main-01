/* ================================================================
   BDG CHAPTERS WORLD MAP  —  chapters-map.js
   ----------------------------------------------------------------
   Data source : GET  window.BDG_MAP.geoUrl       (chapters with lat/lng)
   Place pin   : POST window.BDG_MAP.coordsUrl + <chapterId>
   Edit gating : window.BDG_MAP.canEdit  (server-rendered, super admin only)
   CSRF        : window.BDG_MAP.csrfToken  (sent as X-CSRFToken header)

   No localStorage. No ?admin=true. All persistence goes through Flask.
================================================================ */
(function () {
  "use strict";

  const CFG = window.BDG_MAP;
  if (!CFG) { console.error("BDG_MAP config missing"); return; }

  const W = 960, H = 480;
  const svg = d3.select("#world-svg");

  let chapters = [];        // [{id,name,president,url,lat,lng}]
  let placing  = false;
  let removing = false;

  /* ── SVG scaffolding ── */
  const defs = svg.append("defs");
  const dotPat = defs.append("pattern")
    .attr("id", "bdg-dots").attr("x", 0).attr("y", 0)
    .attr("width", 18).attr("height", 18)
    .attr("patternUnits", "userSpaceOnUse");
  dotPat.append("circle").attr("cx", 1).attr("cy", 1).attr("r", 0.85)
    .attr("fill", "rgba(157,151,174,.18)");

  const projection = d3.geoNaturalEarth1().scale(153).translate([W / 2, H / 2]);
  const geoPath   = d3.geoPath(projection);
  const graticule = d3.geoGraticule();

  const gSphere  = svg.append("g");
  const gDots    = svg.append("g");
  const gGrat    = svg.append("g");
  const gLand    = svg.append("g");
  const gBorders = svg.append("g");
  const gPins    = svg.append("g");

  gSphere.append("path").datum({ type: "Sphere" }).attr("d", geoPath).attr("fill", "#1D1634");
  gDots.append("path").datum({ type: "Sphere" }).attr("d", geoPath).attr("fill", "url(#bdg-dots)");
  gGrat.append("path").datum(graticule()).attr("d", geoPath).attr("class", "graticule");

  /* ── DOM refs ── */
  const tipEl   = document.getElementById("bdg-tip");
  const popupEl = document.getElementById("bdg-popup");
  const puName  = document.getElementById("pu-name");
  const puPres  = document.getElementById("pu-pres");
  const puLink  = document.getElementById("pu-link");

  let activeChId = null, activePinEl = null;

  /* ── Tooltip ── */
  function showTip(text, sx, sy) {
    const map = document.getElementById("bdg-map");
    const scale = map.clientWidth / W;
    tipEl.textContent = text;
    tipEl.style.left = (sx * scale) + "px";
    tipEl.style.top  = (sy * scale) + "px";
    tipEl.classList.add("show");
  }
  function hideTip() { tipEl.classList.remove("show"); }

  /* ── Popup ── */
  function showPopup(ch, sx, sy) {
    puName.textContent = ch.name;
    puPres.textContent = ch.president || "TBD";
    const hasUrl = ch.url && ch.url !== "#";
    puLink.href = hasUrl ? ch.url : "#";
    puLink.textContent = hasUrl ? "Visit Chapter →" : "Page coming soon";
    puLink.className = "pu-btn" + (hasUrl ? "" : " no-url");

    const map = document.getElementById("bdg-map");
    const scale = map.clientWidth / W;
    const px = sx * scale, py = sy * scale, PW = 224, PH = 160;
    let left = px - PW / 2, top = py - PH - 24;
    const flipped = top < 8;
    if (flipped) top = py + 20;
    left = Math.max(8, Math.min(left, map.clientWidth - PW - 8));
    popupEl.style.left = left + "px";
    popupEl.style.top  = top + "px";
    popupEl.classList.toggle("flipped", flipped);
    popupEl.classList.add("open");
    activeChId = ch.id;
  }
  function hidePopup() {
    popupEl.classList.remove("open");
    if (activePinEl) { activePinEl.classed("active", false); activePinEl = null; }
    activeChId = null;
  }
  document.getElementById("pu-close").addEventListener("click", hidePopup);

  svg.on("click.bg", function (e) {
    if (placing) return;
    if (e.target === svg.node() || e.target.classList.contains("graticule")) hidePopup();
  });

  window.addEventListener("resize", () => {
    if (!activeChId || !popupEl.classList.contains("open")) return;
    const ch = chapters.find(c => c.id === activeChId);
    if (!ch) return;
    const c = projection([ch.lng, ch.lat]);
    if (c) showPopup(ch, c[0], c[1]);
  });

  /* ── Pins ── */
  function drawPins() {
    gPins.selectAll(".chapter-pin").remove();
    chapters.forEach(ch => {
      const pt = projection([ch.lng, ch.lat]);
      if (!pt) return;
      const [cx, cy] = pt;
      const g = gPins.append("g").attr("class", "chapter-pin")
        .attr("transform", `translate(${cx},${cy})`);
      g.append("circle").attr("class", "pin-ripple").attr("r", 8);
      g.append("circle").attr("class", "pin-ripple r2").attr("r", 8);
      g.append("circle").attr("class", "pin-ring").attr("r", 9);
      g.append("circle").attr("class", "pin-core").attr("r", 4.5);
      g.append("text").attr("class", "pin-label").attr("y", 14).text(ch.name);

      g.on("mouseenter", () => { if (!removing) showTip(ch.name, cx, cy - 12); });
      g.on("mouseleave", hideTip);
      g.on("click", e => {
        e.stopPropagation();
        hideTip();
        if (removing) { clearPin(ch); return; }
        if (placing)  return;
        hidePopup();
        if (activePinEl) activePinEl.classed("active", false);
        activePinEl = d3.select(g.node());
        activePinEl.classed("active", true);
        showPopup(ch, cx, cy);
      });
    });
  }

  /* ── Data load ── */
  function fetchChapters() {
    return fetch(CFG.geoUrl, { headers: { "Accept": "application/json" } })
      .then(r => r.json())
      .then(data => {
        chapters = (data.chapters || data || []).map(c => ({
          id: c.id, name: c.name, president: c.president,
          url: c.url, lat: c.lat, lng: c.lng
        }));
        drawPins();
      })
      .catch(err => console.error("Failed to load chapters", err));
  }

  /* ================================================================
     ADMIN  (only wired up when CFG.canEdit === true)
  ================================================================ */
  if (CFG.canEdit) {
    const btnAdd  = document.getElementById("btn-add");
    const btnRem  = document.getElementById("btn-rem");
    const admStat = document.getElementById("adm-status");
    const sel     = document.getElementById("adm-chapter");
    const svgDom  = document.getElementById("world-svg");

    const headers = () => ({
      "Content-Type": "application/json",
      "X-CSRFToken": CFG.csrfToken
    });

    function selectedChapterId() {
      return sel && sel.value ? parseInt(sel.value, 10) : null;
    }

    btnAdd.addEventListener("click", () => {
      if (removing) stopRemove();
      placing = !placing;
      if (placing) {
        if (!selectedChapterId()) { admStat.textContent = "⚠ Select a chapter first."; placing = false; return; }
        btnAdd.textContent = "✕ Cancel";
        btnAdd.classList.add("on");
        admStat.textContent = "Click the map to place this chapter.";
        svgDom.classList.add("placing");
      } else { stopPlace(); }
    });

    function stopPlace(msg) {
      placing = false;
      btnAdd.textContent = "＋ Place on map";
      btnAdd.classList.remove("on");
      svgDom.classList.remove("placing");
      admStat.textContent = msg || "Pick a chapter, click Place, then tap the map.";
    }

    btnRem.addEventListener("click", () => {
      if (placing) stopPlace();
      removing = !removing;
      if (removing) {
        btnRem.textContent = "✕ Cancel";
        btnRem.classList.add("on");
        admStat.textContent = "Click a pin to clear its location.";
        gPins.classed("pins-remove", true);
      } else { stopRemove(); }
    });

    function stopRemove(msg) {
      removing = false;
      btnRem.textContent = "✕ Clear pin";
      btnRem.classList.remove("on");
      gPins.classed("pins-remove", false);
      if (msg) admStat.textContent = msg;
    }

    /* Click-to-place → POST coordinates */
    svg.on("click.place", e => {
      if (!placing) return;
      const id = selectedChapterId();
      if (!id) { admStat.textContent = "⚠ Select a chapter first."; return; }
      const [mx, my] = d3.pointer(e);
      const geo = projection.invert([mx, my]);
      if (!geo) return;
      const lat = +geo[1].toFixed(4), lng = +geo[0].toFixed(4);

      fetch(CFG.coordsUrl + id, {
        method: "POST", headers: headers(),
        body: JSON.stringify({ latitude: lat, longitude: lng })
      })
        .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(() => fetchChapters())
        .then(() => {
          const name = sel.options[sel.selectedIndex].dataset.name || "Chapter";
          stopPlace(`✓ "${name}" placed.`);
        })
        .catch(err => { stopPlace("✕ Save failed — check you’re still logged in."); console.error(err); });
    });

    /* Click pin while removing → POST null coordinates (clear) */
    window.__bdgClearPin = function (ch) {
      fetch(CFG.coordsUrl + ch.id, {
        method: "POST", headers: headers(),
        body: JSON.stringify({ latitude: null, longitude: null })
      })
        .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(() => fetchChapters())
        .then(() => { hidePopup(); stopRemove(`✓ "${ch.name}" cleared.`); })
        .catch(err => { stopRemove("✕ Clear failed."); console.error(err); });
    };

    /* Coordinate readout */
    const coordEl = document.getElementById("bdg-coords");
    if (coordEl) {
      svg.on("mousemove.coords", e => {
        const [mx, my] = d3.pointer(e);
        const geo = projection.invert([mx, my]);
        if (geo) {
          const la = Math.abs(geo[1]).toFixed(2), lo = Math.abs(geo[0]).toFixed(2);
          coordEl.textContent = `${la}°${geo[1] >= 0 ? "N" : "S"}  ${lo}°${geo[0] >= 0 ? "E" : "W"}`;
        }
      });
    }
  }

  /* Called from pin click in remove mode; routes to admin handler if present. */
  function clearPin(ch) {
    if (CFG.canEdit && window.__bdgClearPin) window.__bdgClearPin(ch);
  }

  /* ================================================================
     WORLD DATA + BOOT
  ================================================================ */
  d3.json(CFG.worldUrl).then(world => {
    const countries = topojson.feature(world, world.objects.countries);
    const borders   = topojson.mesh(world, world.objects.countries, (a, b) => a !== b);

    gLand.selectAll("path").data(countries.features).join("path")
      .attr("class", "country").attr("d", geoPath);

    gBorders.append("path").datum(borders)
      .attr("fill", "none").attr("stroke", "rgba(100,93,119,.2)")
      .attr("stroke-width", 0.25).attr("d", geoPath);
    gBorders.append("path").datum({ type: "Sphere" })
      .attr("fill", "none").attr("stroke", "rgba(100,93,119,.45)")
      .attr("stroke-width", 0.7).attr("d", geoPath);

    fetchChapters();
  }).catch(() => {
    gSphere.append("text").attr("x", W / 2).attr("y", H / 2)
      .attr("text-anchor", "middle").attr("fill", "rgba(157,151,174,.5)")
      .attr("font-size", 13).text("Map data could not load.");
    fetchChapters();
  });
})();
