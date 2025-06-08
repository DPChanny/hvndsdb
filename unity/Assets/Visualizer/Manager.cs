using System;
using System.IO;
using System.Reflection;
using System.Threading.Tasks;
using GaussianSplatting.Editor;
using GaussianSplatting.Runtime;
using Main;
using UnityEditor;
using UnityEngine;
using UnityEngine.PlayerLoop;
using UnityEngine.Serialization;

namespace Visualizer
{
    public class Manager : MonoBehaviour
    {
        private const int Width = 960;
        private const int Height = 540;

        public string sessionId;

        [SerializeField] private Camera targetCamera;

        [FormerlySerializedAs("renderers")] [SerializeField]
        private GaussianSplatRenderer[] gsrs;

        private const float MaxFPS = 5;
        private float _lastSendFrame;

        private void Update()
        {
            _lastSendFrame += Time.deltaTime;
        }

        public async Task SetPly(string plyUrl)
        {
            byte[] plyBytes = await HttpDownloader.DownloadBytes(plyUrl);

            string sessionDir = Path.Combine(Application.streamingAssetsPath, sessionId);
            if (!Directory.Exists(sessionDir))
                Directory.CreateDirectory(sessionDir);

            string plyPath = Path.Combine(sessionDir, "point_cloud.ply");
            await File.WriteAllBytesAsync(plyPath, plyBytes);

            var editor = ScriptableObject.CreateInstance<GaussianSplatAssetCreatorEditor>();

            var mInputFile =
                typeof(GaussianSplatAssetCreatorEditor).GetField("m_InputFile",
                    BindingFlags.NonPublic | BindingFlags.Instance);
            var mOutputFolder = typeof(GaussianSplatAssetCreatorEditor).GetField("m_OutputFolder",
                BindingFlags.NonPublic | BindingFlags.Instance);
            var mImportCameras = typeof(GaussianSplatAssetCreatorEditor).GetField("m_ImportCameras",
                BindingFlags.NonPublic | BindingFlags.Instance);
            var mQuality =
                typeof(GaussianSplatAssetCreatorEditor).GetField("m_Quality",
                    BindingFlags.NonPublic | BindingFlags.Instance);

            string assetPath = "Assets/GaussianAssets/" + sessionId;
            
            mInputFile?.SetValue(editor, plyPath);
            mOutputFolder?.SetValue(editor, assetPath);
            mImportCameras?.SetValue(editor, true);
            mQuality?.SetValue(editor, 2);

            typeof(GaussianSplatAssetCreatorEditor)
                .GetMethod("ApplyQualityLevel", BindingFlags.NonPublic | BindingFlags.Instance)
                ?.Invoke(editor, null);

            typeof(GaussianSplatAssetCreatorEditor)
                .GetMethod("CreateAsset", BindingFlags.NonPublic | BindingFlags.Instance)
                ?.Invoke(editor, null);

            AssetDatabase.Refresh();
            
            var guids = AssetDatabase.FindAssets("t:Object", new[] { assetPath });

            foreach (var guid in guids)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);

                if (!path.EndsWith(".asset")) continue;

                var asset = AssetDatabase.LoadAssetAtPath<GaussianSplatAsset>(path);
                foreach (var gsr in gsrs)
                    gsr.m_Asset = asset;

                break;
            }

            await Task.Yield();
            await SendFrame();
        }

        public async Task SetCameraPosition(Vector3 position)
        {
            targetCamera.transform.position = position;

            await SendFrame();
        }

        public async Task SetCameraRotation(Quaternion rotation)
        {
            targetCamera.transform.rotation = rotation;

            await SendFrame();
        }

        private async Task SendFrame()
        {
            if (_lastSendFrame < 1 / MaxFPS)
                return;
            
            _lastSendFrame = 0;
            
            var rt = new RenderTexture(Width, Height, 24);
            targetCamera.targetTexture = rt;
            targetCamera.Render();

            RenderTexture.active = rt;

            var tex = new Texture2D(Width, Height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
            tex.Apply();

            targetCamera.targetTexture = null;
            RenderTexture.active = null;
            Destroy(rt);

            var jpgBytes = tex.EncodeToJPG();
            Destroy(tex);

            var base64 = Convert.ToBase64String(jpgBytes);

            await Main.Manager.WebSocket.SendText(
                JsonUtility.ToJson(
                    new WebSocketBaseDto<FrameDto>(
                        "frame",
                        new FrameDto(
                            sessionId,
                            base64))));
        }
    }
}
