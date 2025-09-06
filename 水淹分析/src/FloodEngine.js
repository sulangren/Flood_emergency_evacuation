// FloodEngine.js
import * as Cesium from "cesium";

export class FloodEngine {
  constructor(viewer) {
    this.viewer = viewer;
    this.waterEntities = [];
    this.isDynamicSimulating = false;
    this.currentWaterLevel = 0;
    this.waterMaterial = this.createWaterMaterial();
    this.buildingTilesets = [];
    this.controlPoints = [];
    this.waterSurface = undefined;
    this.rainParticleSystem = null;
  }

  createWaterMaterial() {
    return new Cesium.Material({
      fabric: {
        type: "Water",
        uniforms: {
          baseWaterColor: new Cesium.Color(0.2, 0.5, 0.8, 0.6),
          normalMap: "/textures/waterNormals.jpg",
          frequency: 200.0, // 降低频率
          animationSpeed: 0.08, // 禁用动画
          amplitude: 2.0,
        },
      },
    });
  }

  async setWaterLevel(height) {
    this.currentWaterLevel = height;

    if (this.waterSurface) {
      this.viewer.entities.remove(this.waterSurface);
      this.waterSurface = undefined;
    }

    this.waterSurface = this.viewer.entities.add({
      name: "水面",
      rectangle: {
        coordinates: Cesium.Rectangle.fromDegrees(113.4, 34.6, 113.8, 34.9),
        material: new Cesium.ImageMaterialProperty({
          image: "/textures/waterNormals.jpg",
          repeat: new Cesium.Cartesian2(10.0, 10.0),
          color: new Cesium.Color(0.2, 0.5, 0.8, 1),
        }),
        height: 80,
        extrudedHeight: 80 + height * 0.2,
        outline: false,
      },
    });

    this.updateBuildingsFloodState();
  }

  updateBuildingsFloodState() {
    const tilesets = [];
    const primitives = this.viewer.scene.primitives;

    for (let i = 0; i < primitives.length; i++) {
      const p = primitives.get(i);
      if (p instanceof Cesium.Cesium3DTileset) {
        tilesets.push(p);
      }
    }

    tilesets.forEach((tileset) => {
      tileset.style = new Cesium.Cesium3DTileStyle({
        color: {
          conditions: [
            [
              `\${Height} <= ${this.currentWaterLevel}`,
              "color(0.2, 0.5, 0.8, 0.5)",
            ],
            ["true", "color(1.0, 1.0, 1.0, 1.0)"],
          ],
        },
      });
    });
  }

  async startDynamicSimulation(startPosition, speed = 100) {
    if (this.isDynamicSimulating) return;
    this.isDynamicSimulating = true;

    const queue = [{ position: startPosition, level: 0 }];
    const floodedCells = new Set();

    while (this.isDynamicSimulating && queue.length > 0) {
      const current = queue.shift();
      const cellKey = this.getCellKey(current.position);

      if (floodedCells.has(cellKey)) continue;
      floodedCells.add(cellKey);

      const elevation = await this.getElevation(current.position);
      const waterHeight = current.level * 0.2;

      if (waterHeight >= elevation) {
        this.createWaterCell(current.position, waterHeight);

        for (let i = 0; i < 8; i++) {
          const neighborPos = this.getNeighborPosition(current.position, i);
          queue.push({
            position: neighborPos,
            level: current.level + 1,
          });
        }
      }

      await new Promise((resolve) => setTimeout(resolve, speed));
    }

    this.isDynamicSimulating = false;
  }

  stopDynamicSimulation() {
    this.isDynamicSimulating = false;
    this.clearWaterEffects();
  }

  getCellKey(position) {
    const carto = Cesium.Cartographic.fromCartesian(position);
    const latKey = Math.floor(carto.latitude * 10000);
    const lonKey = Math.floor(carto.longitude * 10000);
    return `${latKey}_${lonKey}`;
  }

