using System.IO;
using System.Threading.Tasks;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Main
{
    public static class Service
    {
        public static void SetCameraPositionService(SetCameraPositionDto dto)
        {
            var scene = Manager.SessionToScene[dto.session_id];
            var roots = scene.GetRootGameObjects();

            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                manager.SetCameraPosition(new Vector3(dto.x, dto.y, dto.z));
                break;
            }
        }

        public static void SetCameraRotationService(SetCameraRotationDto dto)
        {
            var scene = Manager.SessionToScene[dto.session_id];
            var roots = scene.GetRootGameObjects();

            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                manager.SetCameraRotation(new Quaternion(dto.x, dto.y, dto.z, dto.w));
                break;
            }
        }

        public static async Task SetPlyService(SetPlyDto dto)
        {
            var scene = Manager.SessionToScene[dto.session_id];
            var roots = scene.GetRootGameObjects();

            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                await manager.SetPly(dto.ply_url);
                break;
            }
        }

        public static async Task StartSessionService(StartSessionDto dto)
        {
            var sceneID = SceneManager.sceneCount;
            var loadOp = SceneManager.LoadSceneAsync("Visualizer/Visualizer", LoadSceneMode.Additive);

            while (!loadOp!.isDone)
                await Task.Yield();

            var scene = SceneManager.GetSceneAt(sceneID);
            Manager.SessionToScene.Add(dto.session_id, scene);

            var roots = scene.GetRootGameObjects();
            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                manager.sessionId = dto.session_id;
                break;
            }

            await Manager.WebSocket.SendText(
                JsonUtility.ToJson(
                    new WebSocketBaseDto<SessionReadyDTO>(
                        "session_ready",
                        new SessionReadyDTO(dto.session_id))));
        }

        public static async Task EndSessionService(EndSessionDto dto)
        {
            var scene = Manager.SessionToScene[dto.session_id];
            var roots = scene.GetRootGameObjects();

            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                manager.sessionId = null;
                break;
            }
            
            var unloadOperation = SceneManager.UnloadSceneAsync(Manager.SessionToScene[dto.session_id]);
            if (unloadOperation != null)
                await unloadOperation;
            Manager.SessionToScene.Remove(dto.session_id);
            
            string gsPath = Path.Combine("Assets", "GaussianAssets", dto.session_id);
            string streamingPath = Path.Combine("Assets", "StreamingAssets", dto.session_id);

            if (Directory.Exists(gsPath))
                Directory.Delete(gsPath, true);

            if (Directory.Exists(streamingPath))
                Directory.Delete(streamingPath, true);
            
            AssetDatabase.Refresh();
        }
    }

}