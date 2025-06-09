using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using NativeWebSocket;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Main
{
    public class Manager : MonoBehaviour
    {
        public static readonly Dictionary<string, Scene> SessionToScene = new();
        public static WebSocket WebSocket;

        private bool _isConnecting;
        private bool _shouldReconnect = true;
        private const float RetryDelay = 3f;

        private void Awake()
        {
            PlayerSettings.runInBackground = true;
        }

        private async Task HandleMessage(string message)
        {
            try
            {
                var json = JsonUtility.FromJson<WebSocketBase>(message);

                switch (json.type)
                {
                    case "start_session":
                        await Service.StartSessionService(JsonUtility.FromJson<WebSocketBaseDto<StartSessionDto>>(message).data);
                        break;
                    case "set_ply":
                        await Service.SetPlyService(JsonUtility.FromJson<WebSocketBaseDto<SetPlyDto>>(message).data);
                        break;
                    case "set_camera_position":
                        await Service.SetCameraPositionService(JsonUtility.FromJson<WebSocketBaseDto<SetCameraPositionDto>>(message).data);
                        break;
                    case "set_camera_rotation":
                        await Service.SetCameraRotationService(JsonUtility.FromJson<WebSocketBaseDto<SetCameraRotationDto>>(message).data);
                        break;
                    case "end_session":
                        await Service.EndSessionService(JsonUtility.FromJson<WebSocketBaseDto<EndSessionDto>>(message).data);
                        break;
                }
            }
            catch (Exception e)
            {
                Debug.LogError(e);
            }
        }

        private async Task ConnectWebSocket()
        {
            if (_isConnecting) return;

            _isConnecting = true;

            while (_shouldReconnect && (WebSocket == null || WebSocket.State != WebSocketState.Open))
            {
                try
                {
                    WebSocket = new WebSocket("ws://127.0.0.1:8000/ws/unity");

                    WebSocket.OnOpen += () =>
                    {
                        Debug.Log("[WebSocket] Connected");
                    };

                    WebSocket.OnError += (e) =>
                    {
                        Debug.LogError($"[WebSocket] Error: {e}");
                    };

                    WebSocket.OnClose += async (e) =>
                    {
                        Debug.LogWarning($"[WebSocket] Closed with code {e}");
                        await RetryConnection();
                    };

                    WebSocket.OnMessage += (bytes) =>
                    {
                        _ = HandleMessage(Encoding.UTF8.GetString(bytes));
                    };

                    await WebSocket.Connect();
                }
                catch (Exception e)
                {
                    Debug.LogError($"[WebSocket] Connect failed: {e.Message}");
                }

                if (WebSocket == null || WebSocket.State != WebSocketState.Open)
                {
                    Debug.Log("[WebSocket] Retry in a few seconds...");
                    await Task.Delay(TimeSpan.FromSeconds(RetryDelay));
                }
            }

            _isConnecting = false;
        }

        private async Task RetryConnection()
        {
            if (_shouldReconnect)
            {
                Debug.Log("[WebSocket] Attempting to reconnect...");
                await ConnectWebSocket();
            }
        }

        private async void Start()
        {
            await ConnectWebSocket();
        }

        private void Update()
        {
            WebSocket?.DispatchMessageQueue();
        }

        private async void OnApplicationQuit()
        {
            _shouldReconnect = false;

            if (WebSocket != null)
            {
                await WebSocket.Close();
            }
        }
    }
}
