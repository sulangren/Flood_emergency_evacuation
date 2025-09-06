// main.js
import * as Cesium from 'cesium';
import { FloodEngine } from './FloodEngine.js';
import { setupUI } from './setupUI.js';

// ✅ 设置 Cesium ion 令牌
Cesium.Ion.defaultAccessToken =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5Y2MwZTU2Yy1lNjk4LTQ2OGYtYTgxOC0xN2ZkMjZlZTgxNWUiLCJpZCI6MzE0MzkxLCJpYXQiOjE3NTA1NjM1NTZ9.MnrkcPHzOb0xrcBz-pSU4cz7NaKvVBPVyt6-Tt0P_1M';

// ✅ 初始化 Viewer
const viewer = new Cesium.Viewer('cesiumContainer', {
  terrainProvider: Cesium.createWorldTerrain(),
  animation: false,
  timeline: false
});

// ✅ 启用贴地深度测试
viewer.scene.globe.depthTestAgainstTerrain = true;

// ✅ 初始相机位置（郑州）
viewer.camera.flyTo({
  destination: Cesium.Cartesian3.fromDegrees(113.6254, 34.7466, 3000),
  orientation: {
    pitch: Cesium.Math.toRadians(-40.0)
  }
});

// // ✅ 加载 Cesium OSM 模型（可选）
// const tileset = new Cesium.Cesium3DTileset({
//   url: Cesium.IonResource.fromAssetId(96188),
// });
// viewer.scene.primitives.add(tileset);


// ✅ 加载本地 GeoJSON 建筑文件（注意：需通过 HTTP 访问）

Cesium.GeoJsonDataSource.load('/郑州.geojson', {
  clampToGround: true
}).then((dataSource) => {
  viewer.dataSources.add(dataSource);


//   const entities = dataSource.entities.values;
// for (let i = 0; i < entities.length; i++) {
//   const entity = entities[i];
//   if (entity.polygon) {
//     entity.polygon.extrudedHeight = 100;  // 统一高度100米
//     entity.polygon.material = Cesium.Color.RED.withAlpha(0.6);
//     entity.polygon.outline = true;
//     entity.polygon.outlineColor = Cesium.Color.WHITE;
//   }
// }

const entities = dataSource.entities.values;
for (let i = 0; i < entities.length; i++) {
  const entity = entities[i];
  if (entity.polygon) {
    // 获取Floor属性值
    const floors = entity.properties?.Floor?.getValue();
    // 如果没拿到楼层，默认3层
    const floorCount = floors ? floors : 3;

    entity.polygon.extrudedHeight = floorCount * 20; // 楼层数 * 3米高度
    entity.polygon.material = Cesium.Color.GRAY.withAlpha(0.9);
    entity.polygon.outline = true;
    entity.polygon.outlineColor = Cesium.Color.GRAY;
  }
}



  // ✅ 鼠标点击建筑显示属性
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  handler.setInputAction((movement) => {
    const pickedObject = viewer.scene.pick(movement.position);
    if (Cesium.defined(pickedObject) && pickedObject.id) {
      const props = pickedObject.id.properties;
      const name = props.name || '未知建筑';
      const floors = props.楼层数 || '未知';
      alert(`🏢 建筑名称：${name}\n📏 楼层数：${floors}`);
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
});

// ✅ 初始化洪水模拟引擎
const floodEngine = new FloodEngine(viewer);

// ✅ 设置 UI 控件
setupUI(viewer, floodEngine);

// ✅ 跳转郑州中心按钮事件（需配合 HTML 按钮使用）
document.getElementById('gotoZhengzhou').addEventListener('click', () => {
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(113.686, 34.787, 2500),
    orientation: {
      pitch: Cesium.Math.toRadians(-35.0)
    }
  });
});
