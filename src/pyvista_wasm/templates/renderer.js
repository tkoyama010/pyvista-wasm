"use strict";
(() => {
  // ts/renderer.ts
  function at(array, index) {
    var _a;
    return (_a = array[index]) != null ? _a : 0;
  }
  async function getPolyData(sourceResult) {
    if (sourceResult.isFilter) {
      sourceResult.output.update();
      return sourceResult.output.getOutputData();
    }
    return sourceResult.output;
  }
  async function connectInput(filter, sourceResult) {
    if (sourceResult.isFilter) {
      filter.setInputConnection(await sourceResult.output.getOutputPort());
    } else {
      await filter.setInputData(sourceResult.output);
    }
  }
  async function buildScene(vtk) {
    var _a, _b, _c;
    const sceneData = typeof __pvwasmSceneData === "undefined" ? JSON.parse((_b = (_a = document.querySelector("#scene-data")) == null ? void 0 : _a.textContent) != null ? _b : "{}") : __pvwasmSceneData;
    const container = typeof __pvwasmContainer === "undefined" ? (_c = document.querySelector(`#${CSS.escape(sceneData.containerId)}`)) != null ? _c : document.createElement("div") : __pvwasmContainer;
    const bg = sceneData.background;
    const renderer = vtk.vtkRenderer();
    renderer.setBackground(bg[0], bg[1], bg[2]);
    const bbox = container.getBoundingClientRect();
    const canvasId = `${sceneData.containerId}-canvas`;
    const canvas = document.createElement("canvas");
    canvas.id = canvasId;
    canvas.width = bbox.width || 600;
    canvas.height = bbox.height || 400;
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    canvas.tabIndex = -1;
    canvas.addEventListener("click", () => {
      canvas.focus();
    });
    container.append(canvas);
    const canvasSelector = `#${CSS.escape(canvasId)}`;
    const renderWindow = vtk.vtkRenderWindow({ canvasSelector });
    renderWindow.addRenderer(renderer);
    if (sceneData.lightingMode === null && sceneData.lights.length === 0) {
      renderer.removeAllLights();
      renderer.setAutomaticLightCreation(0);
    } else {
      setupLights(vtk, sceneData.lights, renderer);
    }
    for (const [index, actorConfig] of sceneData.actors.entries()) {
      await setupActor(vtk, actorConfig, index, renderer);
    }
    if (sceneData.textActors) {
      for (const textConfig of sceneData.textActors) {
        setupTextActor(textConfig, container);
      }
    }
    renderer.resetCamera();
    if (sceneData.camera) {
      await setupCamera(renderer, sceneData.camera);
    }
    const interactor = vtk.vtkRenderWindowInteractor({
      canvasSelector,
      renderWindow
    });
    await interactor.interactorStyle.setCurrentStyleToTrackballCamera();
    renderWindow.render();
    await interactor.start();
  }
  if (typeof vtkReady !== "undefined") {
    void vtkReady.then(buildScene);
  } else if (typeof vtkWASM !== "undefined") {
    void vtkWASM.createNamespace().then(buildScene);
  }
  function setupLights(vtk, lightsConfig, ren) {
    var _a;
    if (lightsConfig.length === 0) {
      return;
    }
    ren.removeAllLights();
    ren.setAutomaticLightCreation(0);
    for (const cfg of lightsConfig) {
      const light = vtk.vtkLight();
      const typeMap = {
        scene: "setLightTypeToSceneLight",
        camera: "setLightTypeToCameraLight",
        head: "setLightTypeToHeadLight"
      };
      const setter = (_a = typeMap[cfg.type]) != null ? _a : "setLightTypeToSceneLight";
      const setterFunction = light[setter];
      if (typeof setterFunction === "function") {
        setterFunction.call(light);
      }
      light.setPosition(cfg.position[0], cfg.position[1], cfg.position[2]);
      light.setFocalPoint(cfg.focalPoint[0], cfg.focalPoint[1], cfg.focalPoint[2]);
      light.setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
      light.setIntensity(cfg.intensity);
      light.setPositional(cfg.positional ? 1 : 0);
      light.setConeAngle(cfg.coneAngle);
      light.setExponent(cfg.coneFalloff);
      light.setAttenuationValues(
        cfg.attenuationValues[0],
        cfg.attenuationValues[1],
        cfg.attenuationValues[2]
      );
      ren.addLight(light);
    }
  }
  function createSource(vtk, cfg) {
    switch (cfg.type) {
      case "sphere": {
        return createSphereSource(vtk, cfg);
      }
      case "cone": {
        return createConeSource(vtk, cfg);
      }
      case "cube": {
        return createCubeSource(vtk, cfg);
      }
      case "cylinder": {
        return createCylinderSource(vtk, cfg);
      }
      case "disk": {
        return createDiskSource(vtk, cfg);
      }
      case "circle": {
        return createCircleSource(vtk, cfg);
      }
      case "arrow": {
        return createArrowSource(vtk, cfg);
      }
      case "line": {
        return createLineSource(vtk, cfg);
      }
      case "plane": {
        return createPlaneSource(vtk, cfg);
      }
      case "points": {
        console.error("points source must be awaited; use createPointsSource directly");
        return void 0;
      }
      default: {
        console.error("Unknown source type:", cfg.type);
        return void 0;
      }
    }
  }
  function createSphereSource(vtk, cfg) {
    const source = vtk.vtkSphereSource({
      center: cfg.center,
      radius: cfg.radius,
      thetaResolution: cfg.thetaResolution,
      phiResolution: cfg.phiResolution
    });
    return { output: source, isFilter: true };
  }
  function createConeSource(vtk, cfg) {
    const source = vtk.vtkConeSource({
      height: cfg.height,
      radius: cfg.radius,
      resolution: cfg.resolution
    });
    return { output: source, isFilter: true };
  }
  function createCubeSource(vtk, cfg) {
    const source = vtk.vtkCubeSource({
      xLength: cfg.xLength,
      yLength: cfg.yLength,
      zLength: cfg.zLength
    });
    return { output: source, isFilter: true };
  }
  function createCylinderSource(vtk, cfg) {
    const source = vtk.vtkCylinderSource({
      height: cfg.height,
      radius: cfg.radius,
      resolution: cfg.resolution
    });
    return { output: source, isFilter: true };
  }
  function createDiskSource(vtk, cfg) {
    const diskFactory = vtk.vtkDiskSource;
    const source = diskFactory ? diskFactory({
      innerRadius: cfg.innerRadius,
      outerRadius: cfg.outerRadius,
      radialResolution: 1,
      circumferentialResolution: cfg.resolution
    }) : void 0;
    return {
      output: source != null ? source : vtk.vtkPolyData(),
      isFilter: true
    };
  }
  function createCircleSource(vtk, cfg) {
    var _a, _b;
    return createDiskSource(vtk, {
      type: "disk",
      innerRadius: 0,
      outerRadius: (_a = cfg.radius) != null ? _a : 1,
      resolution: (_b = cfg.resolution) != null ? _b : 50
    });
  }
  function createArrowSource(vtk, cfg) {
    const source = vtk.vtkArrowSource({
      tipLength: cfg.tipLength,
      tipRadius: cfg.tipRadius,
      shaftRadius: cfg.shaftRadius
    });
    return { output: source, isFilter: true };
  }
  function createLineSource(vtk, cfg) {
    const source = vtk.vtkLineSource({
      point1: cfg.point1,
      point2: cfg.point2
    });
    return { output: source, isFilter: true };
  }
  function createPlaneSource(vtk, cfg) {
    var _a;
    const source = vtk.vtkPlaneSource({
      origin: cfg.origin
    });
    if (cfg.normal) {
      (_a = source.setNormal) == null ? void 0 : _a.call(source, cfg.normal[0], cfg.normal[1], cfg.normal[2]);
    }
    return { output: source, isFilter: true };
  }
  async function createMeshSource(vtk, cfg) {
    var _a;
    const polydata = vtk.vtkPolyData();
    const pointsFloatArr = vtk.vtkFloatArray({ numberOfComponents: 3 });
    await pointsFloatArr.setArray(Float32Array.from((_a = cfg.points) != null ? _a : []));
    const vtkPts = vtk.vtkPoints();
    await vtkPts.setData(pointsFloatArr);
    await polydata.setPoints(vtkPts);
    if (cfg.polys && cfg.polys.length > 0) {
      const legacyPolys = cfg.polys;
      const offsetsList = [0];
      const connectivityList = [];
      let i = 0;
      while (i < legacyPolys.length) {
        const count = legacyPolys[i];
        for (let j = 1; j <= count; j++) {
          connectivityList.push(legacyPolys[i + j]);
        }
        offsetsList.push(connectivityList.length);
        i += count + 1;
      }
      const offsetsArr = vtk.vtkIntArray({ numberOfComponents: 1 });
      await offsetsArr.setArray(Int32Array.from(offsetsList));
      const connectivityArr = vtk.vtkIntArray({ numberOfComponents: 1 });
      await connectivityArr.setArray(Int32Array.from(connectivityList));
      const cellArray = vtk.vtkCellArray();
      await cellArray.setData(offsetsArr, connectivityArr);
      await polydata.setPolys(cellArray);
    }
    return { output: polydata, isFilter: false };
  }
  async function createPointsSource(vtk, cfg) {
    var _a;
    const polydata = vtk.vtkPolyData();
    const pointsFloatArr = vtk.vtkFloatArray({ numberOfComponents: 3 });
    await pointsFloatArr.setArray(Float32Array.from((_a = cfg.points) != null ? _a : []));
    const vtkPts = vtk.vtkPoints();
    await vtkPts.setData(pointsFloatArr);
    await polydata.setPoints(vtkPts);
    return { output: polydata, isFilter: false };
  }
  async function injectPointData(vtk, polydata, pointDataArrays) {
    if (!pointDataArrays) {
      return;
    }
    const pd = await polydata.getPointData();
    for (const array of pointDataArrays) {
      const dataArray = vtk.vtkFloatArray({
        numberOfComponents: array.numberOfComponents,
        name: array.name
      });
      await dataArray.setArray(Float32Array.from(array.values));
      pd.addArray(dataArray);
    }
  }
  async function injectTcoords(vtk, polydata, tCoords) {
    if (!tCoords) {
      return;
    }
    const tcArray = vtk.vtkFloatArray({
      numberOfComponents: 2,
      name: "TextureCoordinates"
    });
    await tcArray.setArray(Float32Array.from(tCoords));
    const pointData = await polydata.getPointData();
    pointData.setTcoords(tcArray);
  }
  async function setupNormals(vtk, sourceResult, normalsConfig) {
    var _a, _b;
    if (!normalsConfig) {
      return sourceResult;
    }
    const normals = vtk.vtkPolyDataNormals();
    (_a = normals.setComputePointNormals) == null ? void 0 : _a.call(normals, normalsConfig.computePointNormals ? 1 : 0);
    (_b = normals.setComputeCellNormals) == null ? void 0 : _b.call(normals, normalsConfig.computeCellNormals ? 1 : 0);
    await connectInput(normals, sourceResult);
    await normals.update();
    return { output: normals, isFilter: true };
  }
  async function applyPbr(actor, pbr) {
    if (!pbr) return;
    const prop = await actor.getProperty();
    prop.setInterpolationToPhong();
    const m = pbr.metallic;
    const r = pbr.roughness;
    prop.setMetallic(m);
    prop.setRoughness(r);
    prop.setAmbient(0.1);
    prop.setSpecular(0.75 * m + 0.25);
    prop.setSpecularPower(Math.max(1, 100 * (1 - r)));
    prop.setDiffuse(0.65 + 0.35 * (1 - m));
  }
  async function setupActor(vtk, cfg, _index, ren) {
    var _a, _b;
    const sourceResult = cfg.source.type === "mesh" ? await createMeshSource(vtk, cfg.source) : cfg.source.type === "points" ? await createPointsSource(vtk, cfg.source) : createSource(vtk, cfg.source);
    if (!(sourceResult == null ? void 0 : sourceResult.output)) {
      return;
    }
    if ((_a = cfg.source.pointData) != null ? _a : cfg.source.tCoords) {
      const pd = await getPolyData(sourceResult);
      await injectPointData(vtk, pd, cfg.source.pointData);
      await injectTcoords(vtk, pd, cfg.source.tCoords);
    }
    let currentResult = sourceResult;
    if (cfg.source.filters && cfg.source.filters.length > 0) {
      currentResult = await applyFilters(vtk, sourceResult, cfg.source.filters);
    }
    const mapperInput = await setupNormals(vtk, currentResult, cfg.normals);
    const mapper = vtk.vtkPolyDataMapper();
    if (mapperInput.isFilter) {
      await mapper.setInputConnection(await mapperInput.output.getOutputPort());
    } else {
      await mapper.setInputData(mapperInput.output);
    }
    const actor = vtk.vtkActor({ mapper });
    const prop = await actor.getProperty();
    prop.setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
    prop.setOpacity(cfg.opacity);
    const styleMap = {
      surface: 2,
      wireframe: 1,
      points: 0
    };
    const rep = styleMap[cfg.style];
    if (rep !== void 0) {
      prop.setRepresentation(rep);
    }
    if (cfg.shading === "gouraud") {
      prop.setInterpolationToGouraud();
    } else if (cfg.shading === "flat") {
      prop.setInterpolationToFlat();
    }
    if (cfg.edges) {
      prop.setEdgeVisibility(1);
      prop.setEdgeColor(cfg.edges.color[0], cfg.edges.color[1], cfg.edges.color[2]);
    }
    await applyPbr(actor, cfg.pbr);
    if (cfg.actorType === "points") {
      prop.setPointSize((_b = cfg.pointSize) != null ? _b : 5);
      prop.setRepresentationToPoints();
    }
    ren.addActor(actor);
  }
  async function setupCamera(ren, camConfig) {
    const cam = await ren.getActiveCamera();
    if (camConfig.position) {
      cam.setPosition(camConfig.position[0], camConfig.position[1], camConfig.position[2]);
    }
    if (camConfig.focalPoint) {
      cam.setFocalPoint(camConfig.focalPoint[0], camConfig.focalPoint[1], camConfig.focalPoint[2]);
    }
    if (camConfig.viewUp) {
      cam.setViewUp(camConfig.viewUp[0], camConfig.viewUp[1], camConfig.viewUp[2]);
    }
    if (camConfig.viewAngle !== void 0) {
      cam.setViewAngle(camConfig.viewAngle);
    }
    if (camConfig.clippingRange) {
      cam.setClippingRange(camConfig.clippingRange[0], camConfig.clippingRange[1]);
    }
    if (camConfig.parallelProjection) {
      cam.setParallelProjection(1);
    }
    if (camConfig.viewVector && camConfig.viewUp) {
      cam.setPosition(camConfig.viewVector[0], camConfig.viewVector[1], camConfig.viewVector[2]);
      cam.setViewUp(camConfig.viewUp[0], camConfig.viewUp[1], camConfig.viewUp[2]);
      cam.setFocalPoint(0, 0, 0);
      ren.resetCamera();
      ren.resetCameraClippingRange();
    }
  }
  function setupTextActor(cfg, containerElement) {
    const div = document.createElement("div");
    div.textContent = cfg.text;
    div.style.position = "absolute";
    div.style.left = `${String(cfg.position[0] * 100)}%`;
    div.style.bottom = `${String(cfg.position[1] * 100)}%`;
    const r = Math.round(cfg.color[0] * 255);
    const g = Math.round(cfg.color[1] * 255);
    const b = Math.round(cfg.color[2] * 255);
    div.style.color = `rgba(${String(r)},${String(g)},${String(b)},${String(cfg.opacity)})`;
    div.style.fontSize = `${String(cfg.fontSize)}px`;
    div.style.fontWeight = cfg.bold ? "bold" : "normal";
    div.style.fontStyle = cfg.italic ? "italic" : "normal";
    div.style.pointerEvents = "none";
    div.style.zIndex = "10";
    div.style.whiteSpace = "pre";
    div.style.textShadow = "1px 1px 2px rgba(0,0,0,0.8), -1px -1px 2px rgba(0,0,0,0.8)";
    containerElement.append(div);
  }
  async function applyFilters(vtk, sourceResult, filters) {
    let current = sourceResult;
    for (const f of filters) {
      if (f.type === "shrink" && f.shrinkFactor !== void 0) {
        current = await applyShrinkFilter(vtk, current, f.shrinkFactor);
      } else if (f.type === "tube" && f.radius !== void 0 && f.numberOfSides !== void 0) {
        current = await applyTubeFilter(vtk, current, f.radius, f.numberOfSides);
      } else if (f.type === "clip" && f.normal && f.origin && f.invert !== void 0) {
        current = await applyClipManual(vtk, current, {
          normal: f.normal,
          origin: f.origin,
          invert: f.invert
        });
      } else if (f.type === "contour" && f.values && f.scalarName && f.scalarData) {
        current = await applyContourFilter(vtk, current, {
          values: f.values,
          scalarName: f.scalarName,
          scalarData: f.scalarData
        });
      }
    }
    return current;
  }
  async function applyShrinkFilter(vtk, sourceResult, shrinkFactor) {
    var _a;
    const inputPd = await getPolyData(sourceResult);
    const pointsObject = await inputPd.getPoints();
    const inPoints = await pointsObject.getData();
    const polysObject = await inputPd.getPolys();
    const polys = await polysObject.getData();
    if (polys.length === 0) {
      return sourceResult;
    }
    const resultPoints = [];
    const resultPolys = [];
    let offset = 0;
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      let cx = 0;
      let cy = 0;
      let cz = 0;
      const indices = [];
      for (let index_ = 0; index_ < nVerts; index_++) {
        const vi = at(polys, index + index_);
        indices.push(vi);
        cx += at(inPoints, vi * 3);
        cy += at(inPoints, vi * 3 + 1);
        cz += at(inPoints, vi * 3 + 2);
      }
      cx /= nVerts;
      cy /= nVerts;
      cz /= nVerts;
      resultPolys.push(nVerts);
      for (let k = 0; k < nVerts; k++) {
        const pi = (_a = indices[k]) != null ? _a : 0;
        const px = at(inPoints, pi * 3);
        const py = at(inPoints, pi * 3 + 1);
        const pz = at(inPoints, pi * 3 + 2);
        resultPoints.push(
          cx + (px - cx) * shrinkFactor,
          cy + (py - cy) * shrinkFactor,
          cz + (pz - cz) * shrinkFactor
        );
        resultPolys.push(offset + k);
      }
      offset += nVerts;
      index += nVerts;
    }
    const outputPd = vtk.vtkPolyData();
    const outPointsObject = await outputPd.getPoints();
    outPointsObject.setData(new Float32Array(resultPoints), 3);
    const outPolysObject = await outputPd.getPolys();
    outPolysObject.setData(new Uint32Array(resultPolys));
    return { output: outputPd, isFilter: false };
  }
  async function applyTubeFilter(vtk, sourceResult, radius, numberOfSides) {
    const tubeFilter = vtk.vtkTubeFilter({
      radius,
      numberOfSides
    });
    await connectInput(tubeFilter, sourceResult);
    return { output: tubeFilter, isFilter: true };
  }
  async function applyClipManual(vtk, sourceResult, options) {
    var _a, _b;
    const { normal, origin, invert } = options;
    const inputPd = await getPolyData(sourceResult);
    const pointsObject = await inputPd.getPoints();
    const inPoints = await pointsObject.getData();
    const polysObject = await inputPd.getPolys();
    const polys = await polysObject.getData();
    if (polys.length === 0) {
      return sourceResult;
    }
    const [nx, ny, nz] = normal;
    const [ox, oy, oz] = origin;
    const resultPoints = [];
    const resultPolys = [];
    const pointMap = /* @__PURE__ */ new Map();
    let nextIndex = 0;
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      let cx = 0;
      let cy = 0;
      let cz = 0;
      const cellIndices = [];
      for (let index_ = 0; index_ < nVerts; index_++) {
        const vi = at(polys, index + index_);
        cellIndices.push(vi);
        cx += at(inPoints, vi * 3);
        cy += at(inPoints, vi * 3 + 1);
        cz += at(inPoints, vi * 3 + 2);
      }
      cx /= nVerts;
      cy /= nVerts;
      cz /= nVerts;
      const dot = (cx - ox) * nx + (cy - oy) * ny + (cz - oz) * nz;
      const keep = invert ? dot >= 0 : dot <= 0;
      if (keep) {
        resultPolys.push(nVerts);
        for (let k = 0; k < nVerts; k++) {
          const pi = (_a = cellIndices[k]) != null ? _a : 0;
          if (!pointMap.has(pi)) {
            pointMap.set(pi, nextIndex++);
            resultPoints.push(
              at(inPoints, pi * 3),
              at(inPoints, pi * 3 + 1),
              at(inPoints, pi * 3 + 2)
            );
          }
          resultPolys.push((_b = pointMap.get(pi)) != null ? _b : 0);
        }
      }
      index += nVerts;
    }
    const outputPd = vtk.vtkPolyData();
    const outPointsObject = await outputPd.getPoints();
    outPointsObject.setData(new Float32Array(resultPoints), 3);
    const outPolysObject = await outputPd.getPolys();
    outPolysObject.setData(new Uint32Array(resultPolys));
    return { output: outputPd, isFilter: false };
  }
  async function applyContourFilter(vtk, sourceResult, options) {
    const { values, scalarName, scalarData } = options;
    const inputPd = await getPolyData(sourceResult);
    const scalars = vtk.vtkFloatArray({
      numberOfComponents: 1,
      values: Float32Array.from(scalarData),
      name: scalarName
    });
    const pd = await inputPd.getPointData();
    pd.addArray(scalars);
    pd.setActiveScalars(scalarName);
    return applyContourManual(vtk, inputPd, values, scalarName);
  }
  function collectEdgeIntersections(tri, value, inPoints) {
    const edgePoints = [];
    for (const edge of tri) {
      const [ai, bi, sa, sb] = edge;
      if (sa <= value && value < sb || sb <= value && value < sa) {
        const t = (value - sa) / (sb - sa);
        edgePoints.push(
          at(inPoints, ai * 3) + t * (at(inPoints, bi * 3) - at(inPoints, ai * 3)),
          at(inPoints, ai * 3 + 1) + t * (at(inPoints, bi * 3 + 1) - at(inPoints, ai * 3 + 1)),
          at(inPoints, ai * 3 + 2) + t * (at(inPoints, bi * 3 + 2) - at(inPoints, ai * 3 + 2))
        );
      }
    }
    return edgePoints;
  }
  async function applyContourManual(vtk, inputPd, values, scalarName) {
    var _a, _b, _c, _d, _e, _f;
    const pointsObject = await inputPd.getPoints();
    const inPoints = await pointsObject.getData();
    const polysObject = await inputPd.getPolys();
    const polys = await polysObject.getData();
    const pointDataObject = await inputPd.getPointData();
    const scalarsArray = pointDataObject.getArrayByName(scalarName);
    if (polys.length === 0 || !scalarsArray) {
      return { output: inputPd, isFilter: false };
    }
    const scalarValues = await scalarsArray.getData();
    const outPoints = [];
    const outPolys = [];
    let pointIndex = 0;
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      if (nVerts === 3) {
        const index0 = at(polys, index);
        const index1 = at(polys, index + 1);
        const index2 = at(polys, index + 2);
        const s0 = at(scalarValues, index0);
        const s1 = at(scalarValues, index1);
        const s2 = at(scalarValues, index2);
        const tri = [
          [index0, index1, s0, s1],
          [index1, index2, s1, s2],
          [index2, index0, s2, s0]
        ];
        for (const value of values) {
          const edgePoints = collectEdgeIntersections(tri, value, inPoints);
          if (edgePoints.length === 6) {
            outPoints.push(
              (_a = edgePoints[0]) != null ? _a : 0,
              (_b = edgePoints[1]) != null ? _b : 0,
              (_c = edgePoints[2]) != null ? _c : 0,
              (_d = edgePoints[3]) != null ? _d : 0,
              (_e = edgePoints[4]) != null ? _e : 0,
              (_f = edgePoints[5]) != null ? _f : 0
            );
            outPolys.push(2, pointIndex, pointIndex + 1);
            pointIndex += 2;
          }
        }
      }
      index += nVerts;
    }
    const outputPd = vtk.vtkPolyData();
    if (outPoints.length > 0) {
      const outPointsObject = await outputPd.getPoints();
      outPointsObject.setData(new Float32Array(outPoints), 3);
      const outLinesObject = await outputPd.getLines();
      outLinesObject.setData(new Uint32Array(outPolys));
    }
    return { output: outputPd, isFilter: false };
  }
})();
