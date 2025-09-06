// setupUI.js
import * as Cesium from 'cesium';
import { FloodEngine } from './FloodEngine.js';

export function setupUI(viewer, floodEngine) {

    // 加载 Cesium OSM Buildings
    // async function addOsmBuildingsAsync(viewer) {
    //   try {
    //     const osmBuildings = await Cesium.createOsmBuildingsAsync();
    //     viewer.scene.primitives.add(osmBuildings);
    //     floodEngine.buildingTilesets.push(osmBuildings);
    //   } catch (error) {
    //     console.error('Failed to add OSM buildings:', error);
    //   }
    // }

    // addOsmBuildingsAsync(viewer);
    
    const waterLevelSlider = document.getElementById('waterLevel');
    const levelValue = document.getElementById('levelValue');
    waterLevelSlider.max=1000;
    
    waterLevelSlider.addEventListener('input', (e) => {
      const level = parseFloat(e.target.value);
      console.log('滑块当前值:', level);  // 这里打印滑块的值，方便调试
      levelValue.textContent = level;
      floodEngine.setWaterLevel(level);
    });
    
    document.getElementById('staticBtn').addEventListener('click', () => {
      const level = parseFloat(waterLevelSlider.value);
      floodEngine.setWaterLevel(level);
    });
    
    document.getElementById('dynamicBtn').addEventListener('click', () => {
      const center = viewer.camera.position;
      floodEngine.startDynamicSimulation(center);
    });
    
    document.getElementById('stopBtn').addEventListener('click', () => {
      floodEngine.stopDynamicSimulation();
    });
    
    document.getElementById('addBuilding').addEventListener('click', () => {
      const position = viewer.camera.position;
      floodEngine.addTestBuilding(position);
    });
    
    document.getElementById('addDrainage').addEventListener('click', () => {
      const position = viewer.camera.position;
      floodEngine.addDrainageOutlet(position);
    });
    

    document.getElementById('startRain').addEventListener('click', () => {
      const density = parseInt(document.getElementById('rainDensity').value);
      const size = parseInt(document.getElementById('rainSize').value);
      floodEngine.startRain(density, size);
    });
    
    document.getElementById('stopRain').addEventListener('click', () => {
      floodEngine.stopRain();
    });

    
    viewer.cesiumWidget.screenSpaceEventHandler.setInputAction((movement) => {
      const picked = viewer.scene.pick(movement.position);
      if (Cesium.defined(picked) && picked.id) {
        const name = picked.id.name || "未命名实体";
        viewer.selectedEntity = picked.id;
        viewer.infoBox.viewModel.description = name;
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
}