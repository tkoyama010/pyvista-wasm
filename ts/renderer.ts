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
 *
 * IMPORTANT: VTK.wasm getter methods (getProperty, getActiveCamera,
 * getOutputPort, getPoints, getPolys, getPointData, getData,
 * getOutputData, etc.) all return Promises and must be awaited.
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
async function getPolyData(sourceResult: SourceResult): Promise<VtkPolyData> {
  if (sourceResult.isFilter) {
    (sourceResult.output as VtkAlgorithm).update();
    return await (sourceResult.output as VtkAlgorithm).getOutputData();
  }

  return sourceResult.output as VtkPolyData;
}

/**
 * Wire `filter`'s input to the output of `sourceResult`.
 * @param filter
 * @param sourceResult
 */
async function connectInput(filter: VtkAlgorithm, sourceResult: SourceResult): Promise<void> {
  if (sourceResult.isFilter) {
    filter.setInputConnection(await (sourceResult.output as VtkAlgorithm).getOutputPort());
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
  canvas.tabIndex = -1;
  canvas.addEventListener("click", () => canvas.focus());
  container.append(canvas);

  const canvasSelector = `#${CSS.escape(canvasId)}`;
  const renderWindow = vtk.vtkRenderWindow({ canvasSelector });
  await renderWindow.addRenderer(renderer);

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

  // canvasSelector must match the canvas for Emscripten event callbacks
  const interactor = vtk.vtkRenderWindowInteractor({
    canvasSelector,
    renderWindow,
  });
  await interactor.interactorStyle.setCurrentStyleToTrackballCamera();

  renderWindow.render();
  await interactor.start();
}

// Bootstrap: wait for VTK.wasm namespace then build the scene
// eslint-disable-next-line unicorn/prefer-top-level-await -- conditional await not supported at top level
if (typeof vtkReady !== "undefined") {
  // Annotation-based loading: vtkReady is set by the UMD script
  void vtkReady.then(buildScene); // eslint-disable-line unicorn/prefer-top-level-await
} else if (typeof vtkWASM !== "undefined") {
  // Manual loading: create namespace ourselves
  void vtkWASM.createNamespace().then(buildScene); // eslint-disable-line unicorn/prefer-top-level-await
}

/**
 * Add custom lights to the renderer, replacing the defaults.
 * @param vtk
 * @param lightsConfig
 * @param ren
 * @returns Nothing; mutates the renderer in place.
 */
function setupLights(vtk: VtkWasmNamespace, lightsConfig: LightConfig[], ren: VtkRenderer): void {
  if (lightsConfig.length === 0) {
    return;
  }

  ren.removeAllLights();
  ren.setAutomaticLightCreation(0);
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
    light.setPositional(cfg.positional ? 1 : 0);
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
async function createMeshSource(vtk: VtkWasmNamespace, cfg: SourceConfig): Promise<SourceResult> {
  const polydata = vtk.vtkPolyData();
  const pointsArray = Float32Array.from(cfg.points ?? []);
  const vtkPts = vtk.vtkPoints();
  vtkPts.setData(pointsArray, 3);
  polydata.setPoints(vtkPts);
  if (cfg.polys) {
    const polysArray = Uint32Array.from(cfg.polys);
    (await polydata.getPolys()).setData(polysArray);
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
async function injectPointData(
  vtk: VtkWasmNamespace,
  polydata: VtkPolyData,
  pointDataArrays: PointDataArray[] | undefined,
): Promise<void> {
  if (!pointDataArrays) {
    return;
  }

  const pd = await polydata.getPointData();
  for (const array of pointDataArrays) {
    const dataArray = vtk.vtkFloatArray({
      numberOfComponents: array.numberOfComponents,
      values: Float32Array.from(array.values),
      name: array.name,
    });
    pd.addArray(dataArray);
  }
}

/**
 * Inject 2-component texture coordinates into PolyData.
 * @param vtk
 * @param polydata
 * @param tCoords
 */
async function injectTcoords(
  vtk: VtkWasmNamespace,
  polydata: VtkPolyData,
  tCoords: number[] | undefined,
): Promise<void> {
  if (!tCoords) {
    return;
  }

  const tcArray = vtk.vtkFloatArray({
    numberOfComponents: 2,
    values: Float32Array.from(tCoords),
    name: "TextureCoordinates",
  });
  (await polydata.getPointData()).setTcoords(tcArray);
}

/**
 * Optionally insert a normals-computation filter between source and mapper.
 * @param vtk
 * @param sourceResult
 * @param normalsConfig
 * @returns The original {@link SourceResult} if no normals config, otherwise a new one.
 */
async function setupNormals(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  normalsConfig: NormalsConfig | undefined,
): Promise<SourceResult> {
  if (!normalsConfig) {
    return sourceResult;
  }

  const normals = vtk.vtkPolyDataNormals();
  normals.setComputePointNormals?.(normalsConfig.computePointNormals ? 1 : 0);
  normals.setComputeCellNormals?.(normalsConfig.computeCellNormals ? 1 : 0);
  await connectInput(normals, sourceResult);
  return { output: normals, isFilter: true };
}

/**
 * Apply physically-based rendering properties to an actor.
 * @param actor
 * @param pbr
 */
async function applyPbr(actor: VtkActor, pbr: PbrConfig | undefined): Promise<void> {
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

/**
 * Build a complete VTK.wasm actor from an {@link ActorConfig} and add it to the renderer.
 * @param vtk
 * @param cfg
 * @param _index
 * @param ren
 */
async function setupActor(
  vtk: VtkWasmNamespace,
  cfg: ActorConfig,
  _index: number,
  ren: VtkRenderer,
): Promise<void> {
  let sourceResult: SourceResult | undefined;
  if (cfg.source.type === "mesh") {
    sourceResult = await createMeshSource(vtk, cfg.source);
  } else {
    sourceResult = createSource(vtk, cfg.source);
  }

  if (!sourceResult?.output) {
    return;
  }

  if (cfg.source.pointData ?? cfg.source.tCoords) {
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
    mapper.setInputConnection(await (mapperInput.output as VtkAlgorithm).getOutputPort());
  } else {
    mapper.setInputData(mapperInput.output as VtkPolyData);
  }

  const actor = vtk.vtkActor({ mapper });
  const prop = await actor.getProperty();
  prop.setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
  prop.setOpacity(cfg.opacity);

  const styleMap: Record<string, number> = {
    surface: 2,
    wireframe: 1,
    points: 0,
  };
  const rep = styleMap[cfg.style];
  if (rep !== undefined) {
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
    prop.setPointSize(cfg.pointSize ?? 5);
    prop.setRepresentationToPoints();
  }

  ren.addActor(actor);
}

/**
 * Apply camera settings from the scene configuration.
 * @param ren
 * @param camConfig
 */
async function setupCamera(ren: VtkRenderer, camConfig: CameraConfig): Promise<void> {
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

  if (camConfig.viewAngle !== undefined) {
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
async function applyFilters(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  filters: FilterConfig[],
): Promise<SourceResult> {
  let current = sourceResult;
  for (const f of filters) {
    if (f.type === "shrink" && f.shrinkFactor !== undefined) {
      current = await applyShrinkFilter(vtk, current, f.shrinkFactor);
    } else if (f.type === "tube" && f.radius !== undefined && f.numberOfSides !== undefined) {
      current = await applyTubeFilter(vtk, current, f.radius, f.numberOfSides);
    } else if (f.type === "clip" && f.normal && f.origin && f.invert !== undefined) {
      current = await applyClipManual(vtk, current, f.normal, f.origin, f.invert);
    } else if (f.type === "contour" && f.values && f.scalarName && f.scalarData) {
      current = await applyContourFilter(vtk, current, f.values, f.scalarName, f.scalarData);
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
async function applyShrinkFilter(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  shrinkFactor: number,
): Promise<SourceResult> {
  const inputPd = await getPolyData(sourceResult);
  const inPoints = await (await inputPd.getPoints()).getData();
  const polys = await (await inputPd.getPolys()).getData();
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
  (await outputPd.getPoints()).setData(new Float32Array(resultPoints), 3);
  (await outputPd.getPolys()).setData(new Uint32Array(resultPolys));
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
async function applyTubeFilter(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  radius: number,
  numberOfSides: number,
): Promise<SourceResult> {
  const tubeFilter = vtk.vtkTubeFilter({
    radius,
    numberOfSides,
  });
  await connectInput(tubeFilter, sourceResult);
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
async function applyClipManual(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  normal: [number, number, number],
  origin: [number, number, number],
  invert: boolean,
): Promise<SourceResult> {
  const inputPd = await getPolyData(sourceResult);
  const inPoints = await (await inputPd.getPoints()).getData();
  const polys = await (await inputPd.getPolys()).getData();
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
  (await outputPd.getPoints()).setData(new Float32Array(resultPoints), 3);
  (await outputPd.getPolys()).setData(new Uint32Array(resultPolys));
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
async function applyContourFilter(
  vtk: VtkWasmNamespace,
  sourceResult: SourceResult,
  values: number[],
  scalarName: string,
  scalarData: number[],
): Promise<SourceResult> {
  const inputPd = await getPolyData(sourceResult);

  const scalars = vtk.vtkFloatArray({
    numberOfComponents: 1,
    values: Float32Array.from(scalarData),
    name: scalarName,
  });
  const pd = await inputPd.getPointData();
  pd.addArray(scalars);
  pd.setActiveScalars(scalarName);

  return await applyContourManual(vtk, inputPd, values, scalarName);
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
async function applyContourManual(
  vtk: VtkWasmNamespace,
  inputPd: VtkPolyData,
  values: number[],
  scalarName: string,
): Promise<SourceResult> {
  const inPoints = await (await inputPd.getPoints()).getData();
  const polys = await (await inputPd.getPolys()).getData();
  const pointDataObj = await inputPd.getPointData();
  const scalarsArray = pointDataObj.getArrayByName(scalarName);
  if (polys.length === 0 || !scalarsArray) {
    return { output: inputPd, isFilter: false };
  }

  const scalarValues = await scalarsArray.getData();

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
    (await outputPd.getPoints()).setData(new Float32Array(outPoints), 3);
    (await outputPd.getLines()).setData(new Uint32Array(outPolys));
  }

  return { output: outputPd, isFilter: false };
}
