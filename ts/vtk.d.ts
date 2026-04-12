/**
 * Type declarations for the VTK.wasm namespace object.
 *
 * Only the APIs actually used by `renderer.ts` are declared here.
 * These correspond to the `vtk` namespace created by `vtkWASM.createNamespace()`
 * from the `@kitware/vtk-wasm` package.
 *
 * IMPORTANT: VTK.wasm getter methods return Promises and must be awaited.
 * Boolean parameters use number (0/1) instead of boolean due to C++ WASM bindings.
 */

/** A VTK.wasm render window that owns the canvas. */
type VtkRenderWindow = {
  render(): void;
  addRenderer(renderer: VtkRenderer): void;
  delete(): void;
};

/** A VTK.wasm renderer that holds actors, lights, and a camera. */
type VtkRenderer = {
  setBackground(r: number, g: number, b: number): void;
  addActor(actor: VtkActor): void;
  addLight(light: VtkLight): void;
  removeAllLights(): void;
  setAutomaticLightCreation(value: number): void;
  resetCamera(): void;
  resetCameraClippingRange(): void;
  getActiveCamera(): Promise<VtkCamera>;
  delete(): void;
};

/** A renderable entity in the scene that maps data through a mapper. */
type VtkActor = {
  getProperty(): Promise<VtkProperty>;
  delete(): void;
};

/** Controls surface appearance (color, opacity, shading, edges, PBR). */
type VtkProperty = {
  setColor(r: number, g: number, b: number): void;
  setOpacity(opacity: number): void;
  setRepresentation(mode: number): void;
  setRepresentationToPoints(): void;
  setEdgeVisibility(visible: number): void;
  setEdgeColor(r: number, g: number, b: number): void;
  setInterpolationToGouraud(): void;
  setInterpolationToFlat(): void;
  setInterpolationToPhong(): void;
  setMetallic(value: number): void;
  setRoughness(value: number): void;
  setAmbient(value: number): void;
  setSpecular(value: number): void;
  setSpecularPower(value: number): void;
  setDiffuse(value: number): void;
  setPointSize(size: number): void;
};

/** Maps data to graphics primitives for rendering. */
type VtkMapper = {
  setInputData(data: VtkPolyData): Promise<void>;
  setInputConnection(port: VtkOutputPort): Promise<void>;
  delete(): void;
};

/** Opaque handle representing a VTK output port. */
type VtkOutputPort = {
  readonly __brand: "VtkOutputPort";
};

/** Polygonal mesh data structure — the core VTK data object. */
type VtkPolyData = {
  getPoints(): Promise<VtkPoints>;
  setPoints(points: VtkPoints): Promise<void>;
  getPolys(): Promise<VtkCellArray>;
  setPolys(cellArray: VtkCellArray): Promise<void>;
  getLines(): Promise<VtkCellArray>;
  setLines(cellArray: VtkCellArray): Promise<void>;
  getPointData(): Promise<VtkPointData>;
  getNumberOfPoints(): Promise<number>;
  getNumberOfCells(): Promise<number>;
  delete(): void;
};

/** A set of 3D points. */
type VtkPoints = {
  setData(data: VtkDataArray): Promise<void>;
  setData(data: Float32Array, numberOfComponents: number): Promise<void>;
  getData(): Promise<Float32Array>;
};

/** A VTK cell array (polygons, lines, etc.). */
type VtkCellArray = {
  setData(offsets: VtkDataArray, connectivity: VtkDataArray): Promise<void>;
  setData(data: Uint32Array): Promise<void>;
  getData(): Promise<Uint32Array>;
};

/** Manages per-point data arrays (scalars, vectors, texture coordinates). */
type VtkPointData = {
  addArray(array: VtkDataArray): void;
  setTcoords(array: VtkDataArray): void;
  setActiveScalars(name: string): void;
  getArrayByName(name: string): VtkDataArray | undefined;
};

/** A VTK data array holding typed numeric values. */
type VtkDataArray = {
  /** Transfer typed-array values into the C++ VTK array (bypasses JSON serialization). */
  setArray(data: Float32Array | Int32Array): Promise<void>;
  getData(): Promise<Float32Array>;
};

/** A virtual camera controlling the viewpoint. */
type VtkCamera = {
  setPosition(x: number, y: number, z: number): void;
  setFocalPoint(x: number, y: number, z: number): void;
  setViewUp(x: number, y: number, z: number): void;
  setViewAngle(angle: number): void;
  setClippingRange(near: number, far: number): void;
  setParallelProjection(value: number): void;
};

