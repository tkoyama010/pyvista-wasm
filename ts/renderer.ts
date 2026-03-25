/**
 * Pyvista-wasm renderer — reads scene configuration from JSON and creates
 * VTK.wasm objects.
 *
 * In JupyterLite, `_generate_render_js()` sets `__pvwasmSceneData` and
 * `__pvwasmContainer` before evaluating this code. In standalone HTML,
 * the scene data is read from the DOM.
 *
 * VTK.wasm uses an async initialisation model: the wasm namespace must be
 * created via `vtkWASM.createNamespace()` or the `vtkReady` promise before
 * any VTK objects can be constructed.
 */

/**
 * Access a typed array element, returning 0 for out-of-bounds.
 * @param array
 * @param index
 * @returns The element at `index`, or 0 if out of bounds.
 */
function at(array: Float32Array | Uint32Array, index: number): number {
  return array[index] ?? 0;
}

/** Wraps either a VTK algorithm (filter/source) or raw PolyData. */
type SourceResult = {
  output: VtkAlgorithm | VtkPolyData;
  isFilter: boolean;
};

/**
 * Resolve a {@link SourceResult} to its underlying PolyData.
 * @param sourceResult
 * @returns The underlying {@link VtkPolyData} from the source or filter output.
 */
function getPolyData(sourceResult: SourceResult): VtkPolyData {
  if (sourceResult.isFilter) {
    (sourceResult.output as VtkAlgorithm).update();
    return (sourceResult.output as VtkAlgorithm).getOutputData();
  }

  return sourceResult.output as VtkPolyData;
}

/**
 * Wire `filter`'s input to the output of `sourceResult`.
 * @param filter
 * @param sourceResult
 */
function connectInput(filter: VtkAlgorithm, sourceResult: SourceResult): void {
  if (sourceResult.isFilter) {
    filter.setInputConnection((sourceResult.output as VtkAlgorithm).getOutputPort());
  } else {
    filter.setInputData(sourceResult.output as VtkPolyData);
  }
}

/**
 * Main entry point — initialise VTK.wasm and build the scene.
 * @param vtk
 */
async function buildScene(vtk: VtkWasmNamespace): Promise<void> {
  const sceneData: SceneData =
    typeof __pvwasmSceneData === "undefined"
      ? (JSON.parse(document.querySelector("#scene-data")?.textContent ?? "{}") as SceneData)
      : __pvwasmSceneData;
  const container: HTMLElement =
    typeof __pvwasmContainer === "undefined"
      ? (document.querySelector<HTMLElement>(`#${CSS.escape(sceneData.containerId)}`) ??
        document.createElement("div"))
      : __pvwasmContainer;
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
  container.append(canvas);

  const renderWindow = vtk.vtkRenderWindow({ canvasSelector: `#${CSS.escape(canvasId)}` });
  renderWindow.render();

  const interactor = vtk.vtkRenderWindowInteractor({ renderWindow });
  const interactorStyle = vtk.vtkInteractorStyleTrackballCamera();
  interactor.setInteractorStyle(interactorStyle);

  if (sceneData.lightingMode === null && sceneData.lights.length === 0) {
    renderer.removeAllLights();
    renderer.setAutomaticLightCreation(false);
  } else {
    setupLights(vtk, sceneData.lights, renderer);
  }

  for (const [index, actorConfig] of sceneData.actors.entries()) {
    setupActor(vtk, actorConfig, index, renderer);
  }

  if (sceneData.textActors) {
    for (const textConfig of sceneData.textActors) {
      setupTextActor(textConfig, container);
    }
  }

  renderer.resetCamera();
  if (sceneData.camera) {
    setupCamera(renderer, sceneData.camera);
  }

  renderWindow.render();
  await interactor.start();
}

// Bootstrap: wait for VTK.wasm namespace then build the scene
if (typeof vtkReady !== "undefined") {
  // Annotation-based loading: vtkReady is set by the UMD script
  void vtkReady.then(buildScene);
} else if (typeof vtkWASM !== "undefined") {
  // Manual loading: create namespace ourselves
  void vtkWASM.createNamespace().then(buildScene);
}

