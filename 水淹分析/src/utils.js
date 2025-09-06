
export function integrateGaode3DBuildings(viewer) {
    // 创建高德地图实例
    const map = new AMap.Map('temp-container', {
      viewMode: '3D',
      pitch: 60,
      zoom: 15,
      center: [113.6654, 34.757], // 郑州市中心
      mapStyle: 'amap://styles/normal'
    });
  
    // 加载高德 3D 建筑图层
    const threeDFloor = new AMap.ThreeDFloor({
      zIndex: 100
    });
    map.add(threeDFloor);
  
    // 将高德地图的 3D 建筑数据投影到 Cesium 场景中
    const gaodeBuildings = viewer.scene.primitives.add(
      new Cesium.CustomDataSource('Gaode3DBuildings')
    );
  
    // 将高德地图的建筑数据转换为 Cesium 可用的格式
    const buildings = threeDFloor.getBuildings();
    buildings.forEach(building => {
      const positions = building.positions;
      const height = building.height;
  
      const polygon = new Cesium.PolygonGeometry({
        polygonHierarchy: new Cesium.PolygonHierarchy(
          Cesium.Cartesian3.fromDegreesArrayHeights(positions)
        ),
        extrudedHeight: height
      });
  
      const appearance = new Cesium.PerInstanceColorAppearance({
        translucent: true,
        flat: false
      });
  
      const buildingPrimitive = new Cesium.Primitive({
        geometryInstances: new Cesium.GeometryInstance({
          geometry: polygon,
          attributes: {
            color: Cesium.ColorGeometryInstanceAttribute.fromColor(Cesium.Color.fromCssColorString(building.color).withAlpha(0.8))
          }
        }),
        appearance: appearance
      });
  
      gaodeBuildings.add(buildingPrimitive);
    });
  
    // 移除临时的高德地图容器
    document.getElementById('temp-container').remove();
  }