/** A scene light with position, color, and cone parameters. */
type VtkLight = {
  [key: string]: ((...arguments_: number[]) => void) | undefined;
  setPosition(x: number, y: number, z: number): void;
  setFocalPoint(x: number, y: number, z: number): void;
  setColor(r: number, g: number, b: number): void;
  setIntensity(intensity: number): void;
  setPositional(value: number): void;
  setConeAngle(angle: number): void;
  setExponent(value: number): void;
  setAttenuationValues(a: number, b: number, c: number): void;
  setLightTypeToSceneLight(): void;
  setLightTypeToCameraLight(): void;
  setLightTypeToHeadLight(): void;
  delete(): void;
};

/** A VTK algorithm (filter or source) with input/output pipeline. */
type VtkAlgorithm = {
  getOutputPort(): Promise<VtkOutputPort>;
  getOutputData(): Promise<VtkPolyData>;
  update(): Promise<void>;
  setInputConnection(port: VtkOutputPort): Promise<void>;
  setInputData(data: VtkPolyData): Promise<void>;
  setComputePointNormals?: (v: number) => void;
  setComputeCellNormals?: (v: number) => void;
  setNormal?: (x: number, y: number, z: number) => void;
  delete(): void;
};

/** An implicit plane defined by origin and normal. */
type VtkPlane = {
  setOrigin(x: number, y: number, z: number): void;
  setNormal(x: number, y: number, z: number): void;
};

/** Handles user interaction events (mouse, keyboard, touch). */
type VtkInteractor = {
  interactorStyle: VtkInteractorStyleManager;
  start(): Promise<void>;
  delete(): void;
};

/** Manages interactor style selection. */
type VtkInteractorStyleManager = {
  setCurrentStyleToTrackballCamera(): Promise<void>;
};

/** A trackball camera interaction style. */
type VtkInteractorStyle = {
  readonly __brand: "VtkInteractorStyle";
  delete(): void;
};

/** An image-based texture applied to actor surfaces. */
type VtkTexture = {
  setInterpolate(value: number): void;
  setImage(img: HTMLImageElement): void;
  delete(): void;
};

/**
 * The VTK.wasm namespace object created by `vtkWASM.createNamespace()`.
 *
 * In VTK.wasm, objects are created by calling factory functions directly
 * on the namespace (e.g., `vtk.vtkRenderer()`) rather than through
 * a nested hierarchy like vtk.js.
 */
type VtkWasmNamespace = {
  vtkRenderWindow(options?: { canvasSelector?: string }): VtkRenderWindow;
  vtkRenderer(): VtkRenderer;
  vtkActor(options?: { mapper?: VtkMapper }): VtkActor;
  vtkPolyDataMapper(): VtkMapper;
  vtkPolyData(): VtkPolyData;
  vtkPoints(): VtkPoints;
  vtkCellArray(): VtkCellArray;
  vtkFloatArray: (options?: {
    numberOfComponents?: number;
    name?: string;
    values?: Float32Array;
  }) => VtkDataArray;
  vtkIntArray: (options?: {
    numberOfComponents?: number;
    name?: string;
  }) => VtkDataArray;
  vtkLight(): VtkLight;
  vtkCamera(): VtkCamera;
  vtkRenderWindowInteractor: (options?: {
    canvasSelector?: string;
    renderWindow?: VtkRenderWindow;
  }) => VtkInteractor;
  vtkSphereSource(options?: Record<string, unknown>): VtkAlgorithm;
  vtkConeSource(options?: Record<string, unknown>): VtkAlgorithm;
  vtkCubeSource(options?: Record<string, unknown>): VtkAlgorithm;
  vtkCylinderSource(options?: Record<string, unknown>): VtkAlgorithm;
  vtkDiskSource?: (options?: Record<string, unknown>) => VtkAlgorithm;
  vtkArrowSource(options?: Record<string, unknown>): VtkAlgorithm;
  vtkLineSource(options?: Record<string, unknown>): VtkAlgorithm;
  vtkPlaneSource(options?: Record<string, unknown>): VtkAlgorithm;
  vtkPolyDataNormals(): VtkAlgorithm;
  vtkTubeFilter(options?: Record<string, unknown>): VtkAlgorithm;
  vtkClipPolyData(): VtkAlgorithm & {
    setClipFunction(plane: VtkPlane): void;
    setInsideOut(value: number): void;
  };
  vtkPlane(): VtkPlane;
  vtkTexture(): VtkTexture;
};

