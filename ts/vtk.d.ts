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

// biome-ignore lint/nursery/noExcessiveLinesPerFile: VTK type declarations require comprehensive definitions
/** A VTK.wasm render window that owns the canvas. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
// biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method signature style
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkRenderWindow = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  render(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  addRenderer(renderer: VtkRenderer): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** A VTK.wasm renderer that holds actors, lights, and a camera. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkRenderer = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setBackground(r: number, g: number, b: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  addActor(actor: VtkActor): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  addLight(light: VtkLight): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  removeAllLights(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setAutomaticLightCreation(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  resetCamera(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  resetCameraClippingRange(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getActiveCamera(): Promise<VtkCamera>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** A renderable entity in the scene that maps data through a mapper. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkActor = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getProperty(): Promise<VtkProperty>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** Controls surface appearance (color, opacity, shading, edges, PBR). */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkProperty = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setColor(r: number, g: number, b: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setOpacity(opacity: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setRepresentation(mode: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setRepresentationToPoints(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setEdgeVisibility(visible: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setEdgeColor(r: number, g: number, b: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setInterpolationToGouraud(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setInterpolationToFlat(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setInterpolationToPhong(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setMetallic(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setRoughness(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setAmbient(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setSpecular(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setSpecularPower(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setDiffuse(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setPointSize(size: number): void;
};

/** Maps data to graphics primitives for rendering. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkMapper = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setInputData(data: VtkPolyData): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setInputConnection(port: VtkOutputPort): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** Opaque handle representing a VTK output port. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkOutputPort = {
  readonly __brand: "VtkOutputPort";
};

/** Polygonal mesh data structure — the core VTK data object. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkPolyData = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getPoints(): Promise<VtkPoints>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setPoints(points: VtkPoints): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getPolys(): Promise<VtkCellArray>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setPolys(cellArray: VtkCellArray): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getLines(): Promise<VtkCellArray>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setLines(cellArray: VtkCellArray): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getPointData(): Promise<VtkPointData>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getNumberOfPoints(): Promise<number>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getNumberOfCells(): Promise<number>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** A set of 3D points. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkPoints = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setData(data: VtkDataArray): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setData(data: Float32Array, numberOfComponents: number): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getData(): Promise<Float32Array>;
};

/** A VTK cell array (polygons, lines, etc.). */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkCellArray = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setData(offsets: VtkDataArray, connectivity: VtkDataArray): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setData(data: Uint32Array): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getData(): Promise<Uint32Array>;
};

/** Manages per-point data arrays (scalars, vectors, texture coordinates). */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkPointData = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  addArray(array: VtkDataArray): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setTcoords(array: VtkDataArray): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setActiveScalars(name: string): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getArrayByName(name: string): VtkDataArray | undefined;
};

/** A VTK data array holding typed numeric values. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkDataArray = {
  /** Transfer typed-array values into the C++ VTK array (bypasses JSON serialization). */
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setArray(data: Float32Array | Int32Array): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getData(): Promise<Float32Array>;
};

/** A virtual camera controlling the viewpoint. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkCamera = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setPosition(x: number, y: number, z: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setFocalPoint(x: number, y: number, z: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setViewUp(x: number, y: number, z: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setViewAngle(angle: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setClippingRange(near: number, far: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setParallelProjection(value: number): void;
};

/** A scene light with position, color, and cone parameters. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkLight = {
  [key: string]: ((...arguments_: number[]) => void) | undefined;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setPosition(x: number, y: number, z: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setFocalPoint(x: number, y: number, z: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setColor(r: number, g: number, b: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setIntensity(intensity: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setPositional(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setConeAngle(angle: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setExponent(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setAttenuationValues(a: number, b: number, c: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setLightTypeToSceneLight(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setLightTypeToCameraLight(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setLightTypeToHeadLight(): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** A VTK algorithm (filter or source) with input/output pipeline. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkAlgorithm = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getOutputPort(): Promise<VtkOutputPort>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  getOutputData(): Promise<VtkPolyData>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  update(): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setInputConnection(port: VtkOutputPort): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setInputData(data: VtkPolyData): Promise<void>;
  setComputePointNormals?: (v: number) => void;
  setComputeCellNormals?: (v: number) => void;
  setNormal?: (x: number, y: number, z: number) => void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** An implicit plane defined by origin and normal. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkPlane = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setOrigin(x: number, y: number, z: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setNormal(x: number, y: number, z: number): void;
};

/** Handles user interaction events (mouse, keyboard, touch). */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkInteractor = {
  interactorStyle: VtkInteractorStyleManager;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  start(): Promise<void>;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** Manages interactor style selection. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkInteractorStyleManager = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setCurrentStyleToTrackballCamera(): Promise<void>;
};

/** A trackball camera interaction style. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkInteractorStyle = {
  readonly __brand: "VtkInteractorStyle";
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/** An image-based texture applied to actor surfaces. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkTexture = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setInterpolate(value: number): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  setImage(img: HTMLImageElement): void;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  delete(): void;
};

/**
 * The VTK.wasm namespace object created by `vtkWASM.createNamespace()`.
 *
 * In VTK.wasm, objects are created by calling factory functions directly
 * on the namespace (e.g., `vtk.vtkRenderer()`) rather than through
 * a nested hierarchy like vtk.js.
 */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type VtkWasmNamespace = {
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkRenderWindow(options?: { canvasSelector?: string }): VtkRenderWindow;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkRenderer(): VtkRenderer;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkActor(options?: { mapper?: VtkMapper }): VtkActor;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkPolyDataMapper(): VtkMapper;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkPolyData(): VtkPolyData;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkPoints(): VtkPoints;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
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
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkLight(): VtkLight;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkCamera(): VtkCamera;
  vtkRenderWindowInteractor: (options?: {
    canvasSelector?: string;
    renderWindow?: VtkRenderWindow;
  }) => VtkInteractor;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkSphereSource(options?: Record<string, unknown>): VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkConeSource(options?: Record<string, unknown>): VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkCubeSource(options?: Record<string, unknown>): VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkCylinderSource(options?: Record<string, unknown>): VtkAlgorithm;
  vtkDiskSource?: (options?: Record<string, unknown>) => VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkArrowSource(options?: Record<string, unknown>): VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkLineSource(options?: Record<string, unknown>): VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkPlaneSource(options?: Record<string, unknown>): VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkPolyDataNormals(): VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkTubeFilter(options?: Record<string, unknown>): VtkAlgorithm;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkClipPolyData(): VtkAlgorithm & {
    // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
    setClipFunction(plane: VtkPlane): void;
    // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
    setInsideOut(value: number): void;
  };
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkPlane(): VtkPlane;
  // biome-ignore lint/nursery/useConsistentMethodSignatures: Keeping existing method style
  vtkTexture(): VtkTexture;
};

/** Configuration for a single light in the scene. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
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
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type NormalsConfig = {
  computePointNormals: boolean;
  computeCellNormals: boolean;
};

/** A named array of per-point data values. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type PointDataArray = {
  numberOfComponents: number;
  values: number[];
  name: string;
};

/** Configuration for a geometry filter (shrink, tube, clip, or contour). */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
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
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
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
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type EdgesConfig = {
  color: [number, number, number];
};

/** Physically-based rendering parameters. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type PbrConfig = {
  metallic: number;
  roughness: number;
};

/** Configuration for an image texture loaded from a URL. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type TextureConfig = {
  url: string;
};

/** Full configuration for a single actor in the scene. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
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
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
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
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type TextActorConfig = {
  text: string;
  position: [number, number];
  color: [number, number, number];
  opacity: number;
  fontSize: number;
  bold: boolean;
  italic: boolean;
};

/** Top-level scene description passed from Python as JSON. */
// biome-ignore lint/style/useConsistentTypeDefinitions: Keeping existing type alias style
type SceneData = {
  containerId: string;
  background: [number, number, number];
  lightingMode: string | undefined;
  lights: LightConfig[];
  actors: ActorConfig[];
  textActors?: TextActorConfig[];
  axes: boolean;
  camera?: CameraConfig;
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
    config?: { rendering?: string; mode?: string },
  ) => Promise<VtkWasmNamespace>;
};

/**
 * The vtkReady promise is set when using the data-url annotation approach.
 */
declare const vtkReady: Promise<VtkWasmNamespace> | undefined;