/**
 * Add custom lights to the renderer, replacing the defaults.
 * @param vtk
 * @param lightsConfig
 * @param ren
 * @returns Nothing; mutates the renderer in place.
 */
function setupLights(
  vtk: VtkWasmNamespace,
  lightsConfig: LightConfig[],
  ren: VtkRenderer,
): void {
  if (lightsConfig.length === 0) {
    return;
  }

  ren.removeAllLights();
  ren.setAutomaticLightCreation(false);
  for (const cfg of lightsConfig) {
    const light = vtk.vtkLight();
    const typeMap: Record<string, string> = {
      scene: "setLightTypeToSceneLight",
      camera: "setLightTypeToCameraLight",
      head: "setLightTypeToHeadLight",
    };
    const setter = typeMap[cfg.type] ?? "setLightTypeToSceneLight";
    const setterFunction = light[setter];
    if (typeof setterFunction === "function") {
      (setterFunction as () => void).call(light);
    }

    light.setPosition(cfg.position[0], cfg.position[1], cfg.position[2]);
    light.setFocalPoint(cfg.focalPoint[0], cfg.focalPoint[1], cfg.focalPoint[2]);
    light.setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
    light.setIntensity(cfg.intensity);
    light.setPositional(cfg.positional);
    light.setConeAngle(cfg.coneAngle);
    light.setExponent(cfg.coneFalloff);
    light.setAttenuationValues(
      cfg.attenuationValues[0],
      cfg.attenuationValues[1],
      cfg.attenuationValues[2],
    );
    ren.addLight(light);
  }
}

/**
 * Dispatch to the appropriate source factory based on `cfg.type`.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} for the configured source type, or `undefined` if unknown.
 */
function createSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult | undefined {
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

    case "mesh": {
      return createMeshSource(vtk, cfg);
    }

    case "points": {
      return createPointsSource(vtk, cfg);
    }

    default: {
      console.error("Unknown source type:", cfg.type);
      return undefined;
    }
  }
}

/**
 * Create a sphere source.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the sphere source.
 */
function createSphereSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const source = vtk.vtkSphereSource({
    center: cfg.center,
    radius: cfg.radius,
    thetaResolution: cfg.thetaResolution,
    phiResolution: cfg.phiResolution,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a cone source.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the cone source filter.
 */
function createConeSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const source = vtk.vtkConeSource({
    height: cfg.height,
    radius: cfg.radius,
    resolution: cfg.resolution,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a cube source.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the cube source.
 */
function createCubeSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const source = vtk.vtkCubeSource({
    xLength: cfg.xLength,
    yLength: cfg.yLength,
    zLength: cfg.zLength,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a cylinder source.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the cylinder source filter.
 */
function createCylinderSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const source = vtk.vtkCylinderSource({
    height: cfg.height,
    radius: cfg.radius,
    resolution: cfg.resolution,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a disk source, falling back to empty PolyData if unavailable.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the disk source or empty PolyData fallback.
 */
function createDiskSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const diskFactory = vtk.vtkDiskSource;
  const source = diskFactory
    ? diskFactory({
        innerRadius: cfg.innerRadius,
        outerRadius: cfg.outerRadius,
        radialResolution: 1,
        circumferentialResolution: cfg.resolution,
      })
    : undefined;
  return {
    output: source ?? vtk.vtkPolyData(),
    isFilter: true,
  };
}

/**
 * Create a circle source (disk with `innerRadius=0`).
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the disk source configured as a circle.
 */
function createCircleSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  return createDiskSource(vtk, {
    type: "disk",
    innerRadius: 0,
    outerRadius: cfg.radius ?? 1,
    resolution: cfg.resolution ?? 50,
  });
}

/**
 * Create an arrow source.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the arrow source filter.
 */
function createArrowSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const source = vtk.vtkArrowSource({
    tipLength: cfg.tipLength,
    tipRadius: cfg.tipRadius,
    shaftRadius: cfg.shaftRadius,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a line source between two points.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the line source filter.
 */
function createLineSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const source = vtk.vtkLineSource({
    point1: cfg.point1,
    point2: cfg.point2,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a plane source with optional normal.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the plane source filter.
 */
function createPlaneSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const source = vtk.vtkPlaneSource({
    origin: cfg.origin,
  });
  if (cfg.normal) {
    source.setNormal?.(cfg.normal[0], cfg.normal[1], cfg.normal[2]);
  }

  return { output: source, isFilter: true };
}

/**
 * Create PolyData from raw point and polygon arrays.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the constructed mesh PolyData.
 */
function createMeshSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const polydata = vtk.vtkPolyData();
  const pointsArray = Float32Array.from(cfg.points ?? []);
  const vtkPts = vtk.vtkPoints();
  vtkPts.setData(pointsArray, 3);
  polydata.setPoints(vtkPts);
  if (cfg.polys) {
    const polysArray = Uint32Array.from(cfg.polys);
    polydata.getPolys().setData(polysArray);
  }

  return { output: polydata, isFilter: false };
}

/**
 * Create a point cloud PolyData from raw point arrays.
 * @param vtk
 * @param cfg
 * @returns A {@link SourceResult} wrapping the point cloud PolyData.
 */
function createPointsSource(vtk: VtkWasmNamespace, cfg: SourceConfig): SourceResult {
  const polydata = vtk.vtkPolyData();
  const pointsArray = Float32Array.from(cfg.points ?? []);
  const vtkPts = vtk.vtkPoints();
  vtkPts.setData(pointsArray, 3);
  polydata.setPoints(vtkPts);
  return { output: polydata, isFilter: false };
}

/**
 * Inject per-point scalar/vector data arrays into PolyData.
 * @param vtk
 * @param polydata
 * @param pointDataArrays
 */
function injectPointData(
  vtk: VtkWasmNamespace,
  polydata: VtkPolyData,
  pointDataArrays: PointDataArray[] | undefined,
): void {
  if (!pointDataArrays) {
    return;
  }

  for (const array of pointDataArrays) {
    const dataArray = vtk.vtkFloatArray({
      numberOfComponents: array.numberOfComponents,
      values: Float32Array.from(array.values),
      name: array.name,
    });
    polydata.getPointData().addArray(dataArray);
  }
}

/**
 * Inject 2-component texture coordinates into PolyData.
 * @param vtk
 * @param polydata
 * @param tCoords
 */
function injectTcoords(
  vtk: VtkWasmNamespace,
  polydata: VtkPolyData,
  tCoords: number[] | undefined,
): void {
  if (!tCoords) {
    return;
  }

  const tcArray = vtk.vtkFloatArray({
    numberOfComponents: 2,
    values: Float32Array.from(tCoords),
    name: "TextureCoordinates",
  });
  polydata.getPointData().setTcoords(tcArray);
}

/**
 * Optionally insert a normals-computation filter between source and mapper.
 * @param vtk
 * @param sourceResult
 * @param normalsConfig
 * @returns The original {@link SourceResult} if no normals config, otherwise a new one.
 */
function setupNormals(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  normalsConfig: NormalsConfig | undefined,
): SourceResult {
  if (!normalsConfig) {
    return sourceResult;
  }

  const normals = vtk.vtkPolyDataNormals();
  normals.setComputePointNormals?.(normalsConfig.computePointNormals);
  normals.setComputeCellNormals?.(normalsConfig.computeCellNormals);
  connectInput(normals, sourceResult);
  return { output: normals, isFilter: true };
}

/**
 * Apply physically-based rendering properties to an actor.
 * @param actor
 * @param pbr
 */
function applyPbr(actor: VtkActor, pbr: PbrConfig | undefined): void {
  if (!pbr) return;
  actor.getProperty().setInterpolationToPhong();
  const m = pbr.metallic;
  const r = pbr.roughness;
  actor.getProperty().setMetallic(m);
  actor.getProperty().setRoughness(r);
  actor.getProperty().setAmbient(0.1);
  actor.getProperty().setSpecular(0.75 * m + 0.25);
  actor.getProperty().setSpecularPower(Math.max(1, 100 * (1 - r)));
  actor.getProperty().setDiffuse(0.65 + 0.35 * (1 - m));
}

/**
 * Build a complete VTK.wasm actor from an {@link ActorConfig} and add it to the renderer.
 * @param vtk
 * @param cfg
 * @param _index
 * @param ren
 */
function setupActor(
  vtk: VtkWasmNamespace,
  cfg: ActorConfig,
  _index: number,
  ren: VtkRenderer,
): void {
  const sourceResult = createSource(vtk, cfg.source);
  if (!sourceResult?.output) {
    return;
  }

  if (cfg.source.pointData ?? cfg.source.tCoords) {
    const pd = getPolyData(sourceResult);
    injectPointData(vtk, pd, cfg.source.pointData);
    injectTcoords(vtk, pd, cfg.source.tCoords);
  }

  let currentResult = sourceResult;
  if (cfg.source.filters && cfg.source.filters.length > 0) {
    currentResult = applyFilters(vtk, sourceResult, cfg.source.filters);
  }

  const mapperInput = setupNormals(vtk, currentResult, cfg.normals);

  const mapper = vtk.vtkPolyDataMapper();
  if (mapperInput.isFilter) {
    mapper.setInputConnection((mapperInput.output as VtkAlgorithm).getOutputPort());
  } else {
    mapper.setInputData(mapperInput.output as VtkPolyData);
  }

  const actor = vtk.vtkActor({ mapper });
  actor.getProperty().setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
  actor.getProperty().setOpacity(cfg.opacity);

  const styleMap: Record<string, number> = {
    surface: 2,
    wireframe: 1,
    points: 0,
  };
  const rep = styleMap[cfg.style];
  if (rep !== undefined) {
    actor.getProperty().setRepresentation(rep);
  }

  if (cfg.shading === "gouraud") {
    actor.getProperty().setInterpolationToGouraud();
  } else if (cfg.shading === "flat") {
    actor.getProperty().setInterpolationToFlat();
  }

  if (cfg.edges) {
    actor.getProperty().setEdgeVisibility(true);
    actor.getProperty().setEdgeColor(cfg.edges.color[0], cfg.edges.color[1], cfg.edges.color[2]);
  }

  applyPbr(actor, cfg.pbr);

  if (cfg.actorType === "points") {
    actor.getProperty().setPointSize(cfg.pointSize ?? 5);
    actor.getProperty().setRepresentationToPoints();
  }

  ren.addActor(actor);
}

/**
 * Apply camera settings from the scene configuration.
 * @param ren
 * @param camConfig
 */
function setupCamera(ren: VtkRenderer, camConfig: CameraConfig): void {
  const cam = ren.getActiveCamera();
  if (camConfig.position) {
    cam.setPosition(camConfig.position[0], camConfig.position[1], camConfig.position[2]);
  }

  if (camConfig.focalPoint) {
    cam.setFocalPoint(camConfig.focalPoint[0], camConfig.focalPoint[1], camConfig.focalPoint[2]);
  }

  if (camConfig.viewUp) {
    cam.setViewUp(camConfig.viewUp[0], camConfig.viewUp[1], camConfig.viewUp[2]);
  }

  if (camConfig.viewAngle !== undefined) {
    cam.setViewAngle(camConfig.viewAngle);
  }

  if (camConfig.clippingRange) {
    cam.setClippingRange(camConfig.clippingRange[0], camConfig.clippingRange[1]);
  }

  if (camConfig.parallelProjection) {
    cam.setParallelProjection(true);
  }

  if (camConfig.viewVector && camConfig.viewUp) {
    cam.setPosition(camConfig.viewVector[0], camConfig.viewVector[1], camConfig.viewVector[2]);
    cam.setViewUp(camConfig.viewUp[0], camConfig.viewUp[1], camConfig.viewUp[2]);
    cam.setFocalPoint(0, 0, 0);
    ren.resetCamera();
    ren.resetCameraClippingRange();
  }
}

/**
 * Create an absolutely-positioned HTML overlay for 2D text.
 * @param cfg
 * @param containerElement
 */
function setupTextActor(cfg: TextActorConfig, containerElement: HTMLElement): void {
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

/**
 * Apply a chain of filters (shrink, tube) to a source.
 * @param vtk
 * @param sourceResult
 * @param filters
 * @returns The final {@link SourceResult} after all filters have been applied in sequence.
 */
function applyFilters(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  filters: FilterConfig[],
): SourceResult {
  let current = sourceResult;
  for (const f of filters) {
    if (f.type === "shrink" && f.shrinkFactor !== undefined) {
      current = applyShrinkFilter(vtk, current, f.shrinkFactor);
    } else if (f.type === "tube" && f.radius !== undefined && f.numberOfSides !== undefined) {
      current = applyTubeFilter(vtk, current, f.radius, f.numberOfSides);
    } else if (f.type === "clip" && f.normal && f.origin && f.invert !== undefined) {
      current = applyClipManual(vtk, current, f.normal, f.origin, f.invert);
    } else if (f.type === "contour" && f.values && f.scalarName && f.scalarData) {
      current = applyContourFilter(vtk, current, f.values, f.scalarName, f.scalarData);
    }
  }

  return current;
}

/**
 * Manual shrink filter — move each cell's vertices toward its centroid.
 * @param vtk
 * @param sourceResult
 * @param shrinkFactor
 * @returns A {@link SourceResult} with each cell shrunk toward its centroid.
 */
function applyShrinkFilter(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  shrinkFactor: number,
): SourceResult {
  const inputPd = getPolyData(sourceResult);
  const inPoints = inputPd.getPoints().getData();
  const polys = inputPd.getPolys().getData();
  if (polys.length === 0) {
    return sourceResult;
  }

  const resultPoints: number[] = [];
  const resultPolys: number[] = [];
  let offset = 0;
  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    index++;
    let cx = 0;
    let cy = 0;
    let cz = 0;
    const indices: number[] = [];
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
      const pi = indices[k] ?? 0;
      const px = at(inPoints, pi * 3);
      const py = at(inPoints, pi * 3 + 1);
      const pz = at(inPoints, pi * 3 + 2);
      resultPoints.push(
        cx + (px - cx) * shrinkFactor,
        cy + (py - cy) * shrinkFactor,
        cz + (pz - cz) * shrinkFactor,
      );
      resultPolys.push(offset + k);
    }

    offset += nVerts;
    index += nVerts;
  }

  const outputPd = vtk.vtkPolyData();
  outputPd.getPoints().setData(new Float32Array(resultPoints), 3);
  outputPd.getPolys().setData(new Uint32Array(resultPolys));
  return { output: outputPd, isFilter: false };
}

/**
 * Apply a tube filter to thicken line geometry.
 * @param vtk
 * @param sourceResult
 * @param radius
 * @param numberOfSides
 * @returns A {@link SourceResult} with a tube filter applied.
 */
function applyTubeFilter(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  radius: number,
  numberOfSides: number,
): SourceResult {
  const tubeFilter = vtk.vtkTubeFilter({
    radius,
    numberOfSides,
  });
  connectInput(tubeFilter, sourceResult);
  return { output: tubeFilter, isFilter: true };
}

/**
 * Manual clip — discard cells whose centroid is on the wrong side of a plane.
 * @param vtk
 * @param sourceResult
 * @param normal
 * @param origin
 * @param invert
 * @returns A {@link SourceResult} containing only kept cells.
 */
function applyClipManual(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  normal: [number, number, number],
  origin: [number, number, number],
  invert: boolean,
): SourceResult {
  const inputPd = getPolyData(sourceResult);
  const inPoints = inputPd.getPoints().getData();
  const polys = inputPd.getPolys().getData();
  if (polys.length === 0) {
    return sourceResult;
  }

  const [nx, ny, nz] = normal;
  const [ox, oy, oz] = origin;

  const resultPoints: number[] = [];
  const resultPolys: number[] = [];
  const pointMap = new Map<number, number>();
  let nextIndex = 0;
  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    index++;
    let cx = 0;
    let cy = 0;
    let cz = 0;
    const cellIndices: number[] = [];
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
        const pi = cellIndices[k] ?? 0;
        if (!pointMap.has(pi)) {
          pointMap.set(pi, nextIndex++);
          resultPoints.push(
            at(inPoints, pi * 3),
            at(inPoints, pi * 3 + 1),
            at(inPoints, pi * 3 + 2),
          );
        }

        resultPolys.push(pointMap.get(pi) ?? 0);
      }
    }

    index += nVerts;
  }

  const outputPd = vtk.vtkPolyData();
  outputPd.getPoints().setData(new Float32Array(resultPoints), 3);
  outputPd.getPolys().setData(new Uint32Array(resultPolys));
  return { output: outputPd, isFilter: false };
}

/**
 * Inject scalar data into PolyData and extract isocontour lines.
 * @param vtk
 * @param sourceResult
 * @param values
 * @param scalarName
 * @param scalarData
 * @returns A {@link SourceResult} containing the extracted isocontour lines.
 */
function applyContourFilter(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  values: number[],
  scalarName: string,
  scalarData: number[],
): SourceResult {
  const inputPd = getPolyData(sourceResult);

  const scalars = vtk.vtkFloatArray({
    numberOfComponents: 1,
    values: Float32Array.from(scalarData),
    name: scalarName,
  });
  inputPd.getPointData().addArray(scalars);
  inputPd.getPointData().setActiveScalars(scalarName);

  return applyContourManual(vtk, inputPd, values, scalarName);
}

/**
 * Collect the intersection points of a contour value along the edges of a triangle.
 * @param tri
 * @param value
 * @param inPoints
 * @returns Flat array of intersection coordinates (0 or 6 elements).
 */
function collectEdgeIntersections(
  tri: Array<[number, number, number, number]>,
  value: number,
  inPoints: Float32Array | Uint32Array,
): number[] {
  const edgePoints: number[] = [];
  for (const edge of tri) {
    const [ai, bi, sa, sb] = edge;
    if ((sa <= value && value < sb) || (sb <= value && value < sa)) {
      const t = (value - sa) / (sb - sa);
      edgePoints.push(
        at(inPoints, ai * 3) + t * (at(inPoints, bi * 3) - at(inPoints, ai * 3)),
        at(inPoints, ai * 3 + 1) + t * (at(inPoints, bi * 3 + 1) - at(inPoints, ai * 3 + 1)),
        at(inPoints, ai * 3 + 2) + t * (at(inPoints, bi * 3 + 2) - at(inPoints, ai * 3 + 2)),
      );
    }
  }

  return edgePoints;
}

/**
 * Manual marching-triangles contour extraction.
 * @param vtk
 * @param inputPd
 * @param values
 * @param scalarName
 * @returns A {@link SourceResult} containing the marching-triangles contour line segments.
 */
function applyContourManual(
  vtk: VtkWasmNamespace,
  inputPd: VtkPolyData,
  values: number[],
  scalarName: string,
): SourceResult {
  const inPoints = inputPd.getPoints().getData();
  const polys = inputPd.getPolys().getData();
  const scalarsArray = inputPd.getPointData().getArrayByName(scalarName);
  if (polys.length === 0 || !scalarsArray) {
    return { output: inputPd, isFilter: false };
  }

  const scalarValues = scalarsArray.getData();

  const outPoints: number[] = [];
  const outPolys: number[] = [];
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
      const tri: Array<[number, number, number, number]> = [
        [index0, index1, s0, s1],
        [index1, index2, s1, s2],
        [index2, index0, s2, s0],
      ];
      for (const value of values) {
        const edgePoints = collectEdgeIntersections(tri, value, inPoints);

        if (edgePoints.length === 6) {
          outPoints.push(
            edgePoints[0] ?? 0,
            edgePoints[1] ?? 0,
            edgePoints[2] ?? 0,
            edgePoints[3] ?? 0,
            edgePoints[4] ?? 0,
            edgePoints[5] ?? 0,
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
    outputPd.getPoints().setData(new Float32Array(outPoints), 3);
    outputPd.getLines().setData(new Uint32Array(outPolys));
  }

  return { output: outputPd, isFilter: false };
}
