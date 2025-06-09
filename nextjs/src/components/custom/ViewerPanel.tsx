"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/Button";

type SessionData = { session_id: string };
type FrameData = { frame: string; session_id: string };

type ClientMessage =
  | { type: "start_session_request"; data: SessionData }
  | { type: "end_session_request"; data: SessionData }
  | { type: "frame"; data: FrameData };

type ServerMessage =
  | { type: "start_session"; data: SessionData }
  | { type: "end_session"; data: SessionData }
  | { type: "frame"; data: FrameData }
  | { type: "frame_complete"; data: SessionData };

type ViewerPanelProps = {
  ws: WebSocket | null;
  isConnected: boolean;
  buildingId: string;
  onClose: () => void;
};

export function ViewerPanel({
  ws,
  isConnected,
  buildingId,
  onClose,
}: ViewerPanelProps) {
  const [mode, setMode] = useState<"video" | "realtime">("video");
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [frameImage, setFrameImage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const frameAckQueue = useRef<(() => void)[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const sendMessage = useCallback(
    (message: ClientMessage) => {
      if (ws?.readyState === WebSocket.OPEN) {
        console.log("[WebSocket] 보내는 메시지:", message);
        ws.send(JSON.stringify(message));
      } else {
        console.warn("[WebSocket] 연결 안 됨, 메시지 전송 실패");
      }
    },
    [ws]
  );

  useEffect(() => {
    if (!ws) return;

    const handleMessage = (event: MessageEvent<string>) => {
      try {
        const msg: ServerMessage = JSON.parse(event.data);
        console.log("[WebSocket] 수신:", msg);

        if (msg.data.session_id !== buildingId) return;

        switch (msg.type) {
          case "start_session":
            setIsSessionActive(true);
            setFrameImage(null);
            break;
          case "end_session":
            setIsSessionActive(false);
            stopStream();
            onClose();
            break;
          case "frame":
            setFrameImage(`data:image/jpeg;base64,${msg.data.frame}`);
            break;
          case "frame_complete":
            const resolver = frameAckQueue.current.shift();
            if (resolver) resolver();
            break;
        }
      } catch (err) {
        console.error("WebSocket 메시지 파싱 실패:", event.data, err);
      }
    };

    ws.addEventListener("message", handleMessage);
    sendMessage({
      type: "start_session_request",
      data: { session_id: buildingId },
    });

    return () => {
      ws.removeEventListener("message", handleMessage);
      stopStream();
    };
  }, [ws, buildingId, sendMessage, onClose]);

  const waitForFrameAck = (): Promise<void> =>
    new Promise((res) => frameAckQueue.current.push(res));

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !ws || ws.readyState !== WebSocket.OPEN || !isSessionActive)
      return;

    setIsUploading(true);
    const videoURL = URL.createObjectURL(file);
    const video = document.createElement("video");
    video.src = videoURL;
    video.crossOrigin = "anonymous";
    video.muted = true;

    await new Promise((res) =>
      video.addEventListener("loadedmetadata", () => res(null))
    );
    await video.play();

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const fps = 1;
    const interval = 1000 / fps;
    const duration = video.duration * 1000;
    const totalFrames = Math.floor(duration / interval);

    for (let i = 0; i < totalFrames; i++) {
      const time = i * interval;

      await new Promise<void>((res) => {
        const seekHandler = () => {
          requestAnimationFrame(async () => {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const base64 = canvas.toDataURL("image/jpeg").split(",")[1];
            ws.send(
              JSON.stringify({
                type: "frame",
                data: { session_id: buildingId, frame: base64 },
              })
            );
            await waitForFrameAck();
            res();
          });
        };
        video.addEventListener("seeked", seekHandler, { once: true });
        video.currentTime = time / 1000;
      });
    }

    video.pause();
    URL.revokeObjectURL(videoURL);
    setIsUploading(false);
  };

  const handleRealtimeStreaming = async () => {
    if (!isSessionActive || !ws || ws.readyState !== WebSocket.OPEN) return;

    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    streamRef.current = stream;

    const video = document.createElement("video");
    video.srcObject = stream;
    video.muted = true;
    await video.play();

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = 640;
    canvas.height = 480;

    const sendLoop = async () => {
      if (!isSessionActive || !streamRef.current) return;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const base64 = canvas.toDataURL("image/jpeg").split(",")[1];
      ws.send(
        JSON.stringify({
          type: "frame",
          data: { session_id: buildingId, frame: base64 },
        })
      );
      await waitForFrameAck();
      setTimeout(sendLoop, 1000); // 1fps
    };

    sendLoop();
  };

  useEffect(() => {
    if (mode === "realtime" && isSessionActive) {
      handleRealtimeStreaming();
    }
  }, [mode, isSessionActive]);

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <Button
          onClick={() => setMode("video")}
          variantIntent="secondary"
          disabled={isUploading || !isConnected || mode === "video"}
        >
          Video 모드
        </Button>
        <Button
          onClick={() => setMode("realtime")}
          variantIntent="secondary"
          disabled={isUploading || !isConnected || mode === "realtime"}
        >
          Real-time 모드
        </Button>
      </div>

      {mode === "video" && (
        <div className="flex justify-between items-center">
          <input
            type="file"
            accept="video/*"
            onChange={handleVideoUpload}
            disabled={!isSessionActive || isUploading}
          />
        </div>
      )}

      <Button
        onClick={() =>
          sendMessage({
            type: "end_session_request",
            data: { session_id: buildingId },
          })
        }
        disabled={!isConnected}
        variantIntent="destructive"
      >
        세션 종료
      </Button>

      {isUploading && <p className="text-sm text-blue-500">업로드 중...</p>}

      {isSessionActive ? (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold">Frame</h3>
          <div className="aspect-[16/9] bg-black flex items-center justify-center border rounded">
            {frameImage ? (
              <Image
                src={frameImage}
                alt="Frame"
                width={960}
                height={540}
                unoptimized
              />
            ) : (
              <span className="text-gray-400 text-sm">수신된 프레임 없음</span>
            )}
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-500">세션을 기다리는 중입니다...</p>
      )}
    </div>
  );
}
