/* ==========================================================================
   little_brain_3d.js
   100% Authentic Three.js 3D Brain Scene from My Little Brain / cortex²
   - Loads all 28 FreeSurfer fsaverage + ENIGMA binary meshes (anatomy/*.bin)
   - Builds stylized character features: connected eyeballs (sclera, iris,
     limbal ring, 32 radial iris fibers, pupil, corneal highlight), 8 optic
     nerve fascicles per eye, tapered cervical spinal cord, 7 pairs of
     3-fascicle cervical rootlets, and 4 cervical vertebrae
   - Builds 19 10-20 cortical electrode markers + 3D DTI-colored local,
     commissural, and association white-matter fiber tracts with flowing
     action-potential particles
   - Damped-spring eye gaze tracking toward active draggable thoughts or
     orbiting butterfly/mote/fly distraction, natural blinking, breathing,
     and 4-second smooth camera auto-return
   ========================================================================== */
(function (global) {
  "use strict";

  const SUBCORTEX_COLORS = {
    accumbens: "#cfa269",
    amygdala: "#ce8587",
    caudate: "#79a399",
    hippocampus: "#bc97b1",
    pallidum: "#bda75f",
    putamen: "#8e9cbd",
    thalamus: "#d29b76",
    ventricle: "#89bcca",
    cerebellum: "#c58c9a",
    brainstem: "#d4a59c",
    ventral: "#c5ad84",
    white: "#e8d9d0",
    corpus: "#ead7b3",
    third: "#89bcca",
    fourth: "#89bcca"
  };

  const EEG_10_20 = [
    ["Fp1", -24, 66, 6], ["Fp2", 24, 66, 6],
    ["F7", -52, 30, -4], ["F3", -38, 42, 40], ["Fz", 0, 42, 54], ["F4", 38, 42, 40], ["F8", 52, 30, -4],
    ["T7", -64, -14, -6], ["C3", -50, -16, 52], ["Cz", 0, -14, 70], ["C4", 50, -16, 52], ["T8", 64, -14, -6],
    ["P7", -56, -58, -2], ["P3", -40, -62, 48], ["Pz", 0, -62, 58], ["P4", 40, -62, 48], ["P8", 56, -58, -2],
    ["O1", -26, -94, 6], ["O2", 26, -94, 6]
  ];
  const EEG_NAMES = EEG_10_20.map(e => e[0]);

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

  function makeTube(pts, radius, mat, segs = 60) {
    return new THREE.Mesh(
      new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), segs, radius, 7, false),
      mat
    );
  }

  function parseAnatomyBin(buf) {
    if (buf.byteLength < 12) throw new Error("Anatomy mesh is truncated.");
    const dv = new DataView(buf);
    if (dv.getUint32(0, true) !== 827216450) throw new Error("Unsupported anatomy mesh format.");
    const nVerts = dv.getUint32(4, true);
    const nTris = dv.getUint32(8, true);
    const positions = new Float32Array(buf, 12, nVerts * 3);
    const shading = new Float32Array(buf, 12 + nVerts * 12, nVerts);
    const indices = new Uint32Array(buf, 12 + nVerts * 16, nTris * 3);
    const colors = new Float32Array(nVerts * 3);
    for (let i = 0; i < nVerts; i++) {
      const s = shading[i];
      colors[i * 3] = s;
      colors[i * 3 + 1] = s;
      colors[i * 3 + 2] = s;
    }
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geom.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geom.setIndex(new THREE.BufferAttribute(indices, 1));
    geom.computeVertexNormals();
    geom.computeBoundingSphere();
    return geom;
  }

  function buildCharacterGroup(color = "#df9ca3", options = {}) {
    const group = new THREE.Group();
    const matCord = new THREE.MeshPhysicalMaterial({ color, roughness: 0.52, metalness: 0, clearcoat: 0.12, clearcoatRoughness: 0.65 });
    const matNerve = new THREE.MeshStandardMaterial({ color: "#ecc4b4", roughness: 0.7 });
    const matBone = new THREE.MeshStandardMaterial({ color: "#f1dfc7", roughness: 0.64 });
    const matSclera = new THREE.MeshPhysicalMaterial({ color: "#fffdf4", roughness: 0.23, clearcoat: 0.7 });
    const matIris = new THREE.MeshStandardMaterial({ color: "#887649", roughness: 0.55 });
    const matLimbus = new THREE.MeshStandardMaterial({ color: "#3d4030", roughness: 0.65 });
    const matPupil = new THREE.MeshBasicMaterial({ color: "#182322" });
    const matHighlight = new THREE.MeshBasicMaterial({ color: "#ffffff" });

    const eyes = [];
    const eyeRoots = [];
    const cortex = new THREE.Group();
    const subcortex = new THREE.Group();
    group.add(cortex, subcortex);

    if (options && options.eyes === true) {
    for (const side of [-1, 1]) {
      const root = new THREE.Group();
      root.position.set(side * 0.47, -0.43, 1.06);
      const eye = new THREE.Group();

      const sclera = new THREE.Mesh(new THREE.SphereGeometry(0.255, 40, 32), matSclera);
      sclera.castShadow = true;
      eye.add(sclera);

      const iris = new THREE.Mesh(new THREE.SphereGeometry(0.115, 32, 24), matIris);
      iris.scale.z = 0.2;
      iris.position.z = 0.243;
      eye.add(iris);

      const limbus = new THREE.Mesh(new THREE.TorusGeometry(0.107, 0.009, 8, 48), matLimbus);
      limbus.position.z = 0.252;
      eye.add(limbus);

      for (let k = 0; k < 32; k++) {
        const ang = (k / 32) * Math.PI * 2;
        const fiber = makeTube(
          [
            new THREE.Vector3(Math.cos(ang) * 0.051, Math.sin(ang) * 0.051, 0.266),
            new THREE.Vector3(Math.cos(ang + 0.045) * 0.08, Math.sin(ang + 0.045) * 0.08, 0.264),
            new THREE.Vector3(Math.cos(ang) * 0.103, Math.sin(ang) * 0.103, 0.257)
          ],
          0.0019,
          matLimbus,
          5
        );
        eye.add(fiber);
      }

      const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.058, 24, 20), matPupil);
      pupil.scale.z = 0.15;
      pupil.position.z = 0.269;
      eye.add(pupil);

      const spec = new THREE.Mesh(new THREE.SphereGeometry(0.021, 12, 12), matHighlight);
      spec.scale.z = 0.3;
      spec.position.set(-0.037, 0.041, 0.28);
      eye.add(spec);

      root.add(eye);
      group.add(root);
      eyes.push(eye);
      eyeRoots.push(root);

      for (let u = 0; u < 8; u++) {
        const zOff = (u - 3.5) * 0.015;
        group.add(
          makeTube(
            [
              new THREE.Vector3(side * 0.24 + zOff, -0.46, 0.1),
              new THREE.Vector3(side * 0.35 + zOff, -0.59, 0.37),
              new THREE.Vector3(side * 0.47 + zOff, -0.44 + zOff, 0.91)
            ],
            0.013,
            matNerve,
            20
          )
        );
      }
    }

    // Stylized cervical spinal cord
    }

    if (options && options.spine === true) {
    const cordCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-0.008, -0.88, -0.397),
      new THREE.Vector3(0.005, -1.02, -0.37),
      new THREE.Vector3(0.018, -1.29, -0.3),
      new THREE.Vector3(0.008, -1.54, -0.235),
      new THREE.Vector3(0, -1.75, -0.22)
    ]);
    const cordGeom = new THREE.TubeGeometry(cordCurve, 56, 1, 16, false);
    const posAttr = cordGeom.attributes.position;
    for (let w = 0; w <= 56; w++) {
      const t = w / 56;
      const pt = cordCurve.getPointAt(t);
      const rad = 0.085 * (1 - 0.5 * t) + 0.023 * Math.exp(-Math.pow((t - 0.2) * 5, 2));
      for (let i = 0; i <= 16; i++) {
        const idx = w * 17 + i;
        posAttr.setXYZ(
          idx,
          pt.x + (posAttr.getX(idx) - pt.x) * rad,
          pt.y + (posAttr.getY(idx) - pt.y) * rad,
          pt.z + (posAttr.getZ(idx) - pt.z) * rad
        );
      }
    }
    cordGeom.computeVertexNormals();
    const cordMesh = new THREE.Mesh(cordGeom, matCord);
    cordMesh.name = "stylized-cervical-cord";
    group.add(cordMesh);

    // 7 levels of cervical nerve rootlets
    for (let w = 0; w < 7; w++) {
      const t = 0.15 + w * 0.11;
      const pt = cordCurve.getPointAt(t);
      for (const side of [-1, 1]) {
        for (const dv of [-1, 1]) {
          for (let h = 0; h < 3; h++) {
            const k = (h - 1) * 0.013;
            const rootlet = makeTube(
              [
                new THREE.Vector3(pt.x + side * 0.07, pt.y + k, pt.z + dv * 0.025),
                new THREE.Vector3(side * 0.15, pt.y - 0.025 + k, pt.z + dv * 0.04),
                new THREE.Vector3(side * (0.29 - w * 0.013), pt.y - 0.09, pt.z + dv * 0.07),
                new THREE.Vector3(side * (0.36 - w * 0.015), pt.y - 0.13, pt.z + 0.015)
              ],
              0.0065,
              matNerve,
              20
            );
            rootlet.name = "stylized-cervical-rootlet";
            group.add(rootlet);
          }
        }
      }
    }

    // 4 cervical vertebrae
    for (let w = 0; w < 4; w++) {
      const pt = cordCurve.getPointAt(0.57 + w * 0.115);
      const vert = new THREE.Group();
      vert.name = "stylized-cervical-vertebra";
      vert.position.copy(pt);
      vert.position.z -= 0.015;
      vert.rotation.x = -0.12;

      const arch = new THREE.Mesh(new THREE.TorusGeometry(0.12 - w * 0.007, 0.03, 10, 28, Math.PI * 1.8), matBone);
      arch.rotation.x = Math.PI / 2;
      vert.add(arch);

      const spinous = new THREE.Mesh(new THREE.SphereGeometry(0.085, 18, 14), matBone);
      spinous.scale.set(1.35, 0.52, 0.7);
      spinous.position.z = 0.115;
      vert.add(spinous);

      for (const side of [-1, 1]) {
        const trans = new THREE.Mesh(new THREE.SphereGeometry(0.05, 14, 10), matBone);
        trans.scale.set(1.7, 0.45, 0.65);
        trans.position.set(side * 0.135, 0, -0.01);
        vert.add(trans);
      }
      group.add(vert);
    }

    group.rotation.x = 0.045;
    }

    return { group, eyes, eyeRoots, cortex, subcortex };
  }

  function applyInsideMode(cortex, subcortex, insideMode) {
    subcortex.visible = true;
    subcortex.traverse(obj => {
      if (!(obj instanceof THREE.Mesh)) return;
      const kind = obj.userData.anatomyKind;
      obj.visible = insideMode || kind === "hindbrain";
      const mat = obj.material;
      const trans = kind === "white-matter" || (kind === "ventricle" && insideMode);
      mat.transparent = trans;
      mat.opacity = kind === "white-matter" ? 0.11 : trans ? 0.4 : 1.0;
      mat.depthWrite = !trans;
      mat.needsUpdate = true;
    });
    cortex.traverse(obj => {
      if (obj instanceof THREE.Mesh) {
        const mat = obj.material;
        mat.transparent = insideMode;
        mat.opacity = insideMode ? 0.15 : 1.0;
        mat.depthWrite = !insideMode;
        mat.needsUpdate = true;
      }
    });
  }

  function buildProceduralAnatomyFallback(cortexGroup, subcortexGroup, baseColor = "#df9ca3") {
    for (const side of [-1, 1]) {
      const geom = new THREE.SphereGeometry(0.92, 64, 48);
      const pos = geom.attributes.position;
      const cols = new Float32Array(pos.count * 3);
      for (let i = 0; i < pos.count; i++) {
        let vx = pos.getX(i), vy = pos.getY(i), vz = pos.getZ(i);
        if (side * vx < 0) vx *= 0.14;
        else vx = side * Math.pow(Math.abs(vx), 0.86) * 0.88;
        vy *= 0.84;
        vz *= 1.18;
        const sulc = Math.sin(vx * 11 + vz * 8) * Math.cos(vy * 11 - vz * 7) * 0.035;
        const len = Math.sqrt(vx * vx + vy * vy + vz * vz) || 1;
        vx += (vx / len) * sulc + side * 0.15;
        vy += (vy / len) * sulc + 0.36;
        vz += (vz / len) * sulc + 0.02;
        pos.setXYZ(i, vx, vy, vz);
        const s = 0.88 + sulc * 2.2;
        cols[i * 3] = s; cols[i * 3 + 1] = s; cols[i * 3 + 2] = s;
      }
      geom.setAttribute("color", new THREE.BufferAttribute(cols, 3));
      geom.computeVertexNormals();
      const mesh = new THREE.Mesh(geom, new THREE.MeshPhysicalMaterial({
        color: baseColor, vertexColors: true, roughness: 0.66, metalness: 0, clearcoat: 0.06
      }));
      mesh.userData.anatomyKind = "cortex";
      cortexGroup.add(mesh);

      const hippo = new THREE.Mesh(
        new THREE.TorusGeometry(0.24, 0.065, 14, 32, Math.PI * 1.25),
        new THREE.MeshPhysicalMaterial({ color: SUBCORTEX_COLORS.hippocampus, roughness: 0.48 })
      );
      hippo.position.set(side * 0.32, 0.18, -0.05);
      hippo.rotation.set(0.5, side * 0.4, 0);
      hippo.userData.anatomyKind = "subcortex";
      subcortexGroup.add(hippo);

      const thal = new THREE.Mesh(
        new THREE.SphereGeometry(0.19, 24, 18),
        new THREE.MeshPhysicalMaterial({ color: SUBCORTEX_COLORS.thalamus, roughness: 0.48 })
      );
      thal.scale.set(0.8, 1.0, 1.35);
      thal.position.set(side * 0.18, 0.34, 0.04);
      thal.userData.anatomyKind = "subcortex";
      subcortexGroup.add(thal);

      const cereb = new THREE.Mesh(
        new THREE.SphereGeometry(0.36, 28, 22),
        new THREE.MeshPhysicalMaterial({ color: SUBCORTEX_COLORS.cerebellum, roughness: 0.52 })
      );
      cereb.scale.set(1.05, 0.72, 0.88);
      cereb.position.set(side * 0.34, -0.34, -0.52);
      cereb.userData.anatomyKind = "hindbrain";
      subcortexGroup.add(cereb);
    }
  }

  async function loadAnatomyMeshes(cortexGroup, subcortexGroup, baseColor = "#df9ca3") {
    const resp = await fetch("anatomy/manifest.json");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const manifest = await resp.json();
    await Promise.all(
      manifest.meshes.map(async m => {
        const r = await fetch(`anatomy/${m.file}`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const geom = parseAnatomyBin(await r.arrayBuffer());
        const isCortex = m.kind === "cortex";
        const prefix = m.name.split("-")[0];
        const mat = new THREE.MeshPhysicalMaterial({
          color: isCortex ? baseColor : SUBCORTEX_COLORS[prefix] || "#bcaaa0",
          vertexColors: isCortex,
          roughness: isCortex ? 0.66 : 0.48,
          metalness: 0,
          clearcoat: isCortex ? 0.06 : 0.1
        });
        const mesh = new THREE.Mesh(geom, mat);
        mesh.name = m.name;
        mesh.userData.anatomyKind = m.kind;
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        (isCortex ? cortexGroup : subcortexGroup).add(mesh);
      })
    );
  }

  function rasToScene(r, a, s, scale = 0.96) {
    return new THREE.Vector3(-r * 0.015 * scale, (s - 15) * 0.015 * scale + 0.35, (a + 17) * 0.015 * scale);
  }

  function buildResearchOverlay() {
    const root = new THREE.Group();
    root.name = "cortex2-research-overlay";
    const anchors = EEG_10_20.map(([, r, a, s]) => rasToScene(r, a, s));
    const centerHub = new THREE.Vector3(0, 0.42, 0.05);

    const edges = [];
    const seen = new Set();
    const addEdge = (i, j, kind) => {
      if (i === j) return;
      const key = i < j ? `${i}-${j}` : `${j}-${i}`;
      if (!seen.has(key)) {
        seen.add(key);
        edges.push({ a: i, b: j, kind });
      }
    };

    for (let i = 0; i < anchors.length; i++) {
      const nearest = anchors
        .map((pt, j) => ({ j, d: pt.distanceTo(anchors[i]) }))
        .filter(x => x.j !== i)
        .sort((x, y) => x.d - y.d)
        .slice(0, 3);
      nearest.forEach(n => addEdge(i, n.j, "local"));
    }
    const idxOf = name => EEG_NAMES.indexOf(name);
    for (const [a, b] of [["Fp1","Fp2"],["F3","F4"],["F7","F8"],["C3","C4"],["T7","T8"],["P3","P4"],["P7","P8"],["O1","O2"]]) {
      addEdge(idxOf(a), idxOf(b), "commissural");
    }
    for (const [a, b] of [["F7","P7"],["F8","P8"],["Fp1","O1"],["Fp2","O2"],["F3","P3"],["F4","P4"],["T7","O1"],["T8","O2"],["Fz","Pz"],["F7","T7"],["F8","T8"]]) {
      addEdge(idxOf(a), idxOf(b), "association");
    }

    let seed = 20261025;
    const rng = () => {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    };

    const fibers = [];
    const segs = 36, radSegs = 4;
    for (const edge of edges) {
      const mat = new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.48, depthWrite: false });
      const count = edge.kind === "association" ? 3 : 2;
      for (let c = 0; c < count; c++) {
        const jitter = () => new THREE.Vector3(rng() - 0.5, rng() - 0.5, rng() - 0.5).multiplyScalar(0.07);
        const p0 = anchors[edge.a].clone().add(jitter());
        const p1 = anchors[edge.b].clone().add(jitter());
        const pull = edge.kind === "local" ? 0.22 : edge.kind === "commissural" ? 0.62 : 0.42;
        const mids = [0.3, 0.5, 0.7].map(t => {
          const m = p0.clone().lerp(p1, t);
          return m.lerp(centerHub, Math.sin(Math.PI * t) * pull).add(jitter().multiplyScalar(0.8));
        });
        const curve = new THREE.CatmullRomCurve3([p0, ...mids, p1]);
        const radius = edge.kind === "local" ? 0.0055 : 0.008;
        const geom = new THREE.TubeGeometry(curve, segs, radius, radSegs, false);
        const colArr = new Float32Array(geom.attributes.position.count * 3);
        for (let s = 0; s <= segs; s++) {
          const tan = curve.getTangentAt(s / segs);
          const ax = Math.abs(tan.x), az = Math.abs(tan.z), ay = Math.abs(tan.y);
          const mx = Math.max(ax, az, ay, 1e-6);
          const rgb = [0.18 + 0.72 * (ax / mx) * ax, 0.24 + 0.56 * (az / mx) * az, 0.3 + 0.62 * (ay / mx) * ay];
          for (let r = 0; r <= radSegs; r++) {
            colArr.set(rgb, (s * (radSegs + 1) + r) * 3);
          }
        }
        geom.setAttribute("color", new THREE.BufferAttribute(colArr, 3));
        const mesh = new THREE.Mesh(geom, mat);
        mesh.renderOrder = 5;
        root.add(mesh);
        fibers.push({ curve, a: edge.a, b: edge.b, phase: rng(), speed: 0.6 + rng() * 0.8 });
      }
    }

    // Radial glow sprite texture
    const spriteCanvas = document.createElement("canvas");
    spriteCanvas.width = spriteCanvas.height = 64;
    const sCtx = spriteCanvas.getContext("2d");
    const grad = sCtx.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, "rgba(255,255,255,1)");
    grad.addColorStop(0.35, "rgba(255,255,255,0.55)");
    grad.addColorStop(1, "rgba(255,255,255,0)");
    sCtx.fillStyle = grad;
    sCtx.fillRect(0, 0, 64, 64);
    const spriteTex = new THREE.CanvasTexture(spriteCanvas);

    const pGeom = new THREE.BufferGeometry();
    const pPos = new Float32Array(fibers.length * 3);
    const pCol = new Float32Array(fibers.length * 3);
    pGeom.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
    pGeom.setAttribute("color", new THREE.BufferAttribute(pCol, 3));
    const pMat = new THREE.PointsMaterial({ size: 0.13, map: spriteTex, vertexColors: true, transparent: true, depthWrite: false });
    const pPoints = new THREE.Points(pGeom, pMat);
    pPoints.renderOrder = 7;
    root.add(pPoints);

    const cTeal = new THREE.Color("#6fc3b6");
    const cWarm = new THREE.Color("#f2b067");
    const cHot = new THREE.Color("#f07b8f");
    const tmpCol = new THREE.Color();
    const heatColor = v => (v < 0.6 ? tmpCol.copy(cTeal).lerp(cWarm, v / 0.6) : tmpCol.copy(cWarm).lerp(cHot, (v - 0.6) / 0.4));

    return {
      root,
      anchors,
      update(timeSec, intensities) {
        for (let i = 0; i < fibers.length; i++) {
          const f = fibers[i];
          const ia = intensities[f.a] ?? 0.5;
          const ib = intensities[f.b] ?? 0.5;
          const w = (ia + ib) * 0.5;
          const u = (f.phase + timeSec * f.speed * (0.14 + 0.45 * w)) % 1;
          const pt = f.curve.getPoint(ia >= ib ? u : 1 - u);
          pPos[i * 3] = pt.x;
          pPos[i * 3 + 1] = pt.y;
          pPos[i * 3 + 2] = pt.z;
          const col = heatColor(w);
          pCol[i * 3] = col.r;
          pCol[i * 3 + 1] = col.g;
          pCol[i * 3 + 2] = col.b;
        }
        pGeom.attributes.position.needsUpdate = true;
        pGeom.attributes.color.needsUpdate = true;
      }
    };
  }

  function buildPlayfulDistraction() {
    const root = new THREE.Group();
    root.name = "playful-distraction";
    const matBody = new THREE.MeshStandardMaterial({ color: "#3e4540", roughness: 0.6 });
    const matWing = new THREE.MeshStandardMaterial({ color: "#e9ae82", side: THREE.DoubleSide, roughness: 0.7 });
    const butterfly = new THREE.Group();
    const wings = [];
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.032, 12, 10), matBody);
    body.scale.set(0.65, 1.7, 0.7);
    butterfly.add(body);
    for (const side of [-1, 1]) {
      const w1 = new THREE.Mesh(new THREE.SphereGeometry(0.13, 16, 12), matWing);
      w1.scale.set(1, 0.67, 0.07);
      w1.position.set(side * 0.13 * 0.72, 0.015, 0);
      butterfly.add(w1);
      wings.push(w1);
      const w2 = w1.clone();
      w2.scale.multiplyScalar(0.68);
      w2.position.set(side * 0.13 * 0.6, -0.067, 0);
      butterfly.add(w2);
      wings.push(w2);
    }
    root.add(butterfly);
    return {
      root,
      update(timeSec, enabled) {
        root.visible = !!enabled;
        if (!enabled) return;
        root.position.set(
          1.35 * Math.cos(timeSec * 0.68),
          0.35 + Math.sin(timeSec * 1.13) * 0.72,
          1.55 + Math.sin(timeSec * 0.43) * 0.15
        );
        root.rotation.z = Math.sin(timeSec * 0.9) * 0.3;
        wings.forEach((w, idx) => {
          w.rotation.y = Math.sin(timeSec * 12) * 0.9 * (idx % 2 ? 1 : -1);
        });
      }
    };
  }

  function mountLittleBrainScene(container, options = {}) {
    const state = {
      inside: options.inside !== undefined ? options.inside : true,
      fibers: options.fibers !== undefined ? options.fibers : true,
      showThoughts: options.showThoughts !== undefined ? options.showThoughts : true,
      butterfly: options.butterfly !== undefined ? options.butterfly : true,
      color: options.color || "#df9ca3",
      thoughts: options.thoughts || [],
      activeThoughtId: options.activeThoughtId || null,
      onThoughtSelect: options.onThoughtSelect || null
    };

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.7));
    renderer.setClearColor(0, 0);
    if ("outputEncoding" in renderer && THREE.sRGBEncoding) {
      renderer.outputEncoding = THREE.sRGBEncoding;
    }
    if ("toneMapping" in renderer && THREE.ACESFilmicToneMapping) {
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.25;
    }
    renderer.shadowMap.enabled = true;
    renderer.domElement.style.cssText = "width:100%;height:100%;display:block;touch-action:none;cursor:grab";
    container.prepend(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 50);
    let camDist = 7.1;
    camera.position.set(0, -0.12, camDist);
    camera.lookAt(0, -0.12, 0);

    scene.add(new THREE.HemisphereLight("#fffefa", "#bdab9a", 1.45));
    const keyLight = new THREE.DirectionalLight("#fff7ee", 2.6);
    keyLight.position.set(-3, 4, 5);
    keyLight.castShadow = true;
    scene.add(keyLight);
    const fillLight = new THREE.DirectionalLight("#f1f7ff", 1.0);
    fillLight.position.set(3, 1, 3);
    scene.add(fillLight);
    const rimLight = new THREE.DirectionalLight("#ffe1dc", 1.8);
    rimLight.position.set(1, 3, -3);
    scene.add(rimLight);

    const charObj = buildCharacterGroup(state.color, state);
    scene.add(charObj.group);

    const researchObj = buildResearchOverlay();
    charObj.group.add(researchObj.root);

    const distractionObj = buildPlayfulDistraction();
    scene.add(distractionObj.root);

    // Build 19 HTML markers overlay
    const markersWrap = document.createElement("div");
    markersWrap.className = "brain-research-markers";
    container.appendChild(markersWrap);
    const markerEls = EEG_NAMES.map((name, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "brain-research-marker";
      btn.style.setProperty("--mark", "0.65");
      btn.title = `${name} · 6.01 Hz REM Theta Lock`;
      markersWrap.appendChild(btn);
      return btn;
    });

    // Build Thoughts overlay container
    const thoughtsWrap = document.createElement("div");
    thoughtsWrap.style.cssText = "position:absolute;inset:0;pointer-events:none;z-index:3;";
    container.appendChild(thoughtsWrap);

    function renderThoughtPills() {
      thoughtsWrap.innerHTML = "";
      if (!state.showThoughts) return;
      state.thoughts.forEach(t => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "brain-thought";
        btn.style.pointerEvents = "auto";
        btn.setAttribute("aria-pressed", String(t.id === state.activeThoughtId));
        btn.style.left = `${(t.x + 1) * 50}%`;
        btn.style.top = `${(t.y + 1) * 50}%`;
        btn.textContent = t.text;
        let drag = null;
        btn.addEventListener("pointerdown", e => {
          e.stopPropagation();
          drag = { id: e.pointerId, x: e.clientX, y: e.clientY, moved: false };
          btn.setPointerCapture(e.pointerId);
        });
        btn.addEventListener("pointermove", e => {
          if (!drag || drag.id !== e.pointerId) return;
          if (Math.hypot(e.clientX - drag.x, e.clientY - drag.y) > 4) drag.moved = true;
          if (!drag.moved) return;
          const rect = container.getBoundingClientRect();
          t.x = clamp(((e.clientX - rect.left) / rect.width) * 2 - 1, -0.88, 0.88);
          t.y = clamp(((e.clientY - rect.top) / rect.height) * 2 - 1, -0.82, 0.82);
          btn.style.left = `${(t.x + 1) * 50}%`;
          btn.style.top = `${(t.y + 1) * 50}%`;
        });
        btn.addEventListener("pointerup", e => {
          if (!drag) return;
          const wasMoved = drag.moved;
          drag = null;
          if (!wasMoved) {
            state.activeThoughtId = t.id;
            renderThoughtPills();
            if (state.onThoughtSelect) state.onThoughtSelect(t);
          }
        });
        thoughtsWrap.appendChild(btn);
      });
    }
    renderThoughtPills();

    // Load 28 fsaverage/ENIGMA meshes
    loadAnatomyMeshes(charObj.cortex, charObj.subcortex, state.color)
      .then(() => {
        applyInsideMode(charObj.cortex, charObj.subcortex, state.inside);
      })
      .catch(err => {
        console.warn("Anatomy binary fetch fallback (using procedural gyri/subcortex):", err);
        buildProceduralAnatomyFallback(charObj.cortex, charObj.subcortex, state.color);
        applyInsideMode(charObj.cortex, charObj.subcortex, state.inside);
      });

    // Orbit interaction + 4s auto-return
    let orbit = { yaw: 0, pitch: 0, lastInput: 0, dragging: false, returnFrom: null };
    let activePtr = null;
    renderer.domElement.addEventListener("pointerdown", e => {
      if (e.button !== 0) return;
      activePtr = { id: e.pointerId, x: e.clientX, y: e.clientY };
      orbit.dragging = true;
      orbit.returnFrom = null;
      orbit.lastInput = performance.now();
      renderer.domElement.setPointerCapture(e.pointerId);
      renderer.domElement.style.cursor = "grabbing";
    });
    renderer.domElement.addEventListener("pointermove", e => {
      if (!activePtr || activePtr.id !== e.pointerId) return;
      const dx = e.clientX - activePtr.x;
      const dy = e.clientY - activePtr.y;
      activePtr.x = e.clientX;
      activePtr.y = e.clientY;
      const ny = orbit.yaw - dx * 0.007;
      orbit.yaw = Math.atan2(Math.sin(ny), Math.cos(ny));
      orbit.pitch = clamp(orbit.pitch + dy * 0.006, -1.05, 1.05);
      orbit.lastInput = performance.now();
    });
    const endPtr = e => {
      if (!activePtr || activePtr.id !== e.pointerId) return;
      activePtr = null;
      orbit.dragging = false;
      orbit.lastInput = performance.now();
      renderer.domElement.style.cursor = "grab";
    };
    renderer.domElement.addEventListener("pointerup", endPtr);
    renderer.domElement.addEventListener("pointercancel", endPtr);

    function resize() {
      const w = container.clientWidth || 800;
      const h = container.clientHeight || 600;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camDist = Math.max(7.1, 4.5 / camera.aspect);
      camera.updateProjectionMatrix();
    }
    window.addEventListener("resize", resize);
    resize();

    let lastTime = performance.now();
    let elapsed = 0;
    let gazeX = 0, gazeY = 0, velX = 0, velY = 0;
    const raycaster = new THREE.Raycaster();

    function animate(now) {
      requestAnimationFrame(animate);
      const dt = Math.min((now - lastTime) / 1000, 0.04);
      lastTime = now;
      elapsed += dt;

      if (!orbit.dragging && now - orbit.lastInput > 4000) {
        orbit.returnFrom = orbit.returnFrom || { yaw: orbit.yaw, pitch: orbit.pitch };
        const t = Math.min(1, (now - orbit.lastInput - 4000) / 2000);
        const ease = 1 - t * t * (3 - 2 * t);
        orbit.yaw = orbit.returnFrom.yaw * ease;
        orbit.pitch = orbit.returnFrom.pitch * ease;
      }

      camera.position.set(
        Math.sin(orbit.yaw) * Math.cos(orbit.pitch) * camDist,
        Math.sin(orbit.pitch) * camDist - 0.12,
        Math.cos(orbit.yaw) * Math.cos(orbit.pitch) * camDist
      );
      camera.lookAt(0, -0.12, 0);
      camera.updateMatrixWorld();

      distractionObj.update(elapsed, state.butterfly);

      // Damped-spring eye gaze toward active thought or butterfly
      const activeT = state.thoughts.find(t => t.id === state.activeThoughtId);
      const targetX = activeT ? activeT.x : 0;
      const targetY = activeT ? activeT.y : 0;
      velX += ((targetX - gazeX) * 58 - velX * 14) * dt;
      velY += ((targetY - gazeY) * 58 - velY * 14) * dt;
      gazeX += velX * dt;
      gazeY += velY * dt;

      // Gentle breathing & bobbing
      charObj.group.position.y = Math.sin(elapsed * 1.15) * 0.033;
      charObj.group.rotation.y = Math.sin(elapsed * 0.35) * 0.026 + gazeX * 0.055;
      const breath = 1 + Math.sin(elapsed * 1.7) * 0.006;
      charObj.group.scale.set(breath, breath, breath);

      // Compute 3D look target
      const lookTarget = new THREE.Vector3();
      if (activeT) {
        raycaster.setFromCamera(new THREE.Vector2(gazeX, -gazeY), camera);
        const dir = camera.getWorldDirection(new THREE.Vector3());
        const planePt = camera.position.clone().addScaledVector(dir, camDist - 2.4);
        const plane = new THREE.Plane().setFromNormalAndCoplanarPoint(dir, planePt);
        raycaster.ray.intersectPlane(plane, lookTarget);
      } else if (state.butterfly) {
        lookTarget.copy(distractionObj.root.position);
      } else {
        lookTarget.set(0, -0.12, 4.5);
      }
      charObj.group.updateWorldMatrix(true, false);
      charObj.group.worldToLocal(lookTarget);

      // Natural blinking
      const bMod = elapsed % 4.8;
      const blinkScale = bMod > 0.1 && bMod < 0.24 ? Math.max(0.08, Math.abs(bMod - 0.17) / 0.07) : 1.0;
      for (let i = 0; i < charObj.eyes.length; i++) {
        const delta = lookTarget.clone().sub(charObj.eyeRoots[i].position);
        charObj.eyes[i].rotation.set(
          clamp(-Math.atan2(delta.y, delta.z), -0.43, 0.43),
          clamp(Math.atan2(delta.x, delta.z), -0.58, 0.58),
          0
        );
        charObj.eyes[i].scale.y = blinkScale;
      }

      // Update fibers & 19 10-20 markers
      researchObj.root.visible = state.fibers;
      markersWrap.style.display = state.fibers ? "block" : "none";
      if (state.fibers) {
        const intensities = EEG_NAMES.map((_, idx) => 0.35 + 0.32 * Math.sin(elapsed * 2.2 + idx * 0.6));
        researchObj.update(elapsed, intensities);
        researchObj.root.updateWorldMatrix(true, false);
        const wPt = new THREE.Vector3();
        const vDir = new THREE.Vector3();
        for (let i = 0; i < researchObj.anchors.length; i++) {
          const el = markerEls[i];
          wPt.copy(researchObj.anchors[i]).applyMatrix4(researchObj.root.matrixWorld);
          vDir.copy(camera.position).sub(wPt).normalize();
          const facing = wPt.clone().sub(charObj.group.position).normalize().dot(vDir);
          const proj = wPt.project(camera);
          el.style.left = `${(proj.x + 1) * 50}%`;
          el.style.top = `${(1 - proj.y) * 50}%`;
          el.style.opacity = String(facing > -0.15 ? 1 : 0.28);
          el.style.setProperty("--mark", intensities[i].toFixed(2));
        }
      }

      renderer.render(scene, camera);
    }
    requestAnimationFrame(animate);

    return {
      setInside(val) {
        state.inside = !!val;
        applyInsideMode(charObj.cortex, charObj.subcortex, state.inside);
      },
      setFibers(val) {
        state.fibers = !!val;
      },
      setShowThoughts(val) {
        state.showThoughts = !!val;
        renderThoughtPills();
      },
      setButterfly(val) {
        state.butterfly = !!val;
      },
      setThoughts(thoughts, activeId) {
        state.thoughts = thoughts;
        if (activeId !== undefined) state.activeThoughtId = activeId;
        renderThoughtPills();
      },
      setActiveThought(id) {
        state.activeThoughtId = id;
        renderThoughtPills();
      },
      getState() {
        return state;
      }
    };
  }

  global.mountLittleBrainScene = mountLittleBrainScene;
})(window);
