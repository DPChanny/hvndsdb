using System;
using System.IO;
using System.Reflection;
using System.Threading.Tasks;
using GaussianSplatting.Editor;
using GaussianSplatting.Runtime;
using Main;
using UnityEditor;
using UnityEngine;
using UnityEngine.Serialization;

namespace Visualizer
{
    public class Manager : MonoBehaviour
    {
        private const int Width = 960;
        private const int Height = 540;
        private const float MaxFPS = 30f;

        public string sessionId;

        [SerializeField] private Camera targetCamera;
        [FormerlySerializedAs("renderers")] [SerializeField]
        private GaussianSplatRenderer[] gsrs;

        private float _frameTimer;

        private RenderTexture _sharedRT;
        private Texture2D _readbackTex;

        private void Start()
        {
            _sharedRT = new RenderTexture(Width, Height, 24);
            _readbackTex = new Texture2D(Width, Height, TextureFormat.RGB24, false);
        }

        private async void Update()
        {
            if (string.IsNullOrWhiteSpace(sessionId)) return;
            
            _frameTimer += Time.deltaTime;
            if (_frameTimer >= 1f / MaxFPS)
            {
                _frameTimer = 0f;
                await SendFrame();
            }
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

            string assetPath = "Assets/GaussianAssets/" + sessionId;

            typeof(GaussianSplatAssetCreatorEditor).GetField("m_InputFile", BindingFlags.NonPublic | BindingFlags.Instance)
                ?.SetValue(editor, plyPath);
            typeof(GaussianSplatAssetCreatorEditor).GetField("m_OutputFolder", BindingFlags.NonPublic | BindingFlags.Instance)
                ?.SetValue(editor, assetPath);
            typeof(GaussianSplatAssetCreatorEditor).GetField("m_ImportCameras", BindingFlags.NonPublic | BindingFlags.Instance)
                ?.SetValue(editor, true);
            typeof(GaussianSplatAssetCreatorEditor).GetField("m_Quality", BindingFlags.NonPublic | BindingFlags.Instance)
                ?.SetValue(editor, 2);

            typeof(GaussianSplatAssetCreatorEditor).GetMethod("ApplyQualityLevel", BindingFlags.NonPublic | BindingFlags.Instance)
                ?.Invoke(editor, null);
            typeof(GaussianSplatAssetCreatorEditor).GetMethod("CreateAsset", BindingFlags.NonPublic | BindingFlags.Instance)
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
        }

        public void SetCameraPosition(Vector3 position)
        {
            targetCamera.transform.position = position;
        }

        public void SetCameraRotation(Quaternion rotation)
        {
            targetCamera.transform.rotation = rotation;
        }

        private async Task SendFrame()
        {
            // Render
            targetCamera.targetTexture = _sharedRT;
            targetCamera.Render();
            targetCamera.targetTexture = null;

            // Read pixels
            RenderTexture.active = _sharedRT;
            _readbackTex.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
            _readbackTex.Apply();
            RenderTexture.active = null;

            // Encode to base64
            byte[] jpgBytes = _readbackTex.EncodeToJPG();
            string base64 = Convert.ToBase64String(jpgBytes);

            // Send via WebSocket
            await Main.Manager.WebSocket.SendText(
                JsonUtility.ToJson(
                    new WebSocketBaseDto<FrameDto>(
                        "frame",
                        new FrameDto(sessionId, base64))));
        }

        private void OnDestroy()
        {
            if (_sharedRT != null)
            {
                _sharedRT.Release();
                Destroy(_sharedRT);
                _sharedRT = null;
            }

            if (_readbackTex != null)
            {
                Destroy(_readbackTex);
                _readbackTex = null;
            }
        }
    }
}