/** Configuration for a single light in the scene. */
type LightConfig = {
  type: string;
  position: [number, number, number];
  focalPoint: [number, number, number];
  color: [number, number, number];
  intensity: number;
  positional: boolean;
  coneAngle: number;
  coneFalloff: number;
  attenuationValues: [number, number, number];
};

/** Configuration for surface normal computation. */
type NormalsConfig = {
  computePointNormals: boolean;
  computeCellNormals: boolean;
};

/** A named array of per-point data values. */
type PointDataArray = {
  numberOfComponents: number;
  values: number[];
  name: string;
};

/** Configuration for a geometry filter (shrink, tube, clip, or contour). */
type FilterConfig = {
  type: string;
  shrinkFactor?: number;
  radius?: number;
  numberOfSides?: number;
  normal?: [number, number, number];
  origin?: [number, number, number];
  invert?: boolean;
  values?: number[];
  scalarName?: string;
  scalarData?: number[];
};

/** Configuration for a geometry source (primitive, mesh, or file reader). */
type SourceConfig = {
  type: string;
  center?: [number, number, number];
  radius?: number;
  thetaResolution?: number;
  phiResolution?: number;
  height?: number;
  resolution?: number;
  xLength?: number;
  yLength?: number;
  zLength?: number;
  innerRadius?: number;
  outerRadius?: number;
  tipLength?: number;
  tipRadius?: number;
  shaftRadius?: number;
  point1?: [number, number, number];
  point2?: [number, number, number];
  origin?: [number, number, number];
  normal?: [number, number, number];
  points?: number[];
  polys?: number[];
  data?: string;
  pointData?: PointDataArray[];
  tCoords?: number[];
  filters?: FilterConfig[];
};

/** Edge rendering configuration. */
type EdgesConfig = {
  color: [number, number, number];
};

/** Physically-based rendering parameters. */
type PbrConfig = {
  metallic: number;
  roughness: number;
};

/** Configuration for an image texture loaded from a URL. */
type TextureConfig = {
  url: string;
};

/** Full configuration for a single actor in the scene. */
type ActorConfig = {
  source: SourceConfig;
  color: [number, number, number];
  opacity: number;
  style: string;
  shading?: string;
  edges?: EdgesConfig;
  pbr?: PbrConfig;
  normals?: NormalsConfig;
  actorType?: string;
  renderPointsAsSpheres?: boolean;
  pointSize?: number;
  texture?: TextureConfig;
};

/** Camera position and projection settings. */
type CameraConfig = {
  position?: [number, number, number];
  focalPoint?: [number, number, number];
  viewUp?: [number, number, number];
  viewAngle?: number;
  clippingRange?: [number, number];
  parallelProjection?: boolean;
  viewVector?: [number, number, number];
};

/** Configuration for a 2D text overlay. */
type TextActorConfig = {
  text: string;
  position: [number, number];
  color: [number, number, number];
  opacity: number;
  fontSize: number;
  bold: boolean;
  italic: boolean;
};

/** VTK.wasm configuration options for createNamespace(). */
type WasmConfig = {
  rendering?: "webgl" | "webgpu";
  mode?: "sync" | "async";
};

/** Top-level scene description passed from Python as JSON. */
type SceneData = {
  containerId: string;
  background: [number, number, number];
  lightingMode: string | undefined;
  lights: LightConfig[];
  actors: ActorConfig[];
  textActors?: TextActorConfig[];
  axes: boolean;
  camera?: CameraConfig;
  wasmConfig?: WasmConfig;
};

declare const __pvwasmSceneData: SceneData | undefined;
declare const __pvwasmContainer: HTMLElement | undefined;

/**
 * The vtkWASM global loaded from the UMD script.
 * Provides createNamespace() to initialise the VTK.wasm runtime.
 */
// eslint-disable-next-line @typescript-eslint/naming-convention -- external API name from @kitware/vtk-wasm
declare const vtkWASM: {
  createNamespace: (
    url?: string,
    config?: WasmConfig,
  ) => Promise<VtkWasmNamespace>;
};

/**
 * The vtkReady promise is set when using the data-url annotation approach.
 */
declare const vtkReady: Promise<VtkWasmNamespace> | undefined;