  createWaterCell(position, height) {
    const entity = this.viewer.entities.add({
      position: position,
      polygon: {
        hierarchy: new Cesium.CircleGeometry({
          center: position,
          radius: 25,
        }),
        material: new Cesium.Color(0.2, 0.5, 0.8, 0.5),
        height: height,
        extrudedHeight: height + 0.5,
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });
    this.waterEntities.push(entity);
    return entity;
  }

  async getElevation(position) {
    try {
      const carto = Cesium.Cartographic.fromCartesian(position);
      const samples = await Cesium.sampleTerrainMostDetailed(
        this.viewer.terrainProvider,
        [carto]
      );
      return samples[0].height;
    } catch (error) {
      console.error("获取高程失败:", error);
      return 0;
    }
  }

  getNeighborPosition(position, direction) {
    const offsets = [
      [0.0001, 0],
      [0.0001, 0.0001],
      [0, 0.0001],
      [-0.0001, 0.0001],
      [-0.0001, 0],
      [-0.0001, -0.0001],
      [0, -0.0001],
      [0.0001, -0.0001],
    ];
    const carto = Cesium.Cartographic.fromCartesian(position);
    return Cesium.Cartesian3.fromRadians(
      carto.longitude + offsets[direction][0],
      carto.latitude + offsets[direction][1],
      carto.height
    );
  }

  clearWaterEffects() {
    this.waterEntities.forEach((entity) => this.viewer.entities.remove(entity));
    this.waterEntities = [];
    this.viewer.scene.globe.heightOffset = 0;
    this.viewer.scene.globe.material = undefined;
  }

  addTestBuilding(position, height = 20) {
    return this.viewer.entities.add({
      name: "测试建筑",
      position: position,
      box: {
        dimensions: new Cesium.Cartesian3(30, 30, height),
        material: Cesium.Color.GRAY.withAlpha(0.8),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });
  }

  addDrainageOutlet(position) {
    return this.viewer.entities.add({
      name: "排水口",
      position: position,
      cylinder: {
        length: 5,
        topRadius: 0,
        bottomRadius: 3,
        material: Cesium.Color.RED.withAlpha(0.7),
      },
    });
  }

  startRain(density = 50, size = 20, retryCount = 0) {
    const canvas = this.viewer.scene.canvas;

    if (canvas.clientWidth === 0 || canvas.clientHeight === 0) {
      console.warn(
        `🚫 [Rain] Canvas尺寸为0，等待渲染... 第${retryCount + 1}次`
      );
      if (retryCount < 5) {
        setTimeout(() => this.startRain(density, size, retryCount + 1), 500);
      }
      return;
    }

    const camPos = this.viewer.camera?.positionWC;
    if (!camPos) {
      console.warn("🚫 [Rain] 相机位置未准备好，稍后重试...");
      if (retryCount < 5) {
        setTimeout(() => this.startRain(density, size, retryCount + 1), 500);
      }
      return;
    }

    if (this.rainParticleSystem) {
      this.viewer.scene.primitives.remove(this.rainParticleSystem);
      this.rainParticleSystem = null;
    }

    const rainImage = "/textures/rain.png";
    const emitterBoxSize = 30.0;

    const emitterModelMatrix =
      Cesium.Transforms.eastNorthUpToFixedFrame(camPos);

    this.rainParticleSystem = new Cesium.ParticleSystem({
      image: rainImage,
      startColor: Cesium.Color.WHITE.withAlpha(0.2),
      endColor: Cesium.Color.WHITE.withAlpha(0.0),
      startScale: size / 100,
      endScale: size / 100,
      minimumSpeed: 20.0,
      maximumSpeed: 30.0,
      lifetime: 0.8,
      emissionRate: density,
      emitter: new Cesium.BoxEmitter(
        new Cesium.Cartesian3(emitterBoxSize, emitterBoxSize, 5.0)
      ),
      modelMatrix: Cesium.Matrix4.IDENTITY,
      emitterModelMatrix: emitterModelMatrix,
      updateCallback: function (particle, dt) {
        Cesium.Cartesian3.add(
          particle.position,
          new Cesium.Cartesian3(0, 0, -dt * 100.0),
          particle.position
        );
      },
    });

    this.viewer.scene.primitives.add(this.rainParticleSystem);

    const that = this;
    this.viewer.scene.postUpdate.addEventListener(() => {
      if (!that.rainParticleSystem || !that.viewer || !that.viewer.camera)
        return;
      const camPos = that.viewer.camera.positionWC;
      that.rainParticleSystem.emitterModelMatrix =
        Cesium.Transforms.eastNorthUpToFixedFrame(camPos);
    });
  }

  stopRain() {
    if (this.rainParticleSystem) {
      this.viewer.scene.primitives.remove(this.rainParticleSystem);
      this.rainParticleSystem = null;
    }
  }
}